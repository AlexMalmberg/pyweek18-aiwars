import pygame
import sys
import time

import OpenGL
#OpenGL.ERROR_CHECKING = False
#OpenGL.ERROR_LOGGING = False
from OpenGL import GL

import game
import game_loop
import render_state
import text
import world


def main():
  pygame.init()

  fullscreen = False
  if fullscreen:
    flags = (pygame.OPENGL | pygame.DOUBLEBUF | pygame.HWSURFACE
             | pygame.FULLSCREEN)
    width, height = 0, 0
  else:
    flags = pygame.OPENGL | pygame.DOUBLEBUF | pygame.HWSURFACE
    width, height = 1024, 640

  pygame.display.set_caption('AI wars 2000 Deluxe Edition!')
  screen = pygame.display.set_mode((width, height), flags)

  render = render_state.Render(screen)

  clock = pygame.time.Clock()
  t = text.Text(render)

  w = world.LoadWorld('data/world0.map')

  gs = game.GameState(w)

  gl = game_loop.GameLoop(render, t, gs)
  gl.Play()


if __name__ == '__main__':
  main()
