class Vec(object):
  def __init__(self, x, y):
    self.x = x
    self.y = y

  def __repr__(self):
    return 'Vec(%i, %i)' % (self.x, self.y)

