import action
import game
import params


class Crack(action.Action):
  def __init__(self, game_state, node):
    super(Crack, self).__init__(game_state)
    if node.control:
      raise action.ImpossibleAction()
    self.node = node

  def Cost(self):
    defense = self.game_state.human_paranoia_level + self.node.bonus_defense
    attack = self.game_state.research_level[game.Research.Cracking]
    return self._CostAttackDefense(4e6, attack, defense)

  def Execute(self):
    self.node.control = True
    self.node.Captured(self.game_state.ai_owner)
    self.node.immune_until = (
      self.game_state.turn + params.CrackedNodeImmunePeriod)

  def Description(self):
    return 'Cracking %s' % self.node.Description()
