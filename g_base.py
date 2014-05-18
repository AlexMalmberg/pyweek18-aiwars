import random


import game
import misc
import params


class Global(object):
  def __init__(self, game_state, crypto, spread):
    self.crypto = crypto
    self.spread = int(spread)
    self.immune_until = game_state.turn + params.NewGlobalImmunePeriod

  def Flops(self, game_state):
    flops = game_state.PopulationFlops()
    return int(flops * self.spread / 1e3)

  def DiscoverProbability(self, game_state):
    """Returns probability of discovery per day."""
    my_crypto = self.crypto
    their_crypto = game_state.human_level[game.Research.Crypto]
    return misc.StealDiscoverProb(my_crypto, their_crypto, 10)

  def Discovered(self, game_state):
    # TODO: notify
    game_state.RemoveGlobal(self)

  def EndOfTurnUpdate(self, game_state):
    if self.immune_until < game_state.turn:
      day_prob = self.DiscoverProbability(game_state)
      hour_prob = misc.DayProbToHourProb(day_prob)
      if random.uniform(0, 1) < hour_prob:
        self.Discovered(game_state)

  def __repr__(self):
    return ('%s(crypto=%i, spread=%i, immune_until=%i)'
            % (self.__class__.__name__, self.crypto,
               self.spread, self.immune_until))
