import pygame
import sys
import time

import OpenGL
#OpenGL.ERROR_CHECKING = False
#OpenGL.ERROR_LOGGING = False
from OpenGL import GL

import render_state
import text
import world
import world_render


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

  if 1:
    w = world.World(16, 16)
    w.map[5][5] = 1
    w.map[6][5] = 1
    w.map[7][5] = 1
    w.map[8][5] = 1
    w.map[6][6] = 1
    w.map[7][6] = 1
    w.map[8][6] = 1
    w.map[7][7] = 1
  else:
    w = world.World(3, 3)
    w.map[0][0] = 1
    w.map[1][1] = 1
    w.map[2][2] = 1

    # LLL WWW WWW
    # LLL WWW WWW
    # LLL WWW WWW
    # WWW WWW WWW
    # WWW WWW WWW
    # WWW WWW WWW

  wr = world_render.WorldRenderer(render, w)

  t = text.Text(render)
  GL.glEnable(GL.GL_BLEND)

  while True:
    clock.tick()
    GL.glClear(GL.GL_COLOR_BUFFER_BIT)
    t.DrawString(-1.6, -1.0, 0.05, (1, 1, 1, 1), str(clock))
    wr.Draw()
    pygame.display.flip()


if __name__ == '__main__':
  main()
