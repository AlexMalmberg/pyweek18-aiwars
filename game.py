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


class GameState(object):
  def __init__(self):
    self.nodes = []
    self.research_level = [0] * Research.Num
    self.turn = 0
    self.unspent_flops = 0
    self.spent_flops = 0

  def AddNode(self, node):
    self.nodes.append(node)

  def StartTurn(self):
    flops = 0
    for n in self.nodes:
      flops += n.ControlledFlops()
    self.unspent_flops += flops
    self.spent_flops = 0

  def EndTurn(self):
    self.turn += 1

  def ExecuteAction(self, action):
    cost = action.Cost()
    self.spent_flops = self.spent_flops + cost
    self.unspent_flops = self.unspent_flops - cost
    action.Execute()

  def Print(self):
    print '== GameState %r' % self
    print 'Turn %i' % self.turn
    print 'Unspent flops: %s' % misc.FormatFlops(self.unspent_flops)
    print '  Spent flops: %s' % misc.FormatFlops(self.spent_flops)
    print '= Research:'
    for i in xrange(Research.Num):
      print '%10s: %i' % (Research.Names[i], self.research_level[i])
    print '= Nodes:'
    for n in self.nodes:
      print '%r' % n
