import math
import pygame
from OpenGL import GL

import a_crack
import action
import crack
import create
import dialog
import game
import misc
import n_datacenter
import n_factory
import node_render
import render_state
import research
import text
import world
import world_render


# On-screen elements, ordered by layer:
#  Scrolls with map:
#   Map
#   Nodes
#    Labels for some nodes
#   Units
#   Unit effects
#  Hud:
#   Gigaflops counter
#   Turn/time indicator
#   Current in-progress flop-action
#  Dialog:
#   Darken everything
#   Currently active dialog
#
# Parameters:
#  game_state:
#    with current turn and next turn positions for units
#  game time:
#    0 - 1, fraction between previous and next turn, tied to game
#    speed/simulation speed
#  animation time:
#    always advances with real-time


class GameLoop(object):
  def __init__(self, render, text, game_state, music):
    self.render = render
    self.text = text
    self.game_state = game_state
    self.music = music

    self.world = self.game_state.world
    self.world_render = world_render.WorldRenderer(self.render, self.world)
    self.node_render = node_render.NodeRenderer(self.render, self.game_state)
    self.dialog = None
    self.animation_time = 0
    self.turn_time = 0
    self.turn_rate = 200.
    self.quit = False

    self.world_translate = [-self.world.width * 3. / 2.,
                            -self.world.height * 3. / 2.]
    self.world_scale = 0.02

    self.button_pressed = False
    self.active_element = None
    self.active_node = None
    self.active_unit = None

    self.PrepareHud()

  def PrepareHud(self):
    self.research_button = dialog.Button(
      -1.55, -0.95, 0.4, 0.1, 0.05,
      self.OpenResearchDialog, 'Research')

    self.botnet_button = dialog.Button(
      1.15, -0.95, 0.2, 0.1, 0.05,
      self.OpenBotnetDialog, 'Botnet')

    self.app_button = dialog.Button(
      1.4, -0.95, 0.15, 0.1, 0.05,
      self.OpenAppDialog, 'App')

    self.elements = [self.research_button, self.botnet_button, self.app_button]

  def RenderHud(self):
    # Center: Turn/date, flops, resources, current action
    self.RenderHudCenter()

    # Left: Techs + research button
    self.RenderHudTech()

    # Right: Botnets + apps
    self.RenderHudGlobals()

    for e in self.elements:
      if e == self.active_element:
        if self.button_pressed:
          a = 2
        else:
          a = 1
      else:
        a = 0
      e.Render(self.render, self.text, a)

  def RenderHudGlobals(self):
    w = 0.5
    h = 0.25 + len(self.game_state.glbls) * 0.05
    r = 1.6
    l = r - w
    b = -1.0
    t = b + h

    self.render.DrawSolidBoxWithBorder(l, b, w, h, 0.01)

    for i, g in enumerate(self.game_state.glbls):
      self.text.DrawString(l + 0.05, t - 0.1 - 0.05 * i, 0.05,
                           render_state.Black,
                           g.Description())

  def RenderHudTech(self):
    w = 0.5
    h = 0.475
    l = -1.6
    r = l + w
    b = -1.0
    t = b + h

    self.render.DrawSolidBoxWithBorder(l, b, w, h, 0.01)

    for i in xrange(game.Research.Num):
      self.text.DrawString(l + 0.05, t - 0.1 - 0.05 * i, 0.05,
                           render_state.Black,
                           '%i-bit' % (self.game_state.research_level[i] + 1))
      self.text.DrawString(l + 0.18, t - 0.1 - 0.05 * i, 0.05,
                           render_state.Black,
                           game.Research.Names[i])

  def RenderHudCenter(self):
    flops = self.game_state.Flops()

    w = 1.0
    h = 0.35
    l = -w / 2
    r = l + w
    b = -1.0
    t = b + h

    self.render.DrawSolidBoxWithBorder(l, b, w, h, 0.01)

    # TODO: slowly morph this towards unix epoch timestamp
    self.text.DrawString(l + 0.05, t - 0.1, 0.05, render_state.Black,
                         misc.TurnToDate(self.game_state.turn))

    self.text.DrawString(r - 0.05, t - 0.1, 0.05, render_state.Black,
                          misc.FormatFlops(flops),
                          right=True)

    if self.game_state.current_action:
      self.text.DrawString((l + r) / 2, t - 0.19, 0.05, render_state.Black,
                           self.game_state.current_action.Description(),
                           center=True)
      progress = (self.game_state.action_progress
                  / float(self.game_state.action_cost))
      self.render.DrawProgressBar(
        (l + r) / 2 - w * 0.4,
        b + 0.05,
        w * 0.8,
        0.1,
        progress)
    else:
      self.text.DrawString((l + r) / 2, t - 0.25, 0.05, render_state.Black,
                          'Idle', center=True)

  def RenderNodes(self):
    self.node_render.Render()

  def RenderWorld(self):
    GL.glPushMatrix()
    GL.glScale(self.world_scale, self.world_scale, 1)
    GL.glTranslate(self.world_translate[0], self.world_translate[1], 0)

    self.world_render.Draw()
    self.RenderNodes()
    # TODO: Draw units + unit effects.

    GL.glPopMatrix(GL.GL_MODELVIEW)

  def Render(self, clock):
    GL.glClear(GL.GL_COLOR_BUFFER_BIT)

    self.RenderWorld()

    self.RenderHud()

    if self.dialog:
      self.dialog.Render()

    self.text.DrawString(-1.6, 0.95, 0.05, (1, 1, 1, 1), str(clock))
    self.text.DrawString(-1.6, 0.90, 0.05, (1, 1, 1, 1),
                          '%i %5.3f' % (self.animation_time, self.turn_time))
    pygame.display.flip()

  def ScreenToWorld(self, x, y):
    x, y = self.render.ScreenToViewport(x, y)
    x = x / self.world_scale - self.world_translate[0]
    y = y / self.world_scale - self.world_translate[1]
    return x / 3., y / 3.

  def NodeAt(self, x, y):
    for n in self.game_state.nodes:
      if n.pos.x == x and n.pos.y == y:
        return n
    return None

  def UnitAt(self, x, y):
    return None

  def OpenResearchDialog(self):
    self.dialog = research.ResearchDialog(self.render, self.text, self)

  def OpenBotnetDialog(self):
    self.dialog = create.CreateBotnetDialog(
      self.render, self.text, self)

  def OpenAppDialog(self):
    self.dialog = create.CreateAppDialog(
      self.render, self.text, self)

  def OpenDialogFor(self, n):
    if isinstance(n, (n_factory.Factory, n_datacenter.Datacenter)):
      try:
        act = a_crack.Crack(self.game_state, n)
        self.dialog = crack.CrackDialog(self.render, self.text, self, act)
      except action.ImpossibleAction:
        pass  # TODO: sound effect

  def CloseDialog(self):
    self.dialog = None

  def ElementAt(self, x, y):
    for e in self.elements:
      ar = e.active_region
      if not ar:
        continue
      if misc.Inside(x, y, ar):
        return e
    return None

  def HandleEvents(self, dt):
    for e in pygame.event.get():
      if e.type == pygame.QUIT:
        self.quit = True
        continue

      if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
        self.quit = True
        continue

      if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
        x, y = self.render.ScreenToViewport(*e.pos)
        wx, wy = self.ScreenToWorld(*e.pos)
        fx, fy = int(math.floor(wx)), int(math.floor(wy))

        # First check UI elements.
        self.active_node = self.active_unit = None
        self.active_element = self.ElementAt(x, y)
        if self.active_element:
          self.active_element.Clicked(x, y)
          self.button_pressed = True
          continue

        # TODO: check units
        u = self.UnitAt(fx, fy)
        if u:
          self.active_unit = u
          self.button_pressed = True
          continue

        # Finally nodes.
        n = self.NodeAt(fx, fy)
        if n is not None:
          self.OpenDialogFor(n)
        continue

      if e.type == pygame.MOUSEMOTION:
        x, y = self.render.ScreenToViewport(*e.pos)
        wx, wy = self.ScreenToWorld(*e.pos)
        fx, fy = int(math.floor(wx)), int(math.floor(wy))
        if self.button_pressed:
          if self.active_element:
            self.active_element.Dragged(x, y)
          elif self.active_node:
            # Dragging nodes does nothing, and we shouldn't end up
            # here, anyway.
            pass
          elif self.active_unit:
            pass  # TODO: update in-flight order with arrow
        else:
          # For highlighting mouse-over'd stuff.
          self.active_node = self.active_unit = None
          self.active_element = self.ElementAt(x, y)
          if not self.active_element:
            self.active_node = self.NodeAt(fx, fy)
            if not self.active_node:
              self.active_unit = self.UnitAt(fx, fy)
        continue

      if e.type == pygame.MOUSEBUTTONUP and e.button == 1:
        x, y = self.render.ScreenToViewport(*e.pos)
        wx, wy = self.ScreenToWorld(*e.pos)
        fx, fy = int(math.floor(wx)), int(math.floor(wy))

        self.button_pressed = False
        if self.active_element:
          self.active_element.Unclicked(x, y)
        elif self.active_node:
          # Nodes do nothing when dragged.
          pass
        elif self.active_unit:
          pass  # TODO: issue order
        continue

    # Next, check for scroll keys.
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
      self.world_translate[1] -= dt / 1000. * 30.
    if keys[pygame.K_DOWN]:
      self.world_translate[1] += dt / 1000. * 30.
    if keys[pygame.K_LEFT]:
      self.world_translate[0] += dt / 1000. * 30.
    if keys[pygame.K_RIGHT]:
      self.world_translate[0] -= dt / 1000. * 30.

    if keys[pygame.K_KP_PLUS]:
      self.world_scale *= math.exp(dt / 1000. * math.log(1.6))
    if keys[pygame.K_KP_MINUS]:
      self.world_scale /= math.exp(dt / 1000. * math.log(1.6))

  def Play(self):
    clock = pygame.time.Clock()
    self.music.Play()

    GL.glEnable(GL.GL_BLEND)

    while not self.quit:
      self.music.Update()
      dt = clock.tick()

      self.animation_time += dt

      # Wrap animation at 1h to avoid overflows and stuff.
      self.animation_time %= 1000 * 3600

      if not self.dialog:
        self.turn_time += dt / self.turn_rate
        while self.turn_time > 1:
          self.game_state.AdvanceTurn()
          self.node_render.Update(self.game_state)
          self.turn_time -= 1

      self.render.animation_time = self.animation_time / 1000.
      self.turn_time = self.turn_time

      self.Render(clock)

      if self.dialog:
        self.dialog.HandleEvents(dt)
      else:
        self.HandleEvents(dt)
