sdl2-cffi
=========
sdl2-cffi is a python cffi wrapper for SDL2.

Requirements
------------
sdl2-cffi requires:

- SDL2 development package (expects ``sdl2-config`` to work)
- pycparser (to compile)

Why
---
- In contrast to https://pypi.python.org/pypi/PySDL2, sdl2-cffi uses CFFI
  instead of ctypes.
- In contrast to https://pypi.python.org/pypi/pysdl2-cffi, sdl2-cffi is
  licensed under zlib instead of GPLv2.
- I wanted to experiment with CFFI. :-)

License
-------
sdl2-cffi is licensed under the zlib license (same as SDL2).
