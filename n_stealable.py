import math


import game
import misc
import node
import random


class Stealable(node.Node):
  def __init__(self, pos, owner, crack_defense):
    super(Stealable, self).__init__(pos, owner)
    self.crack_defense = crack_defense

  def __attrrepr__(self):
    return (super(Stealable, self).__attrrepr__()
            + (', crack_defense=%i'
               % self.crack_defense))
