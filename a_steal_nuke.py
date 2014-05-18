import action
import game
import icons
import n_unit
import params
import vec


class StealNuke(action.Action):
  def __init__(self, game_state, node):
    super(StealNuke, self).__init__(game_state)
    self.node = node

  def Cost(self):
    defense = self.game_state.human_paranoia_level
    attack = self.game_state.research_level[game.Research.Cracking]
    return self._CostAttackDefense(4e6, attack, defense)

  def Execute(self):
    where = self.game_state.EmptySquareNear(self.node.pos.x, self.node.pos.y)
    if where:
      tx, ty = where
      unit = n_unit.Nuke(vec.Vec(tx, ty), self.game_state.ai_owner)
      self.game_state.AddNode(unit)

    self.node.nukes -= 1
    if not self.node.nukes:
      # Let other code clean this up.
      self.node.health = -1000

  def Description(self):
    return 'Stealing nuke'
