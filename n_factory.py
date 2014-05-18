import icons
import misc
import n_stealable


class Factory(n_stealable.Stealable):
  icon = icons.Factory

  def __init__(self, pos, crack_defense, build_per_turn):
    super(Factory, self).__init__(pos, crack_defense)
    self.build_per_turn = build_per_turn
    self.building = False
    self.target = None
    self.progress = 0
    self.cost = 0

  def StartBuilding(self, game_state, target):
    self.cost = self.target.BuildCost()
    if not game_state.UseRawMaterials(self.cost):
      return
    self.building = True
    self.target = target

  def StopBuilding(self):
    self.building = False

  def Captured(self):
    self.building = False
    self.progress = 0

  def Discoverable(self):
    return self.building

  def EndOfTurnUpdate(self, game_state):
    if self.control and self.building:
      self.progress += self.steal_fraction * self.build_per_turn
      if self.progress > self.cost:
        self.target.BuiltOne(self, game_state)
        self.building = False

    super(Factory, self).EndOfTurnUpdate(game_state)

  def __attrrepr__(self):
    return (super(Factory, self).__attrrepr__()
            + (', per_turn=%i, building=%r, target=%r, progress=%i'
               % (self.build_per_turn, self.building, self.target,
                  self.progress)))

  def Description(self):
    return 'factory'
