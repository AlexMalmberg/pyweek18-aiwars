

class ImpossibleAction(Exception):
  pass


class Action(object):
  def __init__(self, game_state):
    self.game_state = game_state

  def Cost(self):
    raise NotImplemented()

  def _CostAttackDefense(self, base_cost, attack, defense):
    cost = defense + 0.5 * (defense - attack)
    cost *= 1.3
    cost = base_cost * 10 ** cost
    return int(cost)

  def _CostLevel(self, base_cost, level):
    cost = level * 1.3
    cost = base_cost * 10 ** cost
    return int(cost)

  def Execute(self):
    raise NotImplemented()

  def __repr__(self):
    return '%s()' % self.__class__.__name__
