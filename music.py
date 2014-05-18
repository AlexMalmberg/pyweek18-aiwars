import pygame
import time


class Music(object):
  IdleTime = 60.

  def __init__(self):
    pygame.mixer.music.load('data/theme_final.ogg')
    self.restart_time = 0
    self.playing = False

  def Update(self):
    if not self.playing:
      return
    if pygame.mixer.music.get_busy():
      self.restart_time = time.time() + self.IdleTime
    elif time.time() > self.restart_time:
      pygame.mixer.music.play()

  def Play(self):
    self.playing = True
    pygame.mixer.music.play()

  def Stop(self):
    pygame.mixer.music.stop()
    self.playing = False
