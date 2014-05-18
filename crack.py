import dialog
import game
import render_state


class CrackDialog(dialog.Dialog):
  def __init__(self, render, text, game_loop, act):
    super(CrackDialog, self).__init__(render, text, game_loop)
    self.act = act

    n = act.node
    flavors = ['Cracking into a',
               '%s.' % n.Description()]

    w = 1.2
    h = 0.55 + len(flavors) * 0.05
    self.SetSize(w, h)
    self.Center()

    self.AddElement(
      dialog.Button(0.05, 0.05, 0.2, 0.1, 0.05, self.Close, 'Cancel'))
    self.AddElement(
      dialog.Button(w / 2 - 0.1, 0.05, 0.2, 0.1, 0.05, self.Go, 'Go!'))

    self.AddElement(dialog.Text(w / 2, h - 0.15, 0.1,
                                True, 'Cracking'))

    y = h - 0.25
    for flavor_string in flavors:
      self.AddElement(dialog.Text(w / 2, y, 0.05,
                                  True, flavor_string))
      y -= 0.05

    attack_string = (
      'Using %i-bit cracking.'
      % (1 + self.game_loop.game_state.research_level[game.Research.Cracking]))
    self.AddElement(dialog.Text(w / 2, y, 0.05,
                                True, attack_string))
    y -= 0.1

    flops = self.game_loop.game_state.Flops()
    if flops:
      h = round(self.act.Cost() / flops)
      cost_string = 'Cracking will take %i hours.' % h
    else:
      cost_string = 'Cracking will take forever.'
    self.AddElement(dialog.Text(w / 2, y, 0.05,
                                True, cost_string))

    self.Ready()

  def Go(self):
    self.game_loop.game_state.SetCurrentAction(self.act)
    self.Close()
