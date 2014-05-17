import pygame
from OpenGL.GL import *

import render_state


def DrawBox(x, y, w, h, border, ca, cb):
  glColor(*ca)
  #glNormal(*cb)

  glBegin(GL_QUADS)

  glVertex(x, y)
  glVertex(x + border, y)
  glVertex(x + border, y + h - border)
  glVertex(x, y + h - border)

  glVertex(x + w, y)
  glVertex(x + w - border, y)
  glVertex(x + w - border, y + h - border)
  glVertex(x + w, y + h - border)

  glVertex(x, y)
  glVertex(x, y + border)
  glVertex(x + w, y + border)
  glVertex(x + w, y)

  glVertex(x, y + h)
  glVertex(x, y + h - border)
  glVertex(x + w, y + h - border)
  glVertex(x + w, y + h)

  glEnd()


def Inside(x, y, box):
  return x >= box[0] and y >= box[1] and x <= box[2] and y <= box[3]


class DialogElement(object):
  # Tuple of (x0, y0, x1, y1) of region where the element is 'active',
  # or None. Mouse presses will be passed on to this element if they
  # are inside the active region.
  active_region = None

  # active == 2 if element being clicked, 1 if mouse-overed, 0 otherwise.
  def Render(self, render, text, active):
    pass

  def Clicked(self, x, y):
    pass

  def Dragged(self, x, y):
    pass

  def Unclicked(self, x, y):
    pass


class Text(DialogElement):
  def __init__(self, x, y, size, color, center, msg):
    self.x = x
    self.y = y
    self.size = size
    self.color = color
    self.center = center
    self.msg = str(msg)

  def Render(self, render, text, active):
    text.DrawString(self.x, self.y, self.size, self.color, self.msg,
                    center=self.center)


class Button(DialogElement):
  Border = 0.01

  def __init__(self, x, y, width, height, size, callback, msg):
    self.x = x
    self.y = y
    self.width = width
    self.height = height
    self.size = size
    self.callback = callback
    self.msg = str(msg)
    self.active_region = (x, y, x + width, y + height)
    self.tx = x + width / 2.
    self.ty = y + height / 2 - size / 2.

  def Render(self, render, text, active):
    if active == 2:
      ca = (1.0, 0.6, 0.4, 1)
      cb = (1.0, 0.6, 0.4, 1)
    elif active == 1:
      ca = (0.78, 0.22, 0.15, 1)
      cb = (0.78, 0.22, 0.15, 1)
    else:
      ca = (0, 0, 0, 1)
      cb = (0, 0.4, 0, 1)
    DrawBox(self.x, self.y, self.width, self.height, self.Border, ca, cb)
    text.DrawString(self.tx, self.ty, self.size, ca, self.msg, center=True)

  def Unclicked(self, x, y):
    if Inside(x, y, self.active_region):
      self.callback()


class Dialog(object):
  Border = 0.01

  def __init__(self, render, text, game_loop):
    self.render = render
    self.text = text
    self.game_loop = game_loop

    self.x = 0
    self.y = 0
    self.width = 0
    self.height = 0
    self.ready = False
    self.elements = []

    self.active_element = None
    self.button_pressed = False

  def AddElement(self, e):
    self.elements.append(e)

  def SetSize(self, width, height):
    self.width = width
    self.height = height

  def Center(self):
    self.x = -self.width / 2.
    self.y = -self.height / 2.

  def Ready(self):
    self.ready = True

  def Render(self):
    if not self.ready:
      return

    glColor(0, 0, 0, 0.4)
    glBegin(GL_QUADS)
    glVertex(-1.6, -1.0)
    glVertex( 1.6, -1.0)
    glVertex( 1.6,  1.0)
    glVertex(-1.6,  1.0)
    glEnd()

    glPushMatrix(GL_MODELVIEW_MATRIX)
    glTranslate(self.x, self.y, 0)

    # TODO: use solid-color raining numbers shader
    glColor(1.0, 0.9, 0.8, 1.0)
    glBegin(GL_QUADS)
    glVertex(0, 0)
    glVertex(self.width, 0)
    glVertex(self.width, self.height)
    glVertex(0, self.height)
    glEnd()

    # TODO: wireframe glowy-line shader
    glColor(0, 0, 0, 1)
    glBegin(GL_QUADS)

    glVertex(self.Border, self.Border)
    glVertex(self.Border * 2, self.Border)
    glVertex(self.Border * 2, self.height - self.Border)
    glVertex(self.Border, self.height - self.Border)

    glVertex(self.width - self.Border, self.Border)
    glVertex(self.width - self.Border * 2, self.Border)
    glVertex(self.width - self.Border * 2, self.height - self.Border)
    glVertex(self.width - self.Border, self.height - self.Border)


    glVertex(self.Border, self.Border)
    glVertex(self.Border * 2, self.Border * 2)
    glVertex(self.width - self.Border, self.Border * 2)
    glVertex(self.width - self.Border, self.Border)

    glVertex(self.Border, self.height - self.Border)
    glVertex(self.Border, self.height - self.Border * 2)
    glVertex(self.width - self.Border, self.height - self.Border * 2)
    glVertex(self.width - self.Border, self.height - self.Border)

    glEnd()

    for e in self.elements:
      if e == self.active_element:
        if self.button_pressed:
          a = 2
        else:
          a = 1
      else:
        a = 0
      e.Render(self.render, self.text, a)

    glPopMatrix(GL_MODELVIEW_MATRIX)

  def Close(self):
    self.game_loop.CloseDialog()

  def ViewportToDialog(self, x, y):
    return x - self.x, y - self.y

  def ElementAt(self, x, y):
    for e in self.elements:
      ar = e.active_region
      if not ar:
        continue
      if Inside(x, y, ar):
        return e
    return None

  def HandleEvents(self, dt):
    for e in pygame.event.get():
      if e.type == pygame.QUIT:
        self.game_loop.quit = True
        continue

      if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
        self.Close()
        continue

      if e.type == pygame.MOUSEMOTION:
        x, y = self.render.ScreenToViewport(*e.pos)
        x, y = self.ViewportToDialog(x, y)

        if self.button_pressed:
          if self.active_element:
            self.active_element.Dragged(x, y)
        else:
          self.active_element = self.ElementAt(x, y)
        continue

      if e.type == pygame.MOUSEBUTTONUP and e.button == 1:
        x, y = self.render.ScreenToViewport(*e.pos)
        x, y = self.ViewportToDialog(x, y)

        self.button_pressed = False
        if self.active_element:
          self.active_element.Unclicked(x, y)
        self.active_element = self.ElementAt(x, y)
        continue

      if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
        x, y = self.render.ScreenToViewport(*e.pos)
        x, y = self.ViewportToDialog(x, y)
        self.active_element = self.ElementAt(x, y)
        if self.active_element:
          self.active_element.Clicked(x, y)
        self.button_pressed = True
        continue