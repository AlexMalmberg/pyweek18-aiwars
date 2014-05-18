import icons
import misc
import n_stealable


class Datacenter(n_stealable.Stealable):
  icon = icons.DataCenter

  def __init__(self, pos, crack_defense, flops):
    super(Datacenter, self).__init__(pos, crack_defense)
    self.flops = int(flops)

  def Discoverable(self):
    return True

  def Flops(self):
    if not self.control:
      return 0
    return int(self.flops * self.steal_fraction / 100)

  def __attrrepr__(self):
    return (super(Datacenter, self).__attrrepr__()
            + (', flops=%r' % misc.FormatFlops(self.flops)))
