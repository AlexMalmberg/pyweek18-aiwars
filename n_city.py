import node


class City(node.Node):
  def __init__(self, pos, population):
    super(City, self).__init__(pos)
    self.population = population
    self.nanotech_level = 0

  def PopulationFlops(self):
    # TODO: tune
    return self.population * (1 + self.nanotech_level ** 2)

  def Flops(self):
    # TODO: grant flops when nanotech level high
    return 0

  def EndOfTurnUpdate(self, game_state):
    # TODO: chance to riot
    pass

  def __attrrepr__(self):
    return (super(City, self).__attrrepr__()
            + (', population=%i, nanotech=%i'
               % (self.population, self.nanotech_level)))
