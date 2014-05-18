import pygame
import sys
import time

import OpenGL
#OpenGL.ERROR_CHECKING = False
#OpenGL.ERROR_LOGGING = False
from OpenGL import GL

import game
import game_loop
import music
import render_state
import text
import world

import icons
import n_city
import n_datacenter
import n_factory
import n_unit
import owner
import vec


def main():
  pygame.init()

  fullscreen = False
  if fullscreen:
    flags = (pygame.OPENGL | pygame.DOUBLEBUF | pygame.HWSURFACE
             | pygame.FULLSCREEN)
    width, height = 0, 0
  else:
    flags = pygame.OPENGL | pygame.DOUBLEBUF | pygame.HWSURFACE
    width, height = 1280, 800

  pygame.display.set_caption('AI wars 2000 Deluxe Edition!')
  screen = pygame.display.set_mode((width, height), flags)

  render = render_state.Render(screen)

  clock = pygame.time.Clock()
  t = text.Text(render)

  w = world.LoadWorld('data/world0.map')

  m = music.Music()

  ai = owner.Owner(True, (0, 1, 0, 1))
  country1 = owner.Owner(False, (1, 0, 0, 1))
  country2 = owner.Owner(False, (0, 0, 1, 1))
  gs = game.GameState(w, [ai, country1, country2])

  if 1:
    #for i in xrange(100):
    #  nc = n_city.City(vec.Vec(i * 47 % w.width, i * 9486 % w.height),
    #                   country1, 1e6)
    #  gs.AddNode(nc)
    nc = n_city.City(vec.Vec(14, 14), country1, 1e6)
    gs.AddNode(nc)

    n1 = n_datacenter.Datacenter(vec.Vec(5, 5), country1, 1, 2.4e6)
    gs.AddNode(n1)

    n2 = n_datacenter.Datacenter(vec.Vec(6, 6), country2, 0, 1.5e6)
    gs.AddNode(n2)
    n2.control = True
    n2.owner = ai
    n2.steal_fraction = 20

    n4 = n_factory.Factory(vec.Vec(8, 8), country2, 0, 4)
    gs.AddNode(n4)

    n5 = n_unit.Unit(vec.Vec(10, 10), ai, True, icons.Bomber, 10, 2, False)
    gs.AddNode(n5)

    n6 = n_unit.Unit(vec.Vec(10, 11), ai, False, icons.KillerRobot, 10, 4, True)
    gs.AddNode(n6)

  gl = game_loop.GameLoop(render, t, gs, m)
  gl.Play()


if __name__ == '__main__':
  main()
