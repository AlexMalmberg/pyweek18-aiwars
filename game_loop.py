import pygame
from OpenGL import GL

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
    self.turn_rate = 2000.
    self.quit = False

  def RenderHud(self):
    self.text.DrawString(-1.55, 0.5, 0.05, (0.2, 1.0, 0.2, 1.0),
                          misc.FormatFlops(self.game_state.Flops()))
    self.text.DrawString(-1.55, 0.45, 0.05, (0.2, 1.0, 0.2, 1.0),
                          'Turn: %i' % self.game_state.turn)
    self.text.DrawString(-1.55, 0.40, 0.05, (0.2, 1.0, 0.2, 1.0),
                          'Action: %s' % self.game_state.current_action)

  def RenderWorld(self):
    # TODO: scroll(/zoom?) the map + other stuff tied to map
    GL.glPushMatrix(GL.GL_MODELVIEW)
    GL.glTranslate(-0.8, -0.8, 0)
    GL.glScale(0.03, 0.03, 1)

    self.world_render.Draw()
    # TODO: Draw nodes.
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

  def Play(self):
    clock = pygame.time.Clock()

    GL.glEnable(GL.GL_BLEND)

    i = 0
    while not self.quit:
      dt = clock.tick()

      self.animation_time += dt
      self.turn_time += dt / self.turn_rate
      while self.turn_time > 1:
        self.game_state.AdvanceTurn()
        self.turn_time -= 1

      self.Render(clock)

      for e in pygame.event.get():
        if (e.type == pygame.QUIT
            or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE)):
          self.quit = True
        print e
