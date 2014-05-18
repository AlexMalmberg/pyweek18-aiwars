import pygame
import sys
import time

import OpenGL
#OpenGL.ERROR_CHECKING = False
#OpenGL.ERROR_LOGGING = False
from OpenGL import GL

import game
import game_loop
import render_state
import text
import world

import n_city
import n_datacenter
import n_factory
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

  gs = game.GameState(w)

  if 1:
    #for i in xrange(100):
    #  nc = n_city.City(vec.Vec(i * 47 % w.width, i * 9486 % w.height), 1e6)
    #  gs.AddNode(nc)
    nc = n_city.City(vec.Vec(15, 15), 1e6)
    gs.AddNode(nc)

    n1 = n_datacenter.Datacenter(vec.Vec(5, 5), 1, 2.4e6)
    gs.AddNode(n1)

    n2 = n_datacenter.Datacenter(vec.Vec(6, 6), 0, 1.5e6)
    gs.AddNode(n2)
    n2.control = True
    n2.steal_fraction = 20

    n4 = n_factory.Factory(vec.Vec(8, 8), 0, 4)
    gs.AddNode(n4)

  gl = game_loop.GameLoop(render, t, gs)
  gl.Play()


if __name__ == '__main__':
  main()
