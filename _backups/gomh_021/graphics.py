"""
Graphics
"""

import pygame

from constants import *



def LoadImage(filename):
  image = pygame.image.load(filename)
  image = pygame.transform.scale(image, (int(image.get_width()*SCALE), int(image.get_height()*SCALE)))
  image = image.convert_alpha()
  return image


def Draw(surface, target_surface, pos):
  target_surface.blit(surface, GetPosScrolled(pos))


