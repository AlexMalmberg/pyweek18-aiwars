import icons
import misc
import n_stealable
import n_unit
import vec


class Factory(n_stealable.Stealable):
  icon = icons.Factory

  def __init__(self, pos, owner, bonus_defense, build_per_turn):
    super(Factory, self).__init__(pos, owner, bonus_defense)
    self.build_per_turn = build_per_turn
    self.progress = 0
    self.cost = 50

  def EndOfTurnUpdate(self, game_state):
    if self.control:
      self.progress += self.build_per_turn
      if self.progress > self.cost:
        self.BuildOne(game_state)
        self.progress = 0

    super(Factory, self).EndOfTurnUpdate(game_state)

  def BuildOne(self, game_state):
    where = game_state.EmptySquareNear(self.pos.x, self.pos.y)
    if where:
      self.PlaceUnitAt(game_state, where[0], where[1])

  def PlaceUnitAt(self, game_state, tx, ty):
    unit = n_unit.Unit(
      vec.Vec(tx, ty), game_state.ai_owner, False,
      icons.KillerRobot, 10, 40, 4, True)
    game_state.AddNode(unit)

  def __attrrepr__(self):
    return (super(Factory, self).__attrrepr__()
            + (', per_turn=%i, building=%r, target=%r, progress=%i'
               % (self.build_per_turn, self.building, self.target,
                  self.progress)))

  def Description(self):
    return 'factory'
