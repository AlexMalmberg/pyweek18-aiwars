import random

import icons
import game
import misc
import node


class Unit(node.Node):
  def __init__(self, pos, owner, can_fly, icon, strength, health, move_div,
               robotics_based):
    super(Unit, self).__init__(pos, owner)
    self.health = self.max_health = health
    self.icon = icon
    self.can_fly = can_fly
    self.strength = strength
    self.move_div = move_div
    self.robotics_based = robotics_based

    self.move_acc = 0
    self.target = None

  def GiveOrder(self, target):
    self.target = target

  def TryMove(self, game_state, dx, dy):
    x = self.pos.x + dx
    y = self.pos.y + dy
    if not game_state.Empty(x, y):
      return False
    if not self.can_fly and not game_state.world.LandAt(x, y):
      return False
    self.pos.x = x
    self.pos.y = y
    return True

  def ReachedTarget(self):
    pass

  def MoveOneStep(self, game_state):
    if not self.target:
      return
    dx = self.target[0] - self.pos.x
    dy = self.target[1] - self.pos.y

    if not dx and not dy:
      self.ReachedTarget()
      self.target = None
      return

    if dx and dy:
      if self.TryMove(game_state, misc.Sign(dx), misc.Sign(dy)):
        return
    if dx:
      if self.TryMove(game_state, misc.Sign(dx), 0):
        return
    if dy:
      if self.TryMove(game_state, 0, misc.Sign(dy)):
        return

    # Randomly try other directions to try to get unstuck.
    if dx and not dy:
      if random.randint(0, 1) == 0:
        if self.TryMove(game_state, misc.Sign(dx), 1):
          return
        self.TryMove(game_state, misc.Sign(dx), -1)
      else:
        if self.TryMove(game_state, misc.Sign(dx), -1):
          return
        self.TryMove(game_state, misc.Sign(dx), 1)
    else:
      if random.randint(0, 1) == 0:
        if self.TryMove(game_state, 1, misc.Sign(dy)):
          return
        self.TryMove(game_state, -1, misc.Sign(dy))
      else:
        if self.TryMove(game_state, -1, misc.Sign(dy)):
          return
        self.TryMove(game_state, 1, misc.Sign(dy))


  def EndOfTurnUpdate(self, game_state):
    if self.robotics_based:
      robo = game_state.research_level[game.Research.Robotics]
      self.move_div = 9 - robo
      self.strength = 1 + robo * 2
      self.max_health = 20 + 20 * robo
      if robo >= 4:
        self.can_fly = True

    self.move_acc += 1
    if self.move_acc > self.move_div:
      self.move_acc = 0
      self.MoveOneStep(game_state)

    for dy in xrange(-1, 2):
      for dx in xrange(-1, 2):
        if not dx and not dy:
          continue
        n = game_state.NodeAt(self.pos.x + dx, self.pos.y + dy)
        if not n:
          continue
        if n.owner == self.owner:
          continue
        n.health -= self.strength
        game_state.fighting = True
        game_state.AddExplosion(n, 0.5)


class Nuke(Unit):
  def __init__(self, pos, owner):
    super(Nuke, self).__init__(pos, owner, True, icons.Bomb, 10, 1)

  def ReachedTarget(self):
    # TODO: big explosion
    pass
