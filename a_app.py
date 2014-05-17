import a_global
import game
import g_app


class CreateApp(a_global.CreateGlobal):
  def __init__(self, game_state):
    super(CreateApp, self).__init__(game_state)

  def AttackLevel(self):
    return self.game_state.research_level[game.Research.Psychology]

  def DefenseLevel(self):
    return self.game_state.human_paranoia_level

  def Target(self):
    return g_app.App

  def Description(self):
    return 'Creating app'
