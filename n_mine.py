import misc
import n_stealable


class Mine(n_stealable.Stealable):
  def __init__(self, pos, crack_defense, raw_material_per_turn):
    super(Mine, self).__init__(pos, crack_defense)
    self.raw_material_per_turn = raw_material_per_turn
    self.steal_accum = 0

  def Captured(self):
    self.steal_accum = 0

  def Discoverable(self):
    return True

  def EndOfTurnUpdate(self, game_state):
    if self.control:
      self.steal_accum += self.raw_material_per_turn * self.steal_fraction
      stolen = self.steal_accum / 100
      self.steal_accum %= 100
      if stolen:
        game_state.GiveRawMaterial(stolen)

    super(Mine, self).EndOfTurnUpdate(game_state)

  def __attrrepr__(self):
    return (super(Mine, self).__attrrepr__()
            + (', per_turn=%i, accum=%i'
               % (self.raw_material_per_turn, self.steal_accum)))
