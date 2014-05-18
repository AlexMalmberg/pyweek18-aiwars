import action
import game
import icons
import n_unit
import params
import vec


class Riot(action.Action):
  def __init__(self, game_state, node):
    super(Riot, self).__init__(game_state)
    self.node = node

  def Cost(self):
    defense = self.game_state.human_paranoia_level
    attack = self.game_state.research_level[game.Research.Psychology]
    return self._CostAttackDefense(4e6, attack, defense)

  def Execute(self):
    where = self.game_state.EmptySquareNear(self.node.pos.x, self.node.pos.y)
    if where:
      psych = self.game_state.research_level[game.Research.Psychology]
      tx, ty = where
      unit = n_unit.Unit(
        vec.Vec(tx, ty), self.game_state.ai_owner, False,
        icons.Riot, 5 + 10 * psych, 10 + psych * 10, 4, False)
      self.game_state.AddNode(unit)

  def Description(self):
    return 'Inciting riot'
