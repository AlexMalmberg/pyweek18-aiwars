import a_riot
import dialog
import game


class CityDialog(dialog.Dialog):
  def __init__(self, render, text, game_loop, target):
    super(CityDialog, self).__init__(render, text, game_loop)

    self.target = target

    flavors = []

    psych = game_loop.game_state.research_level[game.Research.Psychology]
    self.psych = psych
    nano = game_loop.game_state.research_level[game.Research.Nanotech]
    self.nano = nano

    riot_strength = [
      'very weak',
      'somewhat weak',
      'weak',
      'ok-ish',
      'somewhat strong',
      'strong',
      'very strong',
      'insanely strong']
    flavors += ['You can use social media to start',
                'flamewars and incite a riot. Using',
                '%i-bit psychology, your riot' % (psych + 1),
                'will be %s.' % riot_strength[psych]]
    self.AddElement(
      dialog.Button(0.35, 0.05, 0.2, 0.1, 0.05, self.Riot, 'Riot!'))

    flavors += ['']

    c_nano = target.nanotech_level
    if c_nano == 7:
      flavors += ['City already fully mind-uploaded.']
    elif c_nano == nano:
      flavors += ['Research more nanotech to upload more minds.']
    else:
      flavor_nano = [
        'shouldn\'t happen'
        'cell phones',
        'smart-phones',
        'tablets',
        'wearable computers',
        'spine implants',
        'brain implants',
        'mind uploading']
      target_nano = c_nano + 1
      self.target_nano = target_nano
      flavors += ['Or you can start uploading the',
                  'population\'s minds using awesome',
                  '%i-bit %s.' % ((target_nano + 1), flavor_nano[target_nano])]
      self.AddElement(
        dialog.Button(0.65, 0.05, 0.5, 0.1, 0.05, self.Nanotech,
                      'Upload population!'))

    w = 1.2
    h = 0.35 + len(flavors) * 0.05
    self.SetSize(w, h)
    self.Center()

    self.AddElement(
      dialog.Button(0.05, 0.05, 0.2, 0.1, 0.05, self.Close, 'Cancel'))

    self.AddElement(dialog.Text(w / 2, h - 0.15, 0.1,
                                True, 'Cracking'))

    y = h - 0.25
    for flavor_string in flavors:
      self.AddElement(dialog.Text(w / 2, y, 0.05,
                                  True, flavor_string))
      y -= 0.05

    self.Ready()

  def Riot(self):
    self.game_loop.game_state.SetCurrentAction(
      a_riot.Riot(self.game_loop.game_state, self.target))
    self.Close()

  def Nanotech(self):
    self.game_loop.game_state.SetCurrentAction(
      a_upload.Upload(self.game_loop.game_state, self.target_nano, self.target))
    self.Close()
