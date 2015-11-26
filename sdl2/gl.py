from .gl_api import apis
from sdl2._gl import ffi
from sdl2._gl import lib
from sdl2.sdl2 import SDL_GL_GetProcAddress


class GL:
    def __init__(self, version, api='gl', profile='compatibility'):
        for function in apis[api][version][profile]['functions']:
            name_c_str = ffi.new('char[]', function.encode('utf8'))
            proc = SDL_GL_GetProcAddress(name_c_str)
            if proc != ffi.NULL:
                signature = ffi.typeof(getattr(lib, function))
                casted = ffi.cast(signature, proc)
                setattr(self, function, casted)
            else:
                print('Warning: unable to load {}'.format(function))
        for enum in apis[api][version][profile]['enums']:
            setattr(self, enum, getattr(lib, enum))
