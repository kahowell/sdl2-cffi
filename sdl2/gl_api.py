from pkg_resources import resource_stream
from cffi import FFI
from collections import OrderedDict
import xml.etree.ElementTree as ElementTree
import re
import sys

TYPEDEF_PATTERN = re.compile(r'typedef.* \*?([\w]+);')

with resource_stream('sdl2', 'gl.xml') as gl_xml:
    api = ElementTree.parse(gl_xml)
    types = api.find('types')
    typedefs = OrderedDict()
    raw_typedefs = []
    for type in types.iterfind('type'):
        # ignore gles for windows
        type_name = type.get('name')
        type_requires = type.get('requires')
        if sys.platform.startswith('win'):
            if type_name == 'khrplatform' or type_requires == 'khrplatform':
                continue

        type_api = type.get('api')
        if not type_api:
            type_text = ''.join(type.itertext())
            raw_typedefs.append(type_text)
            matches = [match for match in TYPEDEF_PATTERN.finditer(type_text)]
            for match in TYPEDEF_PATTERN.finditer(type_text):
                name = match.group(1)
                if name in typedefs:
                    typedefs[name] = 'typedef int... {};'.format(name)
                else:
                    typedefs[name] = match.group(0)
            if type.find('apientry') is not None:  # function pointers
                name = type.find('name').text
                typedefs[name] = type_text

    apis = {}
    for feature in api.iterfind('feature'):
        module_name = '_'.join([feature.get('api'), feature.get('number')])
        module_name = module_name.replace('.', '_')
        description = {}
        description['enums'] = set()
        description['functions'] = set()
        api_name = feature.get('api')
        api_number = float(feature.get('number'))
        for require in feature.iterfind('require'):
            for enum in require.iterfind('enum'):
                description['enums'].add(enum.get('name'))
            for command in require.iterfind('command'):
                description['functions'].add(command.get('name'))
        # create core api
        core = {}
        latest_api = None
        if api_name in apis:
            latest_api = apis[api_name][max(apis[api_name])]
        if latest_api is not None and (
                'core' in latest_api or feature.find('remove')):
            core['enums'] = set(description['enums'])
            core['functions'] = set(description['functions'])
            if 'core' in latest_api:
                previous_version = latest_api['core']
            else:
                previous_version = latest_api['compatibility']
            previous_enums = previous_version['enums']
            previous_funcs = previous_version['functions']
            core['enums'] = previous_enums.union(description['enums'])
            core['functions'] = previous_funcs.union(description['functions'])
        if feature.find('remove'):
            for remove in feature.iterfind('remove'):
                for function in remove.iterfind('command'):
                    core['functions'].remove(function.get('name'))
                for enum in remove.iterfind('enum'):
                    core['enums'].remove(enum.get('name'))
        if api_name not in apis:
            apis[api_name] = {}
        else:
            previous_version = latest_api['compatibility']
            description['enums'].update(previous_version['enums'])
            description['functions'].update(previous_version['functions'])
        apis[api_name][api_number] = {'compatibility': description}
        if core:
            apis[api_name][api_number]['core'] = core

    function_defs = {}
    for function in api.find('commands').iterfind('command'):
        function_name = function.find('proto').find('name').text
        proto_text = [text for text in function.find('proto').itertext()]
        return_type = ''.join(proto_text[:-1])
        params = function.iterfind('param')
        args = ','.join([''.join(param.itertext()) for param in params])
        function_pointer = '{} (*{})({});'.format(
            return_type,
            function_name,
            args
        )
        function_defs[function_name] = function_pointer

    enums = {}
    for enum_group in api.iterfind('enums'):
        for enum in enum_group.iterfind('enum'):
            enums[enum.get('name')] = enum.get('value')
    enum_defs = ['#define {} {}'.format(*define) for define in enums.items()]


def build_ffi():
    ffi = FFI()
    source = []
    source.extend(raw_typedefs)
    source.extend(function_defs.values())
    source.extend(enum_defs)
    ffi.set_source('sdl2._gl', '\n'.join(source))
    ffi.cdef('\n'.join(typedefs.values()))
    ffi.cdef('\n'.join(function_defs.values()))
    ffi.cdef('\n'.join(enum_defs))
    return ffi
