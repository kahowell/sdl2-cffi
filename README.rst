sdl2-cffi
=========
|appveyor| |travis|

sdl2-cffi is a python cffi wrapper for SDL2.

Requirements
------------
Windows wheels are published via C-I builds, so you should be able to install
sdl2-cffi on Windows without needing build dependencies.

Building sdl2-cffi requires:

- SDL2 development package
    - On Windows, the ``SDL2_DEVEL_PATH`` environment variable needs to be set
      to the location the SDL2 SDK is installed.
    - On other platforms, ``sdl2-config`` is expected to work. This might mean
      other platforms don't work yet. (Pull request welcome).
- GCC (for C preprocessing)
    - On Windows, MinGW needs to be installed, and ``MINGW_PATH`` should be
      set if MinGW is installed to a location outside of ``C:\MinGW``.
- pycparser

Why
---
- In contrast to https://pypi.python.org/pypi/PySDL2, sdl2-cffi uses CFFI
  instead of ctypes.
- In contrast to https://pypi.python.org/pypi/pysdl2-cffi, sdl2-cffi is
  licensed under zlib instead of GPLv2.
- I wanted to experiment with CFFI. :-)

Licenses
--------
- sdl2-cffi is licensed under the zlib license (same as SDL2).
- sdl2-cffi contains a copy of the OpenGL spec (which is licensed under the
  SGI Free Software License B) [see ``sdl2/gl.xml`` for more info].

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/kahowell/sdl2-cffi?svg=true
    :target: https://ci.appveyor.com/project/kahowell/sdl2-cffi

.. |travis| image:: https://travis-ci.org/kahowell/sdl2-cffi.svg
    :target: https://travis-ci.org/kahowell/sdl2-cffi
