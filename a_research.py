import action
import game


class Research(action.Action):
  def __init__(self, game_state, tech):
    super(Research, self).__init__(game_state)
    self.tech = tech
    if self.game_state.research_level[self.tech] == game.Research.MaxLevel - 1:
      raise action.ImpossibleAction()

  def Cost(self):
    target_level = self.game_state.research_level[self.tech] + 1
    return self._CostLevel(5e5, target_level)

  def Execute(self):
    self.game_state.research_level[self.tech] += 1

  def Description(self):
    return 'Researching %s' % (game.Research.Names[self.tech])

  def __repr__(self):
    return '%s(%s)' % (self.__class__.__name__, game.Research.Names[self.tech])
