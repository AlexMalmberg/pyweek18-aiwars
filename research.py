import action
import a_research
import dialog
import game
import render_state


class ResearchDialog(dialog.Dialog):
  def __init__(self, render, text, game_loop):
    super(ResearchDialog, self).__init__(render, text, game_loop)
    w = 1.8
    self.SetSize(w, 0.8)
    self.Center()

    self.AddElement(
      dialog.Button(0.05, 0.05, 0.2, 0.1, 0.05, self.Close, 'Cancel'))
    self.AddElement(
      dialog.Button(w / 2 - 0.1, 0.05, 0.2, 0.1, 0.05, self.Go, 'Go!'))

    self.tech_icon = []
    for i in xrange(game.Research.Num):
      ti = dialog.Icon(
        0.05 + i * 0.35, 0.45, 0.3, 0.3,
        (lambda j: lambda: self.SelectTech(j))(i),
        self.render.tech_icon[i])
      self.tech_icon.append(ti)
      self.AddElement(ti)

    self.current_tech = 0
    self.tech_icon[self.current_tech].SetHighlight(True)

    self.title_text = dialog.Text(w / 2, 0.30, 0.1,
                                   True, 'title')
    self.AddElement(self.title_text)

    self.flavor_text = dialog.Text(w / 2, 0.23, 0.05,
                                   True, 'flavor')
    self.AddElement(self.flavor_text)

    self.cost_text = dialog.Text(w / 2, 0.18, 0.05,
                                 True, 'cost')
    self.AddElement(self.cost_text)

    self.UpdateText()

    self.Ready()

  def UpdateText(self):
    self.title_text.msg = game.Research.Names[self.current_tech]
    self.flavor_text.msg = game.Research.FlavorTexts[self.current_tech]
    level = self.game_loop.game_state.research_level[self.current_tech]
    try:
      a = a_research.Research(self.game_loop.game_state, self.current_tech)
      flops = self.game_loop.game_state.Flops()
      if flops:
        h = round(a.Cost() / flops)
        self.cost_text.msg = (
          'Upgrading to %i bits will take %i hours.'
          % (level + 2, h))
      else:
        self.cost_text.msg = (
          'Upgrading to %i bits will take forever.'
          % (level + 2))
    except action.ImpossibleAction:
      self.cost_text.msg = 'Already at the highest level.'

  def SelectTech(self, i):
    self.tech_icon[self.current_tech].SetHighlight(False)
    self.current_tech = i
    self.tech_icon[self.current_tech].SetHighlight(True)
    self.UpdateText()

  def Go(self):
    try:
      a = a_research.Research(self.game_loop.game_state, self.current_tech)
      self.game_loop.game_state.SetCurrentAction(a)
    except action.ImpossibleAction:
      pass
    self.Close()
