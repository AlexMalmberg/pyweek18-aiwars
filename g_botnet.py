import random

import g_base


NameParts = ['Quux', 'Foo', 'Zot']

def RandomBotnetName():
  return NameParts[random.randint(0, len(NameParts) - 1)] + 'Net'


class Botnet(g_base.Global):
  name = None

  def Description(self):
    if self.name is None:
      self.name = RandomBotnetName()
    return self.name
