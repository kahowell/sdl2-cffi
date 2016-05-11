from cffi import FFI
from subprocess import check_output
import re
import os
import pycparser
import json
import itertools
import platform
import sys
from pycparser import c_ast
from pycparser.c_generator import CGenerator

INCLUDE_PATTERN = re.compile(r'(-I)?(.*SDL2)')
DEFINE_PATTERN = re.compile(r'^#define\s+(\w+)\s+\(?([\w<|.]+)\)?', re.M)
DEFINE_BLACKLIST = {
    'SDL_ANDROID_EXTERNAL_STORAGE_READ',
    'SDL_ANDROID_EXTERNAL_STORAGE_WRITE',
    'M_PI',
    'main',
    'SDL_main',
    'SDL_AUDIOCVT_PACKED',
    'IMG_GetError',
    'IMG_SetError',
    'Mix_GetError',
    'Mix_SetError',
    'TTF_GetError',
    'TTF_SetError',
    'SDL_malloc',
    'SDL_calloc',
    'SDL_realloc',
    'SDL_free',
    'SDL_memset',
    'SDL_memcpy',
    'SDL_memmove',
    'SDL_memcmp',
    'SDL_strlen',
    'SDL_strlcpy',
    'SDL_strlcat',
    'SDL_strdup',
    'SDL_strchr',
    'SDL_strrchr',
    'SDL_strstr',
    'SDL_strcmp',
    'SDL_strncmp',
    'SDL_strcasecmp',
    'SDL_strncasecmp',
    'SDL_sscanf',
    'SDL_vsscanf',
    'SDL_snprintf',
    'SDL_vsnprintf',
    'SDL_PRINTF_FORMAT_STRING',
    'SDL_PRIX64',
    'SDL_PRIs64',
    'SDL_PRIu64',
    'SDL_PRIx64',
    'SDL_SCANF_FORMAT_STRING'
}

# define GCC specific compiler extensions away
DEFINE_ARGS = [
    '-D__attribute__(x)=',
    '-D__inline=',
    '-D__restrict=',
    '-D__extension__=',
    '-D__GNUC_VA_LIST=',
    '-D__gnuc_va_list=void*',
    '-D__inline__=',
    '-D__forceinline=',
    '-D__volatile__=',
    '-D__MINGW_NOTHROW=',
    '-D__nothrow__=',
    '-DCRTIMP=',
    '-DSDL_FORCE_INLINE=',
    '-DDOXYGEN_SHOULD_IGNORE_THIS=',
    '-D_PROCESS_H_=',
    '-U__GNUC__',
    '-Ui386',
    '-U__i386__',
    '-U__MINGW32__'
]

FUNCTION_BLACKLIST = {
    'SDL_main'
}

VARIADIC_ARG_PATTERN = re.compile(r'va_list \w+')
ARRAY_SIZEOF_PATTERN = re.compile(r'\[[^\]]*sizeof[^\]]*]')

HEADERS = [
    'SDL_main.h',
    'SDL_stdinc.h',
    'SDL_atomic.h',
    'SDL_audio.h',
    'SDL_clipboard.h',
    'SDL_cpuinfo.h',
    'SDL_endian.h',
    'SDL_error.h',
    'SDL_scancode.h',
    'SDL_keycode.h',
    'SDL_keyboard.h',
    'SDL_joystick.h',
    'SDL_touch.h',
    'SDL_gesture.h',
    'SDL_events.h',
    'SDL_filesystem.h',
    'SDL_gamecontroller.h',
    'SDL_haptic.h',
    'SDL_hints.h',
    'SDL_loadso.h',
    'SDL_log.h',
    'SDL_messagebox.h',
    'SDL_mutex.h',
    'SDL_power.h',
    'SDL_render.h',
    'SDL_rwops.h',
    'SDL_system.h',
    'SDL_thread.h',
    'SDL_timer.h',
    'SDL_version.h',
    'SDL_video.h',
    'SDL.h',
    'SDL_image.h',
    'SDL_mixer.h',
    'SDL_ttf.h',
]

ROOT_HEADERS = [
    'SDL.h', 
    'SDL_image.h',
    'SDL_mixer.h',
    'SDL_ttf.h',
]

EXTRA_LIBS = [
    'SDL2_image',
    'SDL2_mixer',
    'SDL2_ttf',
]

