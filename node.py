import misc


class Node(object):
  def __init__(self, pos, flops, crack_defense):
    self.pos = pos
    self.flops = int(flops)
    self.control = False
    self.crack_defense = crack_defense
    self.flops_steal_fraction = 0

  def ControlledFlops(self):
    if not self.control:
      return 0
    return self.flops * self.flops_steal_fraction / 100

  def __repr__(self):
    return ('%s(%r, %s, %r, %i)'
            % (self.__class__.__name__, self.pos, misc.FormatFlops(self.flops),
               self.control, self.crack_defense))
