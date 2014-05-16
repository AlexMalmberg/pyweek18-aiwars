import collections
import os
import pygame
import sys
from OpenGL.GL import *


class TextureHolder(object):
  def __init__(self, width, height, texture):
    self.width = width
    self.height = height
    self.texture = texture

  def __del__(self):
    t = getattr(self, 'texture')
    if t is not None:
      glDeleteTextures(self.texture)
      self.texture = None


class Text(object):
  def __init__(self, render):
    self.render = render
    base_dir = sys.path[0]
    self.font_path = os.path.join(base_dir, 'freesansbold.otf')
    self._font_cache = {}
    self._texture_cache = collections.OrderedDict()
    self._lru_size = 256

  def _GetFont(self, size):
    if not size in self._font_cache:
      self._font_cache[size] = pygame.font.Font(self.font_path, size)
    return self._font_cache[size]

  def _GetTexture(self, size, msg):
    key = (size, msg)
    if not key in self._texture_cache:
      font = self._GetFont(size)
      surf = font.render(msg, True, (255, 255, 255))
      w, h = surf.get_width(), surf.get_height()

      t = glGenTextures(1)
      glBindTexture(GL_TEXTURE_2D, t)
      glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
      glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
      glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
      glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
      glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h,
                   0, GL_RGBA,
                   GL_UNSIGNED_BYTE, surf.get_buffer().raw)
      if len(self._texture_cache) == self._lru_size:
        self._texture_cache.popitem(last=False)
      self._texture_cache[key] = TextureHolder(w, h, t)
    else:
      # Yucky way of resetting the order of this item so the LRU part
      # works.
      t = self._texture_cache[key]
      del self._texture_cache[key]
      self._texture_cache[key] = t

    return self._texture_cache[key]

  def DrawString(self, x, y, size, color, msg):
    msg = str(msg)
    font_size = self.render.ScreenToPixels(size)
    t = self._GetTexture(font_size, msg)
    w = self.render.PixelsToScreen(t.width)
    h = self.render.PixelsToScreen(t.height)
    glColor(*color)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glBindTexture(GL_TEXTURE_2D, t.texture)
    glEnable(GL_TEXTURE_2D)
    glBegin(GL_QUADS)
    glTexCoord(0, 1)
    glVertex(x, y)
    glTexCoord(1, 1)
    glVertex(x + w, y)
    glTexCoord(1, 0)
    glVertex(x + w, y + h)
    glTexCoord(0, 0)
    glVertex(x, y + h)
    glEnd()
    glDisable(GL_TEXTURE_2D)
