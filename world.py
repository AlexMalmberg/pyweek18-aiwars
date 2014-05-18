import ctypes


Water = 0
Land = 1


class World(object):
  # Setup is self.map[x][y]. (0, 0) is the lower left corner.

  def __init__(self, width, height):
    self.width = width
    self.height = height
    self.map = (ctypes.c_byte * height * width)()

  def LandAt(self, x, y):
    return self.map[x][y] == Land


def LoadWorld(filename):
  with open(filename, 'rt') as f:
    hdr = f.readline()
    width, height = map(int, hdr.split())
    w = World(width, height)
    for y in xrange(height):
      l = f.readline()
      for x in xrange(width):
        if l[x] == '1':
          w.map[x][height - 1 - y] = Land
        else:
          w.map[x][height - 1 - y] = Water
  return w
