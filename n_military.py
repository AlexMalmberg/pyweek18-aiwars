import icons
import misc
import n_stealable
import n_unit
import vec


class Military(n_stealable.Stealable):
  icon = icons.Military

  def __init__(self, pos, owner, bonus_defense, nukes):
    super(Military, self).__init__(pos, owner, bonus_defense)
    self.nukes = nukes

  def __attrrepr__(self):
    return (super(Military, self).__attrrepr__()
            + (', nukes=%i' % self.nukes))

  def Description(self):
    return 'military base'
