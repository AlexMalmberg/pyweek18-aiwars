import action
import game


class Upload(action.Action):
  def __init__(self, game_state, target_nano, node):
    super(Upload, self).__init__(game_state)
    self.target_nano = target_nano
    self.node = node

  def Cost(self):
    defense = self.game_state.human_paranoia_level
    attack = self.game_state.research_level[game.Research.Psychology]
    return self._CostAttackDefense(4e6, attack, defense)

  def Execute(self):
    self.node.nanotech_level = self.target_nano

  def Description(self):
    return 'Uploading population'
