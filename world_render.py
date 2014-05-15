import pygame
import random
from OpenGL.GL import *


import world


class WorldRenderer(object):
  def __init__(self, render, world):
    self.render = render
    self.world = world

    files = []
    self.z_land = len(files)
    files.append('data/tile_land.png')
    self.z_water = len(files)
    files.append('data/tile_water.png')

    self.z_line = len(files)
    self.z_line_num = 16
    for i in xrange(self.z_line_num):
      files.append('data/line%02i_col.png' % i)
    self.z_ic = len(files)
    self.z_ic_num = 16
    for i in xrange(self.z_ic_num):
      files.append('data/ic%02i_col.png' % i)
    self.z_oc = len(files)
    self.z_oc_num = 16
    for i in xrange(self.z_oc_num):
      files.append('data/oc%02i_col.png' % i)

    self.texture = render.LoadTextureArray(files)

    self.prg = render.BuildShader("""
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
//  gl_FragColor = texture(texture_atlas, vec3(gl_TexCoord[0].xy, 2));
}
""")

    self._PrepareRendering()

  def __del__(self):
    try:
      # TODO: Free buffer objects and stuff.
      pass
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
      print 'solid'

  def _GenTileSide(self, x, y, n, tc):
    if n == world.Water:
      self._AddMiniQuad(x, y, self.z_water,
                        ((0, 0), (1, 0), (1, 1), (0, 1)))
    else:
      self._AddMiniQuad(x, y, self.GetRandomLine(), tc)

  def _GenTile(self, x, y):
    print '_GenTile: %i, %i' % (x, y)
    me = self.world.map[x][y]
    if me == world.Land:
      self._AddFullQuad(x, y, self.z_land)
      print 'Generate single quad with land texture for entire tile.'
      return
    n = []
    for dy in (-1, 0, 1):
      for dx in (-1, 0, 1):
        if dx or dy:
          n.append(self._GetNeighbour(x + dx, y + dy))
    if all(a == world.Water for a in n):
      self._AddFullQuad(x, y, self.z_water)
      print 'Generate single quad with water texture for entire tile.'
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
    self.quad_coord.append((x, y))
    self.quad_tcoord.append((tex_coords[0][0], tex_coords[0][1], z))
    self.quad_coord.append((x + 1, y))
    self.quad_tcoord.append((tex_coords[1][0], tex_coords[1][1], z))
    self.quad_coord.append((x + 1, y + 1))
    self.quad_tcoord.append((tex_coords[2][0], tex_coords[2][1], z))
    self.quad_coord.append((x, y + 1))
    self.quad_tcoord.append((tex_coords[3][0], tex_coords[3][1], z))

  def _AddFullQuad(self, x, y, z):
    self.quad_coord.append((3 * x, 3 * y))
    self.quad_tcoord.append((0, 0, z))
    self.quad_coord.append((3 * (x + 1), 3 * y))
    self.quad_tcoord.append((1, 0, z))
    self.quad_coord.append((3 * (x + 1), 3 * (y + 1)))
    self.quad_tcoord.append((1, 1, z))
    self.quad_coord.append((3 * x, 3 * (y + 1)))
    self.quad_tcoord.append((0, 1, z))

  def _PrepareRendering(self):
    self.quad_coord = []
    self.quad_tcoord = []
    for y in xrange(self.world.height):
      for x in xrange(self.world.width):
        self._GenTile(x, y)

  def Draw(self):
    glPushMatrix(GL_MODELVIEW)
    glTranslate(-0.8, -0.8, 0)
    glScale(0.05, 0.05, 1)
    glUseProgram(self.prg)
    glBindTexture(GL_TEXTURE_2D_ARRAY, self.texture)
    l = glGetUniformLocation(self.prg, 'texture_atlas')
    glUniform1i(l, 0)
    #glEnable(GL_TEXTURE_3D)
    glBegin(GL_QUADS)
    for c, tc in zip(self.quad_coord, self.quad_tcoord):
      glTexCoord3f(tc[0], tc[1], tc[2])
      glVertex(c)
    glEnd()
    glDisable(GL_TEXTURE_2D)
    glUseProgram(0)
    glPopMatrix(GL_MODELVIEW)
