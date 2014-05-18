import math

import action
import game


class CreateGlobal(action.Action):
  def __init__(self, game_state):
    super(CreateGlobal, self).__init__(game_state)

    # This is fixed when the global is created.
    self.crypto = game_state.research_level[game.Research.Crypto]

  def AttackLevel(self):
    raise NotImplemented()

  def DefenseLevel(self):
    raise NotImplemented()

  def Target(self):
    raise NotImplemented()

  def Cost(self):
    return self._CostLevel(1.4e6, self.AttackLevel())

  def Spread(self):
    attack = self.AttackLevel()
    defense = self.DefenseLevel()
    delta = attack - defense
    if delta > 0:
      spread = 1 - 0.8 * math.exp(-delta / 4.0)
    else:
      spread = 0.2 * math.exp(delta / 4.0)
    return int(spread * 1000)

  def Execute(self):
    self.game_state.AddGlobal(self.Target()(
        self.game_state, self.crypto, self.Spread()))
