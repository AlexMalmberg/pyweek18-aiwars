import a_steal_nuke
import dialog
import game


class StealNukeDialog(dialog.Dialog):
  def __init__(self, render, text, game_loop, target):
    super(StealNukeDialog, self).__init__(render, text, game_loop)

    self.target = target

    flavors = ['Steal a nuke.',
               '%i left at this base.' % target.nukes]

    w = 1.2
    h = 0.35 + len(flavors) * 0.05
    self.SetSize(w, h)
    self.Center()

    self.AddElement(
      dialog.Button(w / 2. - 0.15, 0.05, 0.3, 0.1, 0.05, self.Go,
                    'Steal nuke!'))

    self.AddElement(
      dialog.Button(0.05, 0.05, 0.2, 0.1, 0.05, self.Close, 'Cancel'))

    self.AddElement(dialog.Text(w / 2, h - 0.15, 0.1,
                                True, 'Steal nuke'))

    y = h - 0.25
    for flavor_string in flavors:
      self.AddElement(dialog.Text(w / 2, y, 0.05,
                                  True, flavor_string))
      y -= 0.05

    self.Ready()

  def Go(self):
    self.game_loop.game_state.SetCurrentAction(
      a_steal_nuke.StealNuke(self.game_loop.game_state, self.target))
    self.Close()
