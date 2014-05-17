import dialog
import game


class ResearchDialog(dialog.Dialog):
  def __init__(self, render, text, game_loop):
    super(ResearchDialog, self).__init__(render, text, game_loop)
    self.SetSize(1.8, 0.8)
    self.Center()

    self.AddElement(
      dialog.Button(0.05, 0.05, 0.2, 0.1, 0.05, self.Close, 'Cancel'))
    self.AddElement(
      dialog.Button(0.75, 0.05, 0.2, 0.1, 0.05, self.Go, 'Go!'))

    self.tech_icon = []
    for i in xrange(game.Research.Num):
      ti = dialog.Icon(
        0.05 + i * 0.35, 0.35, 0.3, 0.3,
        (lambda j: lambda: self.SelectTech(j))(i),
        self.render.tech_icon[i])
      self.tech_icon.append(ti)
      self.AddElement(ti)

    self.current_tech = 0
    self.tech_icon[self.current_tech].SetHighlight(True)

    self.Ready()

  def SelectTech(self, i):
    self.tech_icon[self.current_tech].SetHighlight(False)
    self.current_tech = i
    self.tech_icon[self.current_tech].SetHighlight(True)

  def Go(self):
    print 'start research of %i' % self.current_tech
    self.Close()
