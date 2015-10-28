from setuptools import setup, find_packages

setup(
    name='sdl2-cffi',
    packages=['sdl2'],
    version='0.1.0',
    description='CFFI wrapper for SDL2',
    author='Kevin Howell',
    author_email='kevin@kahowell.net',
    url='https://github.com/kahowell/sdl2-cffi',
    keywords=['sdl2', 'cffi'],
    classifiers=[
        'License :: OSI Approved :: zlib/libpng License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    setup_requires=['cffi>=1.0.0'],
    cffi_modules=['bindings/sdl2.py:ffi'],
    install_requires=['cffi>=1.0.0']
)
