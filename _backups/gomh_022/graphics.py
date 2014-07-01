"""
Graphics
"""

import pygame

import constants



def LoadImage(filename):
  image = pygame.image.load(filename)
  image = pygame.transform.scale(image, (int(image.get_width()*constants.SCALE), int(image.get_height()*constants.SCALE)))
  image = image.convert_alpha()
  return image


def Draw(surface, target_surface, pos):
  target_surface.blit(surface, GetPosScrolled(pos))


def GetPosScrolled(pos):
  scrolled_pos = [pos[0] - constants.SCROLL_OFFSET[0], pos[1] - constants.SCROLL_OFFSET[1]]
  
  return scrolled_pos

