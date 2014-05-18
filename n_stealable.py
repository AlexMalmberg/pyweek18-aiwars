import math


import game
import misc
import node
import random


class Stealable(node.Node):
  def __init__(self, pos, owner, bonus_defense):
    super(Stealable, self).__init__(pos, owner)
    self.bonus_defense = bonus_defense
