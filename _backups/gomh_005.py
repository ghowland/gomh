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

# Load scene and it's collision mask
scene = pygame.image.load('sf_back.png')
scene_mask = pygame.image.load('sf_back_mask.png')

guy0 = pygame.Surface(sprite_size)
guy0.convert_alpha() 
guy0.blit(sf_sprites, (0,0), [0, 0, sprite_size[0], sprite_size[1]])

guy1 = pygame.Surface(sprite_size)
guy1.convert_alpha() 
guy1.blit(sf_sprites, (0,0), [sprite_size[0] * 1, sprite_size[1] * 0, sprite_size[0], sprite_size[1]])

background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((0, 0, 0))

guy0_pos = [0, 150]
guy1_pos = [0, 100]



def MovePosCollideWithScene(pos, move, bounding_box_size, scene_image, scene_obstacle_color=(255,255,255)):
  """Returns a new position [x, y] from pos, moved by move [dx, dy], with 
  respect to colliding against non-moveable area in scene_image 
  (non [0,0,0] colors)

  Args:
    pos: list, [x, y]
    move: list, [dx, dy]
    bounding_box_size: list, [width, height]
    scene_image, Surface object

  Returns: list [new_x, new_y], if move is OK, otherwise [old_x, old_y]
  """
  has_collision = False

  # Create target position, where we want to move to
  target_pos = [pos[0] + move[0], pos[1] + move[1]]

  # Test for out of scene positions, and block
  if target_pos[0] < 0:
    has_collision = True
  elif target_pos[0] + bounding_box_size[0] >= scene.get_width() - 1:
    has_collision = True
  elif target_pos[1] < 0:
    has_collision = True
  elif target_pos[1] + bounding_box_size[1] >= scene.get_height() - 1:
    has_collision = True
  
  # Test scene, if we havent already found a collision with the scene border
  if not has_collision:
    #TODO(g): Collision detection with scene_image
    # Make all 4 corners of the bounding box
    corner_top_left = [target_pos[0], target_pos[1]]
    corner_top_right = [target_pos[0] + bounding_box_size[0], target_pos[1]]
    corner_bottom_left = [target_pos[0], target_pos[1] + bounding_box_size[1]]
    corner_bottom_right = [target_pos[0] + bounding_box_size[0], target_pos[1] + bounding_box_size[1]]

    # Get pixel values for each of the corners
    scene_top_left = scene_image.get_at(corner_top_left)[:3]
    scene_top_right = scene_image.get_at(corner_top_right)[:3]
    scene_bottom_left = scene_image.get_at(corner_bottom_left)[:3]
    scene_bottom_right = scene_image.get_at(corner_bottom_right)[:3]

    # Test for colission
    if scene_top_left == scene_obstacle_color:
      has_collision = True
    elif scene_top_right == scene_obstacle_color:
      has_collision = True
    elif scene_bottom_left == scene_obstacle_color:
      has_collision = True
    elif scene_bottom_right == scene_obstacle_color:
      has_collision = True

  # If there was a collision, dont move, create a new list form the old list 
  if has_collision:
    # #DEBUG: Print shit out to see
    # print 'TL: %s - %s' % (corner_top_left, scene_top_left)
    # print 'TR: %s - %s' % (corner_top_right, scene_top_right)
    # print 'BL: %s - %s' % (corner_bottom_left, scene_bottom_left)
    # print 'BR: %s - %s' % (corner_bottom_right, scene_bottom_right)

    final_pos = [pos[0], pos[1]]
  
  # Else, there was not a collision, move the position
  else:
    # print 'No collision, moving: %s' % move
    
    final_pos = target_pos

  return final_pos


while True:
  if guy0_pos[0] < guy1_pos[0]:
	  guy0_pos = MovePosCollideWithScene(guy0_pos, [1, 0], sprite_size, scene_mask)
  elif guy0_pos[0] > guy1_pos[0]:
	  guy0_pos = MovePosCollideWithScene(guy0_pos, [-1, 0], sprite_size, scene_mask)

  if guy0_pos[1] < guy1_pos[1]:
    guy0_pos = MovePosCollideWithScene(guy0_pos, [0, 1], sprite_size, scene_mask)
  elif guy0_pos[1] > guy1_pos[1]:
    guy0_pos = MovePosCollideWithScene(guy0_pos, [0, -1], sprite_size, scene_mask)
  

  for event in pygame.event.get(): 
    if event.type == pygame.QUIT: 
          sys.exit(0) 

  keys = pygame.key.get_pressed()  #checking pressed keys
  if keys[pygame.K_LEFT]:
    guy1_pos = MovePosCollideWithScene(guy1_pos, [-2, 0], sprite_size, scene_mask)
  if keys[pygame.K_RIGHT]:
    guy1_pos = MovePosCollideWithScene(guy1_pos, [2, 0], sprite_size, scene_mask)
  if keys[pygame.K_UP]:
    guy1_pos = MovePosCollideWithScene(guy1_pos, [0, -2], sprite_size, scene_mask)
  if keys[pygame.K_DOWN]:
    guy1_pos = MovePosCollideWithScene(guy1_pos, [0, 2], sprite_size, scene_mask)
  
  # If ESC is hit, quit
  if keys[pygame.K_ESCAPE]:
    sys.exit(0)


  # Render background
  #background.fill((0, 0, 0))
  background.blit(scene, (0, 0))
  background.blit(guy0, guy0_pos)
  background.blit(guy1, guy1_pos)

  # Render to screen   
  screen.blit(background, (0,0))
  pygame.display.flip()


