from setuptools import setup, find_packages
import os

setup(
    name='sdl2-cffi',
    packages=['sdl2'],
    version='0.1.2',
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
