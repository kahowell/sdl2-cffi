from _sdl2 import lib, ffi

for __name in dir(lib):
    globals()[__name] = getattr(lib, __name)
