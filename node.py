import misc


class Node(object):
  def __init__(self, pos, owner):
    self.pos = pos
    self.control = False
    self.immune_until = 0
    self.owner = owner
    self.original_owner = owner
    self.size = 1

  def Flops(self):
    return 0

  def PopulationFlops(self):
    return 0

  def Captured(self, ai):
    self.owner = ai

  def Discovered(self):
    # TODO: notify somehow
    self.control = False
    self.owner = self.original_owner

  def EndOfTurnUpdate(self, game_state):
    pass

  def __attrrepr__(self):
    return ('pos=%r, control=%r, immune_until=%i'
            % (self.pos, self.control, self.immune_until))

  def __repr__(self):
    return ('%s(%s)' % (self.__class__.__name__, self.__attrrepr__()))
