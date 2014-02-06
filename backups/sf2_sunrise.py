#!/usr/bin/env python

import pygame
import sys

sprite_size = [85, 112]

pygame.init()
size = (640, 480)
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Street Figher 9')
#pygame.mouse.set_visible(0)


image = pygame.image.load('sf_sprites.png')
image = image.convert_alpha()
sf_sprites = image

scene = pygame.image.load('sf_back.png')

guy0 = pygame.Surface(sprite_size)
guy0.convert_alpha() 
guy0.blit(sf_sprites, (0,0), [0, 0, sprite_size[0], sprite_size[1]])

guy1 = pygame.Surface(sprite_size)
guy1.convert_alpha() 
guy1.blit(sf_sprites, (0,0), [sprite_size[0] * 1, sprite_size[1] * 0, sprite_size[0], sprite_size[1]])


background = pygame.Surface(screen.get_size())
background = background.convert_alpha()
#background = background.convert()

guy0_pos = [0, 0]
guy1_pos = [0, 100]

while True:
  # Process input
  for event in pygame.event.get(): 
    if event.type == pygame.QUIT: 
          sys.exit(0) 

  # Process Player Input
  keys = pygame.key.get_pressed()  #checking pressed keys
  if keys[pygame.K_LEFT]:
    guy1_pos[0] -= 2
  if keys[pygame.K_RIGHT]:
    guy1_pos[0] += 2
  if keys[pygame.K_UP]:
    guy1_pos[1] -= 2
  if keys[pygame.K_DOWN]:
    guy1_pos[1] += 2

  # Process Non-Player AI
  if guy0_pos[0] < guy1_pos[0]:
    guy0_pos[0] += 1
  if guy0_pos[0] > guy1_pos[0]:
    guy0_pos[0] -= 1

  if guy0_pos[1] < guy1_pos[1]:
    guy0_pos[1] += 1
  if guy0_pos[1] > guy1_pos[1]:
    guy0_pos[1] -= 1


  # Render background
  #background.fill((0, 0, 0))
  background.blit(scene, (0, 0))
  background.blit(guy0, guy0_pos)
  background.blit(guy1, guy1_pos)

  # Render to screen
  screen.blit(background, (0,0))
  pygame.display.flip()


