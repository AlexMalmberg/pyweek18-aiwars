import ctypes


Water = 0
Land = 1


class World(object):
  # Setup is self.map[x][y]. (0, 0) is the lower left corner.

  def __init__(self, width, height):
    self.width = width
    self.height = height
    self.map = (ctypes.c_byte * height * width)()
