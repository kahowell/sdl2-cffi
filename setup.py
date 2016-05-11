from setuptools import setup, find_packages
import glob
import os
import platform
import sys
import shutil

VERSION = '1.0.5'

package_data = {'': ['*.xml']}
if sys.platform.startswith('win'):  # windows
    devel_roots = os.getenv('SDL2_DEVEL_PATH').split(';')
    if platform.architecture()[0] == '64bit':
        architecture = 'x64'
    else:
        architecture = 'x86'
    for devel_root in devel_roots:
        dll_sources = glob.glob(os.sep.join([devel_root, 'lib', architecture, '*.dll']))
        dll_dest = 'sdl2'
        for dll_source in dll_sources:
            print('Copying {} to {}'.format(dll_source, dll_dest))
            shutil.copy(dll_source, dll_dest)
    package_data['sdl2'] = ['*.dll']

setup(
    name='sdl2-cffi',
    packages=['sdl2'],
    package_data=package_data,
    version=VERSION,
    description='CFFI wrapper for SDL2',
    author='Kevin Howell',
    author_email='kevin@kahowell.net',
    url='https://github.com/kahowell/sdl2-cffi',
    keywords=['sdl2', 'cffi'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: zlib/libpng License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    setup_requires=['cffi>=1.0.0', 'pycparser>=2.14'],
    cffi_modules=[
        '{}:ffi'.format(os.sep.join(['sdl2', '_cffi.py'])),
        '{}:build_ffi'.format(os.sep.join(['sdl2', 'gl_api.py']))
    ],
    install_requires=['cffi>=1.0.0']
)
