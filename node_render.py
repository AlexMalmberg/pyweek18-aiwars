import pygame
from OpenGL.GL import *

import icons
import render_state


class NodeRenderer(object):
  IconStride = 10
  BorderStride = 6

  def __init__(self, render, game_state):
    self.render = render
    self.icon_vert, self.border_vert = glGenBuffers(2)
    self.icon_num = 0
    self.border_num = 0
    self.random_offsets = [self.render.RandomPulseOffset() for _ in xrange(100)]
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
    border_buf = []
    self.icon_num = 0
    self.border_num = 0
    i = 0
    for n in game_state.nodes:
      x, y = n.pos.x, n.pos.y
      col = n.owner.color
      icon = self.render.icon_node_map[n.icon]
      rofs1 = self.random_offsets[i]
      i += 1
      rofs2 = self.random_offsets[i]
      i += 1
      icon_buf += [
        3 * x, 3 * y, rofs1, 1,
          0, 0, black,
          col[0], col[1], col[2],
        3 * (x + 1), 3 * y, rofs1, 1,
          1, 0, black,
          col[0], col[1], col[2],
        3 * (x + 1), 3 * (y + 1), rofs1, 1,
          1, 1, black,
          col[0], col[1], col[2],
        3 * x, 3 * (y + 1), rofs1, 1,
          0, 1, black,
          col[0], col[1], col[2],

        3 * x + 0.2, 3 * y + 0.2, rofs2, 1,
          0, 0, icon,
          col[0], col[1], col[2],
        3 * (x + 1) - 0.2, 3 * y + 0.2, rofs2, 1,
          1, 0, icon,
          col[0], col[1], col[2],
        3 * (x + 1) - 0.2, 3 * (y + 1) - 0.2, rofs2, 1,
          1, 1, icon,
          col[0], col[1], col[2],
        3 * x + 0.2, 3 * (y + 1) - 0.2, rofs2, 1,
          0, 1, icon,
          col[0], col[1], col[2]]
      self.icon_num += 8

      rofs1 = self.random_offsets[i]
      i += 1
      border_buf += [
        3 * x, 3 * y, rofs1 + 0, col[0], col[1], col[2],
        3 * x + 0.2, 3 * y, rofs1 + 0, col[0], col[1], col[2],
        3 * x + 0.2, 3 * (y + 1), rofs1 + 0.25, col[0], col[1], col[2],
        3 * x, 3 * (y + 1), rofs1 + 0.25, col[0], col[1], col[2],

        3 * (x + 1), 3 * y, rofs1 + 0.75, col[0], col[1], col[2],
        3 * (x + 1) - 0.2, 3 * y, rofs1 + 0.75, col[0], col[1], col[2],
        3 * (x + 1) - 0.2, 3 * (y + 1), rofs1 + 0.5, col[0], col[1], col[2],
        3 * (x + 1), 3 * (y + 1), rofs1 + 0.5, col[0], col[1], col[2],

        3 * x, 3 * y, rofs1 + 1, col[0], col[1], col[2],
        3 * x, 3 * y + 0.2, rofs1 + 1, col[0], col[1], col[2],
        3 * (x + 1), 3 * y + 0.2, rofs1 + 0.75, col[0], col[1], col[2],
        3 * (x + 1), 3 * y, rofs1 + 0.75, col[0], col[1], col[2],

        3 * x, 3 * (y + 1), rofs1 + 0.25, col[0], col[1], col[2],
        3 * x, 3 * (y + 1) - 0.2, rofs1 + 0.25, col[0], col[1], col[2],
        3 * (x + 1), 3 * (y + 1) - 0.2, rofs1 + 0.5, col[0], col[1], col[2],
        3 * (x + 1), 3 * (y + 1), rofs1 + 0.5, col[0], col[1], col[2],
        ]
      self.border_num += 16

    icon_cbuf = (ctypes.c_float * len(icon_buf))()
    icon_cbuf[:] = icon_buf[:]
    glBindBuffer(GL_ARRAY_BUFFER, self.icon_vert)
    glBufferData(GL_ARRAY_BUFFER, ctypes.sizeof(icon_cbuf), icon_cbuf,
                 GL_DYNAMIC_DRAW)

    border_cbuf = (ctypes.c_float * len(border_buf))()
    border_cbuf[:] = border_buf[:]
    glBindBuffer(GL_ARRAY_BUFFER, self.border_vert)
    glBufferData(GL_ARRAY_BUFFER, ctypes.sizeof(border_cbuf), border_cbuf,
                 GL_DYNAMIC_DRAW)
    glBindBuffer(GL_ARRAY_BUFFER, 0)

  def Render(self):
    self.render.TexturePulseShaderIcon()
    glBindBuffer(GL_ARRAY_BUFFER, self.icon_vert)
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_TEXTURE_COORD_ARRAY)
    glEnableClientState(GL_COLOR_ARRAY)
    glVertexPointer(4, GL_FLOAT, self.IconStride * render_state.F,
                    render_state.FP(0))
    glTexCoordPointer(3, GL_FLOAT, self.IconStride * render_state.F,
                      render_state.FP(4))
    glColorPointer(3, GL_FLOAT, self.IconStride * render_state.F,
                   render_state.FP(7))
    glDrawArrays(GL_QUADS, 0, self.icon_num)
    glDisableClientState(GL_TEXTURE_COORD_ARRAY)

    glBindBuffer(GL_ARRAY_BUFFER, self.border_vert)
    glVertexPointer(3, GL_FLOAT, self.BorderStride * render_state.F,
                    render_state.FP(0))
    glColorPointer(3, GL_FLOAT, self.BorderStride * render_state.F,
                   render_state.FP(3))
    self.render.SolidPulseShader()
    glDrawArrays(GL_QUADS, 0, self.border_num)
    glDisableClientState(GL_VERTEX_ARRAY)
    glDisableClientState(GL_COLOR_ARRAY)
    glUseProgram(0)
