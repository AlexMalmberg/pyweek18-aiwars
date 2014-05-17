import random

import g_base


NamePart1 = ['Angry', 'Upset', 'Funny', 'Bloppy']
NamePart2 = ['Rhinos', 'Hippos', 'Giraffes', 'Zebras']

def RandomAppName():
  return (NamePart1[random.randint(0, len(NamePart1) - 1)]
          + ' '
          + NamePart2[random.randint(0, len(NamePart2) - 1)])


class App(g_base.Global):
  name = None

  def Description(self):
    if self.name is None:
      self.name = RandomAppName()
    return self.name
