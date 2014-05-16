import ctypes
import pygame
import sys
from OpenGL import GL


F = ctypes.sizeof(ctypes.c_float)
FP = lambda x: ctypes.cast(x * F, ctypes.POINTER(ctypes.c_float))


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

  def ScreenToViewport(self, x, y):
    x = x * 3.2 / self.width - 1.6
    y = 1.0 - y * 2.0 / self.height
    return x, y

  def LoadTextureArray(self, files):
    t = GL.glGenTextures(1)
    GL.glBindTexture(GL.GL_TEXTURE_2D_ARRAY, t)
    surfs = [pygame.image.load(f) for f in files]
    width = surfs[0].get_width()
    height = surfs[0].get_height()

    GL.glTexParameteri(GL.GL_TEXTURE_2D_ARRAY, GL.GL_TEXTURE_MIN_FILTER,
                       GL.GL_LINEAR_MIPMAP_LINEAR)
    GL.glTexParameteri(GL.GL_TEXTURE_2D_ARRAY, GL.GL_TEXTURE_MAG_FILTER,
                       GL.GL_LINEAR)
    GL.glTexParameter(GL.GL_TEXTURE_2D_ARRAY, GL.GL_GENERATE_MIPMAP, GL.GL_TRUE)
    GL.glTexParameter(GL.GL_TEXTURE_2D_ARRAY, GL.GL_TEXTURE_WRAP_S,
                      GL.GL_CLAMP_TO_EDGE)
    GL.glTexParameter(GL.GL_TEXTURE_2D_ARRAY, GL.GL_TEXTURE_WRAP_T,
                      GL.GL_CLAMP_TO_EDGE)

    GL.glTexImage3D(GL.GL_TEXTURE_2D_ARRAY, 0, GL.GL_RGBA8,
                    width, height, len(files), 0,
                    GL.GL_RGBA, GL.GL_UNSIGNED_BYTE,
                    None)

    for i, s in enumerate(surfs):
      GL.glTexSubImage3D(GL.GL_TEXTURE_2D_ARRAY, 0,
                         0, 0, i, width, height, 1,
                         GL.GL_RGBA, GL.GL_UNSIGNED_BYTE,
                         pygame.image.tostring(s, 'RGBA', 1))

    return t

  def BuildShader(self, vertex_shader_src, fragment_shader_src):
    program = GL.glCreateProgram()

    for kind, src in ((GL.GL_VERTEX_SHADER, vertex_shader_src),
                      (GL.GL_FRAGMENT_SHADER, fragment_shader_src)):
      if not src:
        continue
      shader = GL.glCreateShader(kind)
      GL.glShaderSource(shader, [src])
      GL.glCompileShader(shader)
      result = GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS)
      if not result:
        print ('shader compilation failed: %s'
               % GL.glGetShaderInfoLog(shader))
        sys.exit(1)
      GL.glAttachShader(program, shader)
      GL.glDeleteShader(shader)
    GL.glLinkProgram(program)
    return program
