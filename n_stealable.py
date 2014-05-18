import math


import game
import misc
import node
import random


class Stealable(node.Node):
  def __init__(self, pos, owner, crack_defense):
    super(Stealable, self).__init__(pos, owner)
    self.crack_defense = crack_defense
    self.steal_fraction = 0

  def DiscoverProbability(self, game_state):
    """Returns probability of discovery per day."""
    if not self.control:
      return 0
    my_crypto = game_state.research_level[game.Research.Crypto]
    their_crypto = game_state.human_level[game.Research.Crypto]
    return misc.StealDiscoverProb(my_crypto, their_crypto, self.steal_fraction)

  def Discoverable(self):
    raise NotImplemented()

  def Discovered(self):
    super(Stealable, self).Discovered()
    self.steal_fraction = 0

  def EndOfTurnUpdate(self, game_state):
    if self.control and self.Discoverable():
      if self.immune_until < game_state.turn:
        day_prob = self.DiscoverProbability(game_state)
        hour_prob = misc.DayProbToHourProb(day_prob)
        if random.uniform(0, 1) < hour_prob:
          self.Discovered()

  def __attrrepr__(self):
    return (super(Stealable, self).__attrrepr__()
            + (', crack_defense=%i, steal_fraction=%i'
               % (self.crack_defense, self.steal_fraction)))
