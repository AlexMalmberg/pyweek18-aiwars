import math


import misc


class Research(object):
  Cracking = 0
  Psychology = 1
  Crypto = 2
  Robotics = 3
  Nanotech = 4
  Num = 5

  MaxLevel = 7

  Names = ['Cracking', 'Psychology', 'Crypto', 'Robotics', 'Nanotech']
  IconNames = ['cracking', 'psych', 'crypto', 'robo', 'nano']

  FlavorTexts = [
    'Makes it easier to take control of factories and data centers.',
    'Allows you to incite riots and game social media to control humans.',
    'Makes your actions harder for humans to discover.',
    'Increases the fighting strength of your robot armies.',
    'Improves human/computer interfaces and computing capacity.']


class GameState(object):
  def __init__(self, world, owners):
    self.world = world
    self.owners = owners
    self.ai_owner = owners[0]
    self.nodes = []
    self.glbls = []
    self.research_level = [0] * Research.Num
    self.human_level = [0] * Research.Num
    self.human_paranoia_level = 0

    # Each turn is 1 hour.
    self.turn = 0
    self.raw_material = 0

    self.current_action = None
    self.action_progress = 0
    self.action_cost = 0

    self.fighting = False
    self.explosions = []

  def AddNode(self, node):
    self.nodes.append(node)

  def AddGlobal(self, g):
    self.glbls.append(g)

  def RemoveGlobal(self, g):
    self.glbls.remove(g)

  def SetCurrentAction(self, action):
    self.current_action = action
    self.action_cost = action.Cost()
    self.action_progress = 0

  def AdvanceTurn(self):
    self.turn += 1
    self.fighting = False
    self.explosions = []
    if self.current_action:
      self.action_progress += self.Flops()
      if self.action_progress > self.action_cost:
        self.current_action.Execute()
        self.current_action = None

    for n in self.nodes:
      n.EndOfTurnUpdate(self)

    for g in self.glbls:
      g.EndOfTurnUpdate(self)

    # Clear out dead nodes.
    nnodes = []
    for n in self.nodes:
      if n.health > 0:
        nnodes.append(n)
        # Slowly regen health when not attacked.
        n.health += 1
        if n.health > n.max_health:
          n.health = n.max_health
      else:
        self.AddExplosion(n, 1.0)

    self.nodes = nnodes

  def PopulationFlops(self):
    pop_flops = 0
    for n in self.nodes:
      pop_flops += n.PopulationFlops()
    return pop_flops

  def Flops(self):
    flops = 0
    for n in self.nodes:
      flops += n.Flops()
    for g in self.glbls:
      flops += g.Flops(self)
    return flops

  def GiveRawMaterial(self, amount):
    self.raw_material += int(amount)

  def Print(self):
    print('== GameState %r' % self)
    print('Turn %i' % self.turn)
    print('Raw material: %i' % self.raw_material)
    flops = self.Flops()
    print('Current flops: %s' % misc.FormatFlops(flops))
    if self.current_action:
      print('= Action: %r' % self.current_action)
      print('Progress: %s / %s' % (misc.FormatFlops(self.action_progress),
                                   misc.FormatFlops(self.action_cost)))
      if flops:
        print(('(%i turns left)'
               % ((self.action_cost - self.action_progress) / flops)))
    print('= Research:')
    for i in xrange(Research.Num):
      print('%10s: %i' % (Research.Names[i], self.research_level[i]))
    print('= Humans:')
    for i in xrange(Research.Num):
      print('%10s: %i' % (Research.Names[i], self.human_level[i]))
    print('Paranoia level: %i' % self.human_paranoia_level)
    print('= Nodes:')
    for n in self.nodes:
      print('%r' % n)
    print('= Globals:')
    for n in self.glbls:
      print('%r' % n)

  def NodeAt(self, x, y):
    for n in self.nodes:
      if (x >= n.pos.x
          and y >= n.pos.y
          and x < n.pos.x + n.size
          and y < n.pos.y + n.size):
        return n
    return None

  def Empty(self, x, y):
    return self.NodeAt(x, y) is None

  def AddExplosion(self, n, size):
    size *= n.size / 2.
    self.explosions.append((n.pos.x + n.size / 2., n.pos.y + n.size / 2., size))

  def EmptySquareNear(self, x, y):
    for dy in xrange(-1, 2):
      for dx in xrange(-1, 2):
        if not dx and not dy:
          continue
        tx = x + dx
        ty = y + dy
        if not self.Empty(tx, ty):
          continue
        if not self.world.LandAt(tx, ty):
          continue
        return (tx, ty)
    return None
