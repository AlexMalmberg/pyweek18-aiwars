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

  def RenderHud(self):
    self.text.DrawString(-1.55, 0.5, 0.05, (0.2, 1.0, 0.2, 1.0),
                          misc.FormatFlops(self.game_state.Flops()))
    self.text.DrawString(-1.55, 0.45, 0.05, (0.2, 1.0, 0.2, 1.0),
                          'Turn: %i' % self.game_state.turn)
    self.text.DrawString(-1.55, 0.40, 0.05, (0.2, 1.0, 0.2, 1.0),
                          'Action: %s' % self.game_state.current_action)

  def Play(self):
    clock = pygame.time.Clock()

    GL.glEnable(GL.GL_BLEND)

    i = 0
    while True:
      clock.tick()
      GL.glClear(GL.GL_COLOR_BUFFER_BIT)

      # TODO: scroll(/zoom?) the map + other stuff tied to map
      self.world_render.Draw()
      # TODO: Draw nodes.
      # TODO: Draw units + unit effects.

      self.RenderHud()

      if self.dialog:
        self.dialog.Render()

      self.text.DrawString(-1.6, -1.0, 0.05, (1, 1, 1, 1), str(clock))

      pygame.display.flip()
      i += 1
      if i == 1000:
        break
