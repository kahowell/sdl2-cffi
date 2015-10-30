from setuptools import setup, find_packages
import os
import platform
import sys
import shutil

VERSION='0.1.6'

package_data = {}
if sys.platform.startswith('win'):  # windows
    devel_root = os.getenv('SDL2_DEVEL_PATH')
    if platform.architecture()[0] == '64bit':
        architecture = 'x64'
    else:
        architecture = 'x86'
    shutil.copyfile(os.sep.join([devel_root, 'lib', architecture, 'SDL2.dll']), 'SDL2.dll')
    package_data['sdl2'] = ['SDL2.dll']

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
    cffi_modules=['{}:ffi'.format(os.sep.join(['sdl2', '_cffi.py']))],
    install_requires=['cffi>=1.0.0']
)
