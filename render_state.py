import ctypes
import pygame
import random
import sys
from OpenGL.GL import *

import game
import icons


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
  AnimationTimeOffsetScale = 0.1
  AnimationTimeScale = 0.1

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

    self.icon_node_map = []
    icon_file_map = {icons.City: 'city',
                     icons.Factory: 'factory',
                     icons.DataCenter: 'datacenter',
                     icons.Bomb: 'bomb',
                     icons.KillerRobot: 'robo',
                     icons.Tank: 'tank',
                     icons.Bomber: 'bomber',
                     icons.Riot: 'riot',
                     icons.Security: 'security',
                     icons.Military: 'military',
                     icons.Black: 'black'}
    for i in xrange(icons.Num):
      self.icon_node_map.append(len(files))
      files.append(icon_file_map[i])

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


# Texture:
# At each point, need:
# - Color of pulse. gl_Color.rgb
# - Tex coords to get local alpha and stroke distance. gl_TexCoord[0]
# - Local sampler offset: gl_Vertex.z
# - Local sampler scale: gl_Vertex.w
#
# Solid:
# At each point, need:
# - Color of pulse. gl_Color.rgb
# - Local pulse offset: gl_Vertex.z
#   (equal to sampler offset + sampler scale * stroke dist)

    self.solid_pulse_shader = self.BuildShader('solid pulse shader', """
#version 120

varying vec4 color;
varying float stroke_distance;

void main() {
  gl_Position = gl_ModelViewProjectionMatrix * vec4(gl_Vertex.xy, 0, 1);
  color = gl_Color;
  stroke_distance = gl_Vertex.z;
}
""", """
#version 120

uniform sampler1D line_pulse;
uniform float global_pulse_offset;
uniform float global_pulse_scale;

varying vec4 color;
varying float stroke_distance;

void main(){
  float offset = global_pulse_offset + stroke_distance * global_pulse_scale;
  float pulse = 2.0 * texture1D(line_pulse, offset);

  vec4 col;
  if (pulse > 1)
    col = mix(color, vec4(1, 1, 1, 1), pulse - 1);
  else
    col = mix(vec4(0, 0, 0, 1), color, pulse);
  gl_FragColor = col;
}
""")

    # TODO: proper blending
    # r = ur * (1 - a) * (1 - ga) + (tr * a * (1 - ga) + gr * ga)
    # so set a = 1 - (1 - a) * (1 - ga)
    #
    # then find r so that:
    # r * (1 - a) * (1 - ga) = tr * a * (1 - ga) + gr * ga
    #
    # r = tr * a / (1 - a) + gr * ga / (1 - a) * (1 - ga)

    self.texture_pulse_shader = self.BuildShader('solid pulse shader', """
#version 120

varying vec4 color;
varying float sampler_offset;
varying float sampler_scale;

void main() {
  gl_Position = gl_ModelViewProjectionMatrix * vec4(gl_Vertex.xy, 0, 1);
  gl_TexCoord[0].xyz = gl_MultiTexCoord0.xyz;
  color = gl_Color;
  sampler_offset = gl_Vertex.z;
  sampler_scale = gl_Vertex.w;
}
""", """
#version 130

uniform sampler2DArray color_tex;
uniform sampler2DArray line_tex;

uniform sampler1D line_pulse;
uniform float global_pulse_offset;
uniform float global_pulse_scale;

uniform float base_strength;
uniform float pulse_strength;

varying vec4 color;
varying float sampler_offset;
varying float sampler_scale;

void main(){
  vec4 base_color = texture(color_tex, gl_TexCoord[0].xyz) * base_strength;
  vec4 line_color = texture(line_tex, gl_TexCoord[0].xyz);

  float stroke_dist = line_color.r * sampler_scale + sampler_offset;
  float offset = global_pulse_offset + stroke_dist * global_pulse_scale;
  float pulse = 2.0 * texture1D(line_pulse, offset);
  pulse *= pulse_strength;

  vec4 pulse_col;
  if (pulse > 1)
    pulse_col = mix(color, vec4(1, 1, 1, 1), pulse - 1);
  else
    pulse_col = mix(vec4(0, 0, 0, 1), color, pulse);

  gl_FragColor = base_color + line_color.a * pulse_col;
}
""")

    self.line_pulse_texture = glGenTextures(1)
    pw = 8
    cbuf = (ctypes.c_ubyte * pw)()
    for i in xrange(pw):
      cbuf[i] = random.randint(80, 255)
    glBindTexture(GL_TEXTURE_1D, self.line_pulse_texture)
    glTexParameter(GL_TEXTURE_1D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameter(GL_TEXTURE_1D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameter(GL_TEXTURE_1D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexImage1D(GL_TEXTURE_1D, 0, 1, pw, 0, GL_RED, GL_UNSIGNED_BYTE, cbuf)

  def _TexturePulseShaderCommon(self):
    prg = self.texture_pulse_shader
    glUseProgram(prg)

    l = glGetUniformLocation(prg, b'global_pulse_offset')
    glUniform1f(l, self.animation_time * self.AnimationTimeOffsetScale)
    l = glGetUniformLocation(prg, b'global_pulse_scale')
    glUniform1f(l, self.AnimationTimeScale)

    l = glGetUniformLocation(prg, b'base_strength')
    glUniform1f(l, 1 - self.wireframe_frac)
    l = glGetUniformLocation(prg, b'pulse_strength')
    glUniform1f(l, 0.4 + 0.6 * self.wireframe_frac)

    glActiveTexture(GL_TEXTURE2)
    glBindTexture(GL_TEXTURE_1D, self.line_pulse_texture)
    l = glGetUniformLocation(prg, b'line_pulse')
    glUniform1i(l, 2)

  def TexturePulseShaderTile(self):
    prg = self.texture_pulse_shader
    self._TexturePulseShaderCommon()

    glActiveTexture(GL_TEXTURE1)
    glBindTexture(GL_TEXTURE_2D_ARRAY, self.tile_line_textures)
    l = glGetUniformLocation(prg, b'line_tex')
    glUniform1i(l, 1)

    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D_ARRAY, self.tile_col_textures)
    l = glGetUniformLocation(prg, b'color_tex')
    glUniform1i(l, 0)

  def TexturePulseShaderIcon(self):
    prg = self.texture_pulse_shader
    self._TexturePulseShaderCommon()

    glActiveTexture(GL_TEXTURE1)
    glBindTexture(GL_TEXTURE_2D_ARRAY, self.icon_line_textures)
    l = glGetUniformLocation(prg, b'line_tex')
    glUniform1i(l, 1)

    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D_ARRAY, self.icon_col_textures)
    l = glGetUniformLocation(prg, b'color_tex')
    glUniform1i(l, 0)

  def SolidPulseShader(self):
    prg = self.solid_pulse_shader
    glUseProgram(prg)
    glBindTexture(GL_TEXTURE_1D, self.line_pulse_texture)
    l = glGetUniformLocation(prg, b'line_pulse')
    glUniform1i(l, 0)
    l = glGetUniformLocation(prg, b'global_pulse_offset')
    glUniform1f(l, self.animation_time * self.AnimationTimeOffsetScale)
    l = glGetUniformLocation(prg, b'global_pulse_scale')
    glUniform1f(l, self.AnimationTimeScale)

  def RandomPulseOffset(self):
    return random.uniform(0, 10)

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
    wf = self.wireframe_frac
    nf = 1. - wf
    col = (ca[0] * nf + cb[0] * wf,
           ca[1] * nf + cb[1] * wf,
           ca[2] * nf + cb[2] * wf)
    glColor(col[0], col[1], col[2])

    ofs = (x - y) * 4.

    self.SolidPulseShader()
    glBegin(GL_QUADS)

    glVertex(x, y, ofs + 0)
    glVertex(x + border, y, ofs + 0)
    glVertex(x + border, y + h - border, ofs + 0.25)
    glVertex(x, y + h - border, ofs + 0.25)

    glVertex(x + w, y, ofs + 0.75)
    glVertex(x + w - border, y, ofs + 0.75)
    glVertex(x + w - border, y + h - border, ofs + 0.5)
    glVertex(x + w, y + h - border, ofs + 0.5)

    glVertex(x, y, ofs + 1)
    glVertex(x, y + border, ofs + 1)
    glVertex(x + w, y + border, ofs + 0.75)
    glVertex(x + w, y, ofs + 0.75)

    glVertex(x, y + h, ofs + 0.25)
    glVertex(x, y + h - border, ofs + 0.25)
    glVertex(x + w, y + h - border, ofs + 0.5)
    glVertex(x + w, y + h, ofs + 0.5)

    glEnd()
    glUseProgram(0)

  def DrawSolidBoxWithBorder(self, x, y, w, h, border):
    # TODO: use solid-color raining numbers shader
    wf = self.wireframe_frac
    nf = 1. - wf
    ca = BoxBackground
    cb = Black
    col = (ca[0] * nf + cb[0] * wf,
           ca[1] * nf + cb[1] * wf,
           ca[2] * nf + cb[2] * wf)
    glColor(col[0], col[1], col[2])
    glBegin(GL_QUADS)
    glVertex(x, y)
    glVertex(x + w, y)
    glVertex(x + w, y + h)
    glVertex(x, y + h)
    glEnd()

    self.DrawBox(x + border, y + border, w - border * 2, h - border * 2, border,
                 Black, GreenWireframe)

  def DrawIcon(self, x, y, w, h, icon):
    self.TexturePulseShaderIcon()
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

  def DrawProgressBar(self, x, y, w, h, progress):
    glBegin(GL_QUADS)
    xmid = x + w * progress

    wf = self.wireframe_frac
    nf = 1. - wf

    ca = (0, 0.7, 0)
    cb = (0.2, 1.0, 0.2)
    col = (ca[0] * nf + cb[0] * wf,
           ca[1] * nf + cb[1] * wf,
           ca[2] * nf + cb[2] * wf)
    glColor(col[0], col[1], col[2], 1)

    glVertex(x, y)
    glVertex(x, y + h)
    glVertex(xmid, y + h )
    glVertex(xmid, y)

    ca = (0, 0, 0)
    cb = (0.2, 0.2, 0.2)
    col = (ca[0] * nf + cb[0] * wf,
           ca[1] * nf + cb[1] * wf,
           ca[2] * nf + cb[2] * wf)
    glColor(col[0], col[1], col[2], 1)

    glVertex(xmid, y)
    glVertex(xmid, y + h)
    glVertex(x + w, y + h )
    glVertex(x + w, y)
    glEnd()

  def TextColor(self):
    wf = self.wireframe_frac
    nf = 1. - wf

    ca = (0.0, 0.0, 0.0)
    cb = (0.4, 1.0, 0.4)
    col = (ca[0] * nf + cb[0] * wf,
           ca[1] * nf + cb[1] * wf,
           ca[2] * nf + cb[2] * wf,
           1)
    return col
