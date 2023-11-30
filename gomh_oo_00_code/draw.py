import pygame


def LoadImage(config, filename):
  image = pygame.image.load(filename)
  image = pygame.transform.scale(image, (int(image.get_width() * config.SCALE), int(image.get_height() * config.SCALE)))
  image = image.convert_alpha()
  return image



def GetPosScrolled(config, pos):
  scrolled_pos = [pos[0] - config.SCROLL_OFFSET[0], pos[1] - config.SCROLL_OFFSET[1]]
  
  return scrolled_pos


def Draw(config, surface, target_surface, pos):
  target_surface.blit(surface, GetPosScrolled(config, pos))

