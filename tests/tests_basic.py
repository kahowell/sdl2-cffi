
from sdl2 import sdl2, gl

def test_basic():
    sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
    sdl2.SDL_Quit()
