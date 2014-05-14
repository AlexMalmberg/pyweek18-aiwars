import pygame
import sys
import time

import OpenGL
#OpenGL.ERROR_CHECKING = False
#OpenGL.ERROR_LOGGING = False
from OpenGL import GL

import render_state
import text


def main():
  pygame.init()
  flags = pygame.OPENGL | pygame.DOUBLEBUF | pygame.HWSURFACE
  width, height = 1024, 640

  pygame.display.set_caption('AI wars 2000 Deluxe Edition!')
  screen = pygame.display.set_mode((width, height), flags)

  render = render_state.Render(screen)

  clock = pygame.time.Clock()

  t = text.Text(render)
  GL.glEnable(GL.GL_BLEND)

  while True:
    clock.tick()
    GL.glClear(GL.GL_COLOR_BUFFER_BIT)
    t.DrawString(-1.6, -1.0, 0.05, (1, 1, 1, 1), str(clock))
    pygame.display.flip()


if __name__ == '__main__':
  main()
