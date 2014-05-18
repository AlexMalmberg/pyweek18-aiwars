import action
import a_app
import a_botnet
import dialog
import game
import render_state


class CreateDialog(dialog.Dialog):
  def __init__(self, render, text, game_loop, act, title, flavors):
    super(CreateDialog, self).__init__(render, text, game_loop)
    self.act = act
    w = 1.2
    h = 0.5 + len(flavors) * 0.05
    self.SetSize(w, h)
    self.Center()

    self.AddElement(
      dialog.Button(0.05, 0.05, 0.2, 0.1, 0.05, self.Close, 'Cancel'))
    self.AddElement(
      dialog.Button(w / 2 - 0.1, 0.05, 0.2, 0.1, 0.05, self.Go, 'Go!'))

    self.AddElement(dialog.Text(w / 2, h - 0.15, 0.1,
                                True, title))

    y = h - 0.25
    for flavor_string in flavors:
      self.AddElement(dialog.Text(w / 2, y, 0.05,
                                  True, flavor_string))
      y -= 0.05

    hide_string = (
      'Using %i-bit crypto to hide.'
      % (1 + self.game_loop.game_state.research_level[game.Research.Crypto]))
    self.AddElement(dialog.Text(w / 2, y, 0.05,
                                True, hide_string))
    y -= 0.1

    flops = self.game_loop.game_state.Flops()
    if flops:
      h = round(self.act.Cost() / flops)
      cost_string = 'Creating will take %i hours.' % h
    else:
      cost_string = 'Creating will take forever.'
    self.AddElement(dialog.Text(w / 2, y, 0.05,
                                True, cost_string))

    self.Ready()

  def Go(self):
    self.game_loop.game_state.SetCurrentAction(self.act)
    self.Close()


class CreateBotnetDialog(CreateDialog):
  def __init__(self, render, text, game_loop):
    act = a_botnet.CreateBotnet(game_loop.game_state)
    super(CreateBotnetDialog, self).__init__(
      render, text, game_loop,
      act,
      'Create botnet',
      ['Create a botnet that steals cycles from',
       'computers across the world.',
       ('Using %i-bit cracking to attack,'
        % (act.AttackLevel() + 1)),
       ('will reach %.0f%% of computers.' % (act.Spread() / 10.))])


class CreateAppDialog(CreateDialog):
  def __init__(self, render, text, game_loop):
    act = a_app.CreateApp(game_loop.game_state)
    super(CreateAppDialog, self).__init__(
      render, text, game_loop,
      act,
      'Create app',
      ['Create an app that steals cycles from',
       'cell phones across the world.',
       ('Using %i-bit psychology to attack,'
        % (game_loop.game_state.research_level[game.Research.Psychology] + 1)),
       ('will reach %.0f%% of humans.'
        % (act.Spread() / 10.))])
