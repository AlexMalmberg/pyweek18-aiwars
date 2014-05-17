import ctypes
import pygame
import sys
from OpenGL.GL import *

import game


F = ctypes.sizeof(ctypes.c_float)
FP = lambda x: ctypes.cast(x * F, ctypes.POINTER(ctypes.c_float))


Black = (0, 0, 0, 1)
BoxBackground = (1.0, 0.9, 0.8, 1.0)
GreenWireframe = (0, 0.4, 0, 1)


def _MakeWidescreen(width, height):
  if width > int(1.6 * height):
    width = int(1.6 * height)
  else:
    height = int(width / 1.6)
  return width, height


class Render(object):
  def LoadStuff(self):
    # Tile texture arrays.
    files = []
    self.z_land = len(files)
    files.append('tile_land')
    self.z_water = len(files)
    files.append('tile_water')

    self.z_line = len(files)
    self.z_line_num = 32
    for i in xrange(self.z_line_num):
      files.append('line%02i' % i)
    self.z_ic = len(files)
    self.z_ic_num = 16
    for i in xrange(self.z_ic_num):
      files.append('ic%02i' % i)
    self.z_oc = len(files)
    self.z_oc_num = 16
    for i in xrange(self.z_oc_num):
      files.append('oc%02i' % i)

    self.tile_col_textures = self.LoadTextureArray(
      ['data/tiles/%s_col.png' % f for f in files])
    self.tile_line_textures = self.LoadTextureArray(
      ['data/tiles/%s_line.png' % f for f in files])

    # Icons.
    files = list(game.Research.IconNames)
    self.tech_icon = list(range(game.Research.Num))
    self.icon_col_textures = self.LoadTextureArray(
      ['data/icon_%s_col.png' % f for f in files])
    self.icon_line_textures = self.LoadTextureArray(
      ['data/icon_%s_line.png' % f for f in files])

    # Shaders.
    self.tile_shader = self.BuildShader('tile shader', """
#version 120

void main() {
  gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
  gl_TexCoord[0].xyz = gl_MultiTexCoord0.xyz;
}

""", """
#version 130

uniform sampler2DArray texture_atlas;

void main(){
  gl_FragColor = texture(texture_atlas, gl_TexCoord[0].xyz);
}
""")

  def __init__(self, screen):
    screen_width, screen_height = screen.get_width(), screen.get_height()
    width, height = _MakeWidescreen(screen_width, screen_height)

    self.width = width
    self.height = height

    ofs_x = (screen_width - width) / 2
    ofs_y = (screen_height - height) / 2.
    glViewport(int(ofs_x), int(ofs_y), width, height)
    glMatrixMode(GL_PROJECTION)
    glOrtho(-1.6, 1.6, -1.0, 1.0, -1.0, 1.0)
    glMatrixMode(GL_MODELVIEW)

    # Do an initial clear since we may stall for a bit loading stuff.
    glClearColor(0, 0, 0, 0)
    glClear(GL_COLOR_BUFFER_BIT)
    pygame.display.flip()

    self.LoadStuff()

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
    t = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D_ARRAY, t)
    surfs = [pygame.image.load(f) for f in files]
    width = surfs[0].get_width()
    height = surfs[0].get_height()

    glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MIN_FILTER,
                    GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MAG_FILTER,
                    GL_LINEAR)
    glTexParameter(GL_TEXTURE_2D_ARRAY, GL_GENERATE_MIPMAP, GL_TRUE)
    glTexParameter(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_S,
                   GL_CLAMP_TO_EDGE)
    glTexParameter(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_T,
                   GL_CLAMP_TO_EDGE)

    glTexImage3D(GL_TEXTURE_2D_ARRAY, 0, GL_RGBA8,
                 width, height, len(files), 0,
                 GL_RGBA, GL_UNSIGNED_BYTE,
                 None)

    for i, s in enumerate(surfs):
      glTexSubImage3D(GL_TEXTURE_2D_ARRAY, 0,
                      0, 0, i, width, height, 1,
                      GL_RGBA, GL_UNSIGNED_BYTE,
                      pygame.image.tostring(s, 'RGBA', 1))

    return t

  def CompileShader(self, src, kind, kind_name, name):
    shader = glCreateShader(kind)
    glShaderSource(shader, [src])
    glCompileShader(shader)
    result = glGetShaderiv(shader, GL_COMPILE_STATUS)
    if not result:
      print ('Shader compilation failed (%s, %s): %s'
             % (name, kind_name, glGetShaderInfoLog(shader)))
      sys.exit(1)
    return shader

  def BuildShader(self, name, vertex_shader_src, fragment_shader_src):
    program = glCreateProgram()
    for kind, src, kind_name in (
      (GL_VERTEX_SHADER, vertex_shader_src, 'vertex'),
      (GL_FRAGMENT_SHADER, fragment_shader_src, 'fragment')):
      if not src:
        continue
      shader = self.CompileShader(src, kind, kind_name, name)
      glAttachShader(program, shader)
      glDeleteShader(shader)
    glLinkProgram(program)
    return program

  def DrawBox(self, x, y, w, h, border, ca, cb):
    # TODO: wireframe glowy-line shader
    glColor(*ca)
    glNormal(*cb)

    glBegin(GL_QUADS)

    glVertex(x, y)
    glVertex(x + border, y)
    glVertex(x + border, y + h - border)
    glVertex(x, y + h - border)

    glVertex(x + w, y)
    glVertex(x + w - border, y)
    glVertex(x + w - border, y + h - border)
    glVertex(x + w, y + h - border)

    glVertex(x, y)
    glVertex(x, y + border)
    glVertex(x + w, y + border)
    glVertex(x + w, y)

    glVertex(x, y + h)
    glVertex(x, y + h - border)
    glVertex(x + w, y + h - border)
    glVertex(x + w, y + h)

    glEnd()

  def DrawSolidBoxWithBorder(self, x, y, w, h, border):
    # TODO: use solid-color raining numbers shader
    glColor(BoxBackground)
    glBegin(GL_QUADS)
    glVertex(x, y)
    glVertex(x + w, y)
    glVertex(x + w, y + h)
    glVertex(x, y + h)
    glEnd()

    self.DrawBox(x + border, y + border, w - border * 2, h - border * 2, border,
                 Black, GreenWireframe)

  def DrawIcon(self, x, y, w, h, icon):
    prg = self.tile_shader
    glUseProgram(prg)
    glBindTexture(GL_TEXTURE_2D_ARRAY, self.icon_col_textures)
    l = glGetUniformLocation(prg, b'texture_atlas')
    glUniform1i(l, 0)
    glBegin(GL_QUADS)
    glTexCoord3f(0, 0, icon)
    glVertex(x, y)
    glTexCoord3f(1, 0, icon)
    glVertex(x + w, y)
    glTexCoord3f(1, 1, icon)
    glVertex(x + w, y + h)
    glTexCoord3f(0, 1, icon)
    glVertex(x, y + h)
    glEnd()
    glUseProgram(0)
