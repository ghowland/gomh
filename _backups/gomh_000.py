#!/usr/bin/env python

import pygame
import sys

sprite_size = [85/2, 112/2]

pygame.init()
size = (640, 480)
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Get Off My Head')
#pygame.mouse.set_visible(0)


background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((0, 0, 0))

while True:
  for event in pygame.event.get(): 
    if event.type == pygame.QUIT: 
      sys.exit(0) 


  # Render background
  background.fill((0, 0, 0))

  # Render to screen   
  screen.blit(background, (0,0))
  pygame.display.flip()


