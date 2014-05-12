import action
import game


class Crack(action.Action):
  def __init__(self, game_state, node):
    super(Crack, self).__init__(game_state)
    if node.control:
      raise action.ImpossibleAction()
    self.node = node

  def Cost(self):
    defense = self.node.crack_defense
    attack = self.game_state.research_level[game.Research.Cracking]
    return self._CostAttackDefense(400, attack, defense)

  def Execute(self):
    self.node.control = True
    self.node.flops_steal_fraction = 20
