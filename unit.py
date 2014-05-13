# Units we want:
# - Rioters
# - Human land unit
# - Human flying unit
# - Human-robot land unit
# - Human-robot flying unit
# - Robot land unit
# - Robot flying unit
# - Nuke
#

class UnitClass(Buildable):
  def __init__(self, level, flying, nuke):
    self.level = level
    self.flying = flying
    self.oneshot = oneshot
    self.nuke = nuke

  def BuildCost(self):
    return self.level * 10

  def __repr__(self):
    return ('UnitClass(level=%i, flying=%r, nuke=%r)'
            % (self.level, self.flying, self.oneshot, self.nuke))
