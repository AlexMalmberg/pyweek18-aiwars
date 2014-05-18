import pygame
from OpenGL.GL import *

import icons
import render_state


class NodeRenderer(object):
  VertStride = 5

  def __init__(self, render, game_state):
    self.render = render
    self.icon_vert, self.border_vert = glGenBuffers(2)
    self.icon_num = 0
    self.border_num = 0
    self.Update(game_state)

  def __del__(self):
    try:
      glDeleteBuffers(self.icon_vert)
      glDeleteBuffers(self.border_vert)
    except:
      pass

  def Update(self, game_state):
    black = self.render.icon_node_map[icons.Black]
    icon_buf = []
    self.icon_num = 0
    for n in game_state.nodes:
      x, y = n.pos.x, n.pos.y
      icon = self.render.icon_node_map[n.icon]
      icon_buf += [
        3 * x, 3 * y, 0, 0, black,
        3 * (x + 1), 3 * y, 1, 0, black,
        3 * (x + 1), 3 * (y + 1), 1, 1, black,
        3 * x, 3 * (y + 1), 0, 1, black,

        3 * x + 0.2, 3 * y + 0.2, 0, 0, icon,
        3 * (x + 1) - 0.2, 3 * y + 0.2, 1, 0, icon,
        3 * (x + 1) - 0.2, 3 * (y + 1) - 0.2, 1, 1, icon,
        3 * x + 0.2, 3 * (y + 1) - 0.2, 0, 1, icon]
      self.icon_num += 8
    icon_cbuf = (ctypes.c_float * len(icon_buf))()
    icon_cbuf[:] = icon_buf[:]
    glBindBuffer(GL_ARRAY_BUFFER, self.icon_vert)
    glBufferData(GL_ARRAY_BUFFER, ctypes.sizeof(icon_cbuf), icon_cbuf,
                 GL_DYNAMIC_DRAW)
    glBindBuffer(GL_ARRAY_BUFFER, 0)

  def Render(self):
    prg = self.render.tile_shader
    glUseProgram(prg)
    glBindTexture(GL_TEXTURE_2D_ARRAY, self.render.icon_col_textures)
    l = glGetUniformLocation(prg, b'texture_atlas')
    glUniform1i(l, 0)
    glBindBuffer(GL_ARRAY_BUFFER, self.icon_vert)
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_TEXTURE_COORD_ARRAY)
    glVertexPointer(2, GL_FLOAT, self.VertStride * render_state.F,
                    render_state.FP(0))
    glTexCoordPointer(3, GL_FLOAT, self.VertStride * render_state.F,
                      render_state.FP(2))
    glDrawArrays(GL_QUADS, 0, self.icon_num)
    glDisableClientState(GL_VERTEX_ARRAY)
    glDisableClientState(GL_TEXTURE_COORD_ARRAY)
    glUseProgram(0)

"""
    prg = self.render.tile_shader
    GL.glUseProgram(prg)
    GL.glBindTexture(GL.GL_TEXTURE_2D_ARRAY, self.render.icon_col_textures)
    l = GL.glGetUniformLocation(prg, b'texture_atlas')
    GL.glUniform1i(l, 0)
    GL.glBegin(GL.GL_QUADS)
    for n in self.game_state.nodes:
      x, y = n.pos.x, n.pos.y
      icon = self.render.icon_node_map[n.icon]
      GL.glTexCoord3f(0, 0, icon)
      GL.glVertex(3 * x, 3 * y)
      GL.glTexCoord3f(1, 0, icon)
      GL.glVertex(3 * (x + 1), 3 * y)
      GL.glTexCoord3f(1, 1, icon)
      GL.glVertex(3 * (x + 1), 3 * (y + 1))
      GL.glTexCoord3f(0, 1, icon)
      GL.glVertex(3 * x, 3 * (y + 1))
    GL.glEnd()
    GL.glUseProgram(0)
"""
