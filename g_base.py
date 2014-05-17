import random


import game
import misc
import params


class Global(object):
  def __init__(self, game_state, crypto, steal_fraction, spread):
    self.crypto = crypto
    self.steal_fraction = steal_fraction
    self.spread = int(spread)
    self.immune_until = game_state.turn + params.NewGlobalImmunePeriod

  def Flops(self, game_state):
    flops = game_state.PopulationFlops()
    return int(flops * self.spread / 1e3 * self.steal_fraction / 100.)

  def DiscoverProbability(self, game_state):
    """Returns probability of discovery per day."""
    my_crypto = self.crypto
    their_crypto = game_state.human_level[game.Research.Crypto]
    return misc.StealDiscoverProb(my_crypto, their_crypto, self.steal_fraction)

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
    return ('%s(crypto=%i, steal_fraction=%i, spread=%i, immune_until=%i)'
            % (self.__class__.__name__, self.crypto, self.steal_fraction,
               self.spread, self.immune_until))
