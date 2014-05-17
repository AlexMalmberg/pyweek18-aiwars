import math
import pygame
from OpenGL import GL

import a_crack
import action
import dialog
import misc
import render_state
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
  def __init__(self, render, text, game_state):
    self.render = render
    self.text = text
    self.game_state = game_state
    self.world = self.game_state.world
    self.world_render = world_render.WorldRenderer(self.render, self.world)
    self.dialog = None
    self.animation_time = 0
    self.turn_time = 0
    self.turn_rate = 500.
    self.quit = False

    self.world_translate = [-1.6, -1.0]
    self.world_scale = 0.02

  def RenderHud(self):
    #
    # Need to display:
    #
    # Flops
    # Progress on current action
    # Raw materials
    # Date
    #
    # Active botnets
    # Active apps
    #

    flops = self.game_state.Flops()
    raw_material = self.game_state.raw_material

    self.text.DrawString(-1.55, 0.5, 0.05, (0.2, 1.0, 0.2, 1.0),
                          misc.FormatFlops(flops))
    self.text.DrawString(-1.55, 0.45, 0.05, (0.2, 1.0, 0.2, 1.0),
                          'Turn: %i' % self.game_state.turn)
    self.text.DrawString(-1.55, 0.40, 0.05, (0.2, 1.0, 0.2, 1.0),
                          'Action: %s' % self.game_state.current_action)
    if self.game_state.current_action:
      a = self.game_state.current_action
      self.text.DrawString(
        -1.55, 0.35, 0.05, (0.2, 1.0, 0.2, 1.0),
         'Progress: %s / %s'
         % (misc.FormatFlops(self.game_state.action_progress),
            misc.FormatFlops(self.game_state.action_cost)))
      if flops:
        self.text.DrawString(
          -1.55, 0.30, 0.05, (0.2, 1.0, 0.2, 1.0),
           '(%i turns left)'
           % ((self.game_state.action_cost - self.game_state.action_progress)
              / flops))

  def RenderNodes(self):
    GL.glBegin(GL.GL_QUADS)
    for n in self.game_state.nodes:
      x, y = n.pos.x, n.pos.y
      GL.glColor(1, 0, 0, 1)
      GL.glVertex(3 * x, 3 * y)
      GL.glVertex(3 * (x + 1), 3 * y)
      GL.glVertex(3 * (x + 1), 3 * (y + 1))
      GL.glVertex(3 * x, 3 * (y + 1))
    GL.glEnd()

  def RenderWorld(self):
    # TODO: scroll(/zoom?) the map + other stuff tied to map
    GL.glPushMatrix(GL.GL_MODELVIEW)
    GL.glTranslate(self.world_translate[0], self.world_translate[1], 0)
    GL.glScale(self.world_scale, self.world_scale, 1)

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

    self.text.DrawString(-1.6, -1.0, 0.05, (1, 1, 1, 1), str(clock))
    self.text.DrawString(-1.6, -0.95, 0.05, (1, 1, 1, 1),
                          '%i %5.3f' % (self.animation_time, self.turn_time))
    pygame.display.flip()

  def ScreenToWorld(self, x, y):
    x, y = self.render.ScreenToViewport(x, y)
    x = (x - self.world_translate[0]) / self.world_scale / 3.
    y = (y - self.world_translate[1]) / self.world_scale / 3.
    return x, y

  def NodeAt(self, x, y):
    for n in self.game_state.nodes:
      if n.pos.x == x and n.pos.y == y:
        return n
    return None

  def OpenDialogFor(self, n):
    d = dialog.Dialog(self.render, self.text, self)
    d.SetSize(0.6, 0.4)
    d.Center()
    d.AddElement(dialog.Text(0.3, 0.38, 0.04, (0, 0, 0, 1), True, 'Dialog'))
    d.AddElement(dialog.Button(
        0.1, 0.1, 0.4, 0.2, 0.1, self.CloseDialog, 'Crack!'))
    d.Ready()
    self.dialog = d

  def CloseDialog(self):
    self.dialog = None

  def HandleEvents(self, dt):
    for e in pygame.event.get():
      if e.type == pygame.QUIT:
        self.quit = True
        continue

      if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
        self.quit = True
        continue

      if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
        x, y = self.ScreenToWorld(*e.pos)
        print 'click at %5.2f %5.2f' % (x, y)

        fx, fy = int(math.floor(x)), int(math.floor(y))
        n = self.NodeAt(fx, fy)
        if n is not None:
          self.OpenDialogFor(n)
        continue

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
      self.world_translate[1] -= dt / 1000.
    if keys[pygame.K_DOWN]:
      self.world_translate[1] += dt / 1000.
    if keys[pygame.K_LEFT]:
      self.world_translate[0] += dt / 1000.
    if keys[pygame.K_RIGHT]:
      self.world_translate[0] -= dt / 1000.

    # TODO: only for debugging, disable? if not, need to fix
    # scale/translate order
    if keys[pygame.K_KP_PLUS]:
      self.world_scale *= math.exp(dt / 1000. * math.log(1.3))
    if keys[pygame.K_KP_MINUS]:
      self.world_scale /= math.exp(dt / 1000. * math.log(1.3))

  def Play(self):
    clock = pygame.time.Clock()

    GL.glEnable(GL.GL_BLEND)

    i = 0
    while not self.quit:
      dt = clock.tick()

      self.animation_time += dt

      if not self.dialog:
        self.turn_time += dt / self.turn_rate
        while self.turn_time > 1:
          self.game_state.AdvanceTurn()
          self.turn_time -= 1

      self.Render(clock)

      if self.dialog:
        self.dialog.HandleEvents(dt)
      else:
        self.HandleEvents(dt)