class Collector(c_ast.NodeVisitor):

    def __init__(self):
        self.generator = CGenerator()
        self.typedecls = []
        self.functions = []

    def process_typedecl(self, node):
        coord = os.path.abspath(node.coord.file)
        if node.coord is None or coord.find(include_dir) != -1:
            typedecl = '{};'.format(self.generator.visit(node))
            typedecl = ARRAY_SIZEOF_PATTERN.sub('[...]', typedecl)
            if typedecl not in self.typedecls:
                self.typedecls.append(typedecl)

    def sanitize_enum(self, enum):
        for name, enumeratorlist in enum.children():
            for name, enumerator in enumeratorlist.children():
                enumerator.value = c_ast.Constant('dummy', '...')
        return enum

    def visit_Typedef(self, node):
        coord = os.path.abspath(node.coord.file)
        if node.coord is None or coord.find(include_dir) != -1:
            if ((isinstance(node.type, c_ast.TypeDecl) and
                 isinstance(node.type.type, c_ast.Enum))):
                self.sanitize_enum(node.type.type)
            self.process_typedecl(node)

    def visit_Union(self, node):
        self.process_typedecl(node)

    def visit_Struct(self, node):
        self.process_typedecl(node)

    def visit_Enum(self, node):
        coord = os.path.abspath(node.coord.file)
        if node.coord is None or coord.find(include_dir) != -1:
            node = self.sanitize_enum(node)
            self.process_typedecl(node)

    def visit_FuncDecl(self, node):
        coord = os.path.abspath(node.coord.file)
        if node.coord is None or coord.find(include_dir) != -1:
            if isinstance(node.type, c_ast.PtrDecl):
                function_name = node.type.type.declname
            else:
                function_name = node.type.declname
            if function_name in FUNCTION_BLACKLIST:
                return
            decl = '{};'.format(self.generator.visit(node))
            decl = VARIADIC_ARG_PATTERN.sub('...', decl)
            if decl not in self.functions:
                self.functions.append(decl)


ffi = FFI()
if sys.platform.startswith('linux'):
    cflags = check_output(['sdl2-config', '--cflags']).decode('utf-8').strip()
    cflags_libs = check_output(['sdl2-config', '--libs']
                            ).decode('utf-8').strip() + ' -l' + ' -l'.join(EXTRA_LIBS)
    include_dir = INCLUDE_PATTERN.search(cflags).group(2)
    include_dirs = []
    libraries = []
    library_dirs = []
else:  # FIXME assumes windows otherwise
    cflags = ''
    cflags_libs = ''
    devel_root = os.getenv('SDL2_DEVEL_PATH')
    include_dir = os.path.abspath(os.sep.join([devel_root, 'include']))
    include_dirs = [include_dir]
    libraries = ['SDL2'] + EXTRA_LIBS
    if platform.architecture()[0] == '64bit':
        architecture = 'x64'
    else:
        architecture = 'x86'
    library_dirs = [os.sep.join([devel_root, 'lib', architecture])]

ffi.set_source(
    'sdl2._sdl2',
    ('\n').join('#include "%s"' % header for header in ROOT_HEADERS),
    include_dirs=include_dirs,
    libraries=libraries,
    library_dirs=library_dirs,
    extra_compile_args=cflags.split(),
    extra_link_args=cflags_libs.split()
)

pycparser_args = {
    'use_cpp': True,
    'cpp_args': DEFINE_ARGS
}
if sys.platform.startswith('win'):  #windows
    mingw_path = os.getenv('MINGW_PATH', default='C:\\MinGW')
    pycparser_args['cpp_path'] = '{}\\bin\\cpp.exe'.format(mingw_path)

collector = Collector()
for header in ROOT_HEADERS:
    ast = pycparser.parse_file(os.sep.join([include_dir, header]), **pycparser_args)
    collector.visit(ast)

defines = set()
for header_path in HEADERS:
    with open(os.sep.join([include_dir, header_path]), 'r') as header_file:
        header = header_file.read()
        for match in DEFINE_PATTERN.finditer(header):
            if match.group(1) in DEFINE_BLACKLIST or match.group(1) in collector.typedecls or match.group(1) in collector.functions:
                continue
            try:
                int(match.group(2), 0)
                defines.add('#define {} {}'.format(match.group(1),
                                                   match.group(2)))
            except:
                defines.add('#define {} ...'.format(match.group(1)))

print('Processing {} defines, {} types, {} functions'.format(
    len(defines),
    len(collector.typedecls),
    len(collector.functions)
))

ffi.cdef('\n'.join(itertools.chain(*[
    defines,
    collector.typedecls,
    collector.functions
])))
