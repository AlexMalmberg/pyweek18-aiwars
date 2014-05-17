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
    'Allows you to incite riots and control the population.',
    'Makes your actions harder for humans to discover.',
    'Improves the fighting strength of your robot armies.',
    'Increases computing capacity and human/computer interfaces.']


class GameState(object):
  def __init__(self, world):
    self.world = world
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

  def AddNode(self, node):
    self.nodes.append(node)

  def AddGlobal(self, g):
    self.glbls.append(g)

  def SetCurrentAction(self, action):
    self.current_action = action
    self.action_cost = action.Cost()
    self.action_progress = 0

  def AdvanceTurn(self):
    self.turn += 1
    if self.current_action:
      self.action_progress += self.Flops()
      if self.action_progress > self.action_cost:
        self.current_action.Execute()
        self.current_action = None

    for n in self.nodes:
      n.EndOfTurnUpdate(self)

    for g in self.glbls:
      g.EndOfTurnUpdate(self)

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
