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
import n_military
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
    nc = n_city.City(vec.Vec(15, 15), country1, 1e6)
    gs.AddNode(nc)

    n1 = n_datacenter.Datacenter(vec.Vec(5, 5), country1, 1, 2.4e6)
    gs.AddNode(n1)

    n2 = n_datacenter.Datacenter(vec.Vec(6, 6), country2, 0, 1.5e6)
    gs.AddNode(n2)
    n2.control = True
    n2.owner = ai

    n4 = n_factory.Factory(vec.Vec(8, 8), country2, 0, 4)
    gs.AddNode(n4)

    nf = n_factory.Factory(vec.Vec(50, 8), country2, 0, 4)
    gs.AddNode(nf)

    nf2 = n_factory.Factory(vec.Vec(55, 3), country2, 1, 15)
    gs.AddNode(nf2)

    nf3 = n_factory.Factory(vec.Vec(48, 22), country2, 1, 15)
    gs.AddNode(nf3)

    n6 = n_datacenter.Datacenter(vec.Vec(50, 6), country2, 1, 3e6)
    gs.AddNode(n6)

    n7 = n_datacenter.Datacenter(vec.Vec(38, 8), country2, 0, 0.5e6)
    gs.AddNode(n7)

    n8 = n_datacenter.Datacenter(vec.Vec(50, 20), country2, 0, 0.5e6)
    gs.AddNode(n8)

    n9 = n_datacenter.Datacenter(vec.Vec(58, 10), country2, 0, 5e6)
    gs.AddNode(n9)

    nc2 = n_city.City(vec.Vec(38, 3), country2, 1e6)
    gs.AddNode(nc2)

    nc3 = n_city.City(vec.Vec(40, 13), country2, 2e6)
    gs.AddNode(nc3)

    nc4 = n_city.City(vec.Vec(58, 12), country2, 5e6)
    gs.AddNode(nc4)

    nc5 = n_city.City(vec.Vec(20, 3), country1, 0.5e6)
    gs.AddNode(nc5)

    nc6 = n_city.City(vec.Vec(3, 2), country1, 3e6)
    gs.AddNode(nc6)

    nm1 = n_military.Military(vec.Vec(7, 5), country1, 0, 4)
    gs.AddNode(nm1)


    n9 = n_datacenter.Datacenter(vec.Vec(22, 13), country1, 0, 0.5e6)
    gs.AddNode(n9)

    n10 = n_datacenter.Datacenter(vec.Vec(20, 8), country1, 0, 0.5e6)
    gs.AddNode(n10)

    unit = n_unit.Unit(vec.Vec(4, 5), country1, False,
                       icons.Tank, 10, 200, 2, False)
    gs.AddNode(unit)
    unit = n_unit.Unit(vec.Vec(4, 4), country1, False,
                       icons.Tank, 10, 200, 2, False)
    gs.AddNode(unit)
    unit = n_unit.Unit(vec.Vec(15, 15), country1, False,
                       icons.Tank, 10, 200, 2, False)
    gs.AddNode(unit)

    unit = n_unit.Unit(vec.Vec(49, 20), country2, False,
                       icons.Tank, 10, 200, 2, False)
    gs.AddNode(unit)
    unit = n_unit.Unit(vec.Vec(50, 19), country2, False,
                       icons.Tank, 10, 200, 2, False)
    gs.AddNode(unit)
    unit = n_unit.Unit(vec.Vec(51, 19), country2, False,
                       icons.Tank, 10, 200, 2, False)
    gs.AddNode(unit)

  gl = game_loop.GameLoop(render, t, gs, m)
  gl.Play()


if __name__ == '__main__':
  main()
