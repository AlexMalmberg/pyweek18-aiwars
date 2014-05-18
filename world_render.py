import pygame
import random
from OpenGL.GL import *


import render_state
import world


def Fix(x, y):
  return (x, y, (x + y) / 20., 1 / 20.)


class WorldRenderer(object):
  # 0 - 3: vertex
  # 4 - 5: tex coord
  VertStride = 7

  def __init__(self, render, world):
    self.render = render
    self.world = world
    self.vbo_index = None
    self.vbo_vert = None

    self.texture = render.tile_col_textures
    self.z_land = render.z_land
    self.z_water = render.z_water
    self.z_line = render.z_line
    self.z_line_num = render.z_line_num
    self.z_ic = render.z_ic
    self.z_ic_num = render.z_ic_num
    self.z_oc = render.z_oc
    self.z_oc_num = render.z_oc_num
    self.prg = render.tile_shader
    self._PrepareRendering()

  def __del__(self):
    try:
      if self.vbo_index is not None:
        glDeleteBuffers(self.vbo_index)
        self.vbo_index = None
      if self.vbo_vert is not None:
        glDeleteBuffers(self.vbo_vert)
        self.vbo_vert = None
    except:
      pass

  def GetRandomLine(self):
    return random.randint(self.z_line, self.z_line + self.z_line_num - 1)
  def GetRandomInsideCircle(self):
    return random.randint(self.z_ic, self.z_ic + self.z_ic_num - 1)
  def GetRandomOutsideCircle(self):
    return random.randint(self.z_oc, self.z_oc + self.z_oc_num - 1)

  def _GetNeighbour(self, x, y):
    if x < 0 or y < 0 or x >= self.world.width or y >= self.world.height:
      return world.Water
    return self.world.map[x][y]

  def _GenTileCorner(self, x, y, n, n1, n2, n3, tc):
    # For corners:
    # LL  Inside circle.
    # Lx
    #
    # WL  Outside circle.
    # Lx
    #
    # LW  Inside circle.
    # Wx
    #
    # LL  Horizontal line.
    # Wx
    #
    # WL  Horizontal line.
    # Wx
    #
    # LW  Vertical line.
    # Lx
    #
    # WW  Vertical line.
    # Lx
    #
    # WW  Solid water.
    # Wx
    b = n[n1] == world.Water
    a = n[n2] == world.Water
    c = n[n3] == world.Water
    if not b and not c:
      self._AddMiniQuad(x, y, self.GetRandomOutsideCircle(), tc)
    elif not a and b and c:
      self._AddMiniQuad(x, y, self.GetRandomInsideCircle(), tc)
    elif not b and c:
      self._AddMiniQuad(x, y, self.GetRandomLine(), tc)
    elif b and not c:
      self._AddMiniQuad(x, y, self.GetRandomLine(),
                        ((tc[3], tc[0], tc[1], tc[2])))
    else:
      self._AddMiniQuad(x, y, self.z_water,
                        ((0, 0), (1, 0), (1, 1), (0, 1)))

  def _GenTileSide(self, x, y, n, tc):
    if n == world.Water:
      self._AddMiniQuad(x, y, self.z_water,
                        ((0, 0), (1, 0), (1, 1), (0, 1)))
    else:
      self._AddMiniQuad(x, y, self.GetRandomLine(), tc)

  def _GenTile(self, x, y):
    me = self.world.map[x][y]
    if me == world.Land:
      self._AddFullQuad(x, y, self.z_land)
      return
    n = []
    for dy in (-1, 0, 1):
      for dx in (-1, 0, 1):
        if dx or dy:
          n.append(self._GetNeighbour(x + dx, y + dy))
    if all(a == world.Water for a in n):
      self._AddFullQuad(x, y, self.z_water)
      return

    self._AddMiniQuad(3 * x + 1, 3 * y + 1, self.z_water,
                      ((0, 0), (1, 0), (1, 1), (0, 1)))

    # 0 1 2
    # 3 . 4
    # 5 6 7
    self._GenTileCorner(3 * x, 3 * y, n, 3, 0, 1,
                        ((0, 1),
                         (0, 0),
                         (1, 0),
                         (1, 1)))
    self._GenTileCorner(3 * x + 2, 3 * y, n, 1, 2, 4,
                        ((1, 1),
                         (0, 1),
                         (0, 0),
                         (1, 0)))
    self._GenTileCorner(3 * x + 2, 3 * y + 2, n, 4, 7, 6,
                        ((1, 0),
                         (1, 1),
                         (0, 1),
                         (0, 0)))
    self._GenTileCorner(3 * x, 3 * y + 2, n, 6, 5, 3,
                        ((0, 0),
                         (1, 0),
                         (1, 1),
                         (0, 1)))

    self._GenTileSide(3 * x + 1, 3 * y, n[1],
                      ((1, 1),
                       (0, 1),
                       (0, 0),
                       (1, 0)))
    self._GenTileSide(3 * x + 1, 3 * y + 2, n[6],
                      ((0, 0),
                       (1, 0),
                       (1, 1),
                       (0, 1)))
    self._GenTileSide(3 * x, 3 * y + 1, n[3],
                      ((0, 1),
                       (0, 0),
                       (1, 0),
                       (1, 1)))
    self._GenTileSide(3 * x + 2, 3 * y + 1, n[4],
                      ((1, 0),
                       (1, 1),
                       (0, 1),
                       (0, 0)))

  def _AddMiniQuad(self, x, y, z, tex_coords):
    self.quad_coord.append(Fix(x, y))
    self.quad_tcoord.append((tex_coords[0][0], tex_coords[0][1], z))
    self.quad_coord.append(Fix(x + 1, y))
    self.quad_tcoord.append((tex_coords[1][0], tex_coords[1][1], z))
    self.quad_coord.append(Fix(x + 1, y + 1))
    self.quad_tcoord.append((tex_coords[2][0], tex_coords[2][1], z))
    self.quad_coord.append(Fix(x, y + 1))
    self.quad_tcoord.append((tex_coords[3][0], tex_coords[3][1], z))

  def _AddFullQuad(self, x, y, z):
    self.quad_coord.append(Fix(3 * x, 3 * y))
    self.quad_tcoord.append((0, 0, z))
    self.quad_coord.append(Fix(3 * (x + 1), 3 * y))
    self.quad_tcoord.append((1, 0, z))
    self.quad_coord.append(Fix(3 * (x + 1), 3 * (y + 1)))
    self.quad_tcoord.append((1, 1, z))
    self.quad_coord.append(Fix(3 * x, 3 * (y + 1)))
    self.quad_tcoord.append((0, 1, z))

  def _PrepareRendering(self):
    self.quad_coord = []
    self.quad_tcoord = []
    for y in xrange(self.world.height):
      for x in xrange(self.world.width):
        self._GenTile(x, y)

    n = self.num_index = len(self.quad_coord)
    self.vbo_index, self.vbo_vert = glGenBuffers(2)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vbo_index)
    indices = (ctypes.c_int * n)()
    for i in xrange(n):
      indices[i] = i
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, ctypes.sizeof(indices), indices,
                 GL_STATIC_DRAW)

    glBindBuffer(GL_ARRAY_BUFFER, self.vbo_vert)
    verts = (ctypes.c_float * (n * self.VertStride))()
    for i in xrange(n):
      verts[i * self.VertStride + 0] = self.quad_coord[i][0]
      verts[i * self.VertStride + 1] = self.quad_coord[i][1]
      verts[i * self.VertStride + 2] = self.quad_coord[i][2]
      verts[i * self.VertStride + 3] = self.quad_coord[i][3]
      verts[i * self.VertStride + 4] = self.quad_tcoord[i][0]
      verts[i * self.VertStride + 5] = self.quad_tcoord[i][1]
      verts[i * self.VertStride + 6] = self.quad_tcoord[i][2]
    glBufferData(GL_ARRAY_BUFFER, ctypes.sizeof(verts), verts,
                 GL_STATIC_DRAW)

  def Draw(self):
    #glUseProgram(self.prg)
    #glBindTexture(GL_TEXTURE_2D_ARRAY, self.texture)
    #l = glGetUniformLocation(self.prg, b'texture_atlas')
    #glUniform1i(l, 0)
    self.render.TexturePulseShaderTile()
    glColor(0, 1, 0, 1)
    glBindBuffer(GL_ARRAY_BUFFER, self.vbo_vert)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vbo_index)
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_TEXTURE_COORD_ARRAY)
    glVertexPointer(4, GL_FLOAT, self.VertStride * render_state.F,
                    render_state.FP(0))
    glTexCoordPointer(3, GL_FLOAT, self.VertStride * render_state.F,
                      render_state.FP(4))
    glDrawElements(GL_QUADS, self.num_index, GL_UNSIGNED_INT, None)
    glDisableClientState(GL_VERTEX_ARRAY)
    glDisableClientState(GL_TEXTURE_COORD_ARRAY)
    glUseProgram(0)
