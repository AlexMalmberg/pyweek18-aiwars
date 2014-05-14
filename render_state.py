import pygame
from OpenGL import GL


def _MakeWidescreen(width, height):
  if width > int(1.6 * height):
    width = int(1.6 * height)
  else:
    height = int(width / 1.6)
  return width, height


class Render(object):
  def __init__(self, screen):
    screen_width, screen_height = screen.get_width(), screen.get_height()
    width, height = _MakeWidescreen(screen_width, screen_height)

    self.width = width
    self.height = height

    ofs_x = (screen_width - width) / 2
    ofs_y = (screen_height - height) / 2
    GL.glViewport(ofs_x, ofs_y, width, height)
    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glOrtho(-1.6, 1.6, -1.0, 1.0, -1.0, 1.0)
    GL.glMatrixMode(GL.GL_MODELVIEW)

    # Do an initial clear since we may stall for a bit loading stuff.
    GL.glClearColor(0, 0, 0, 0)
    GL.glClear(GL.GL_COLOR_BUFFER_BIT)
    pygame.display.flip()

  def ScreenToPixels(self, screen):
    pixels = screen / 2.0 * self.height
    return int(pixels)

  def PixelsToScreen(self, pixels):
    return pixels / float(self.height) * 2.0
