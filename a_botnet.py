import a_global
import game
import g_botnet


class CreateBotnet(a_global.CreateGlobal):
  def __init__(self, game_state):
    super(CreateBotnet, self).__init__(game_state)

  def AttackLevel(self):
    return self.game_state.research_level[game.Research.Cracking]

  def DefenseLevel(self):
    return self.game_state.human_level[game.Research.Crypto]

  def Target(self):
    return g_botnet.Botnet
