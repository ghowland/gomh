#!/usr/bin/env python

import pygame
import sys

sprite_size = [85/2, 112/2]

pygame.init()
size = (640, 480)
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Get Off My Head')
#pygame.mouse.set_visible(0)


image = pygame.image.load('sf_sprites.png')
image = pygame.transform.scale(image, (image.get_width()/2, image.get_height()/2))
image = image.convert_alpha()
sf_sprites = image

scene = pygame.image.load('sf_back.png')

guy0 = pygame.Surface(sprite_size)
guy0.convert_alpha() 
guy0.blit(sf_sprites, (0,0), [0, 0, sprite_size[0], sprite_size[1]])

background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((0, 0, 0))

guy0_pos = [0, 0]


while True:
  background.blit(guy0, guy0_pos)
  

  for event in pygame.event.get(): 
    if event.type == pygame.QUIT: 
          sys.exit(0) 

  keys = pygame.key.get_pressed()  #checking pressed keys
  if keys[pygame.K_LEFT]:
    guy0_pos[0] -= 2
  if keys[pygame.K_RIGHT]:
    guy0_pos[0] += 2
  if keys[pygame.K_UP]:
    guy0_pos[1] -= 2
  if keys[pygame.K_DOWN]:
    guy0_pos[1] += 2


  # Render background
  #background.fill((0, 0, 0))
  background.blit(scene, (0, 0))
  background.blit(guy0, guy0_pos)

  # Render to screen   
  screen.blit(background, (0,0))
  pygame.display.flip()


