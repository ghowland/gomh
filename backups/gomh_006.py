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

guy0_pos = [300, 150]
guy1_pos = [360, 100]


def TestCollisionByPixelStep(start_pos, end_pos, step, scene, scene_obstacle_color=(255,255,255), log=False):
  """Test for a collision against the scene, starting at start_pos, ending at end_pos, using step to increment.
  
  NOTE: This function assumes that the bounding box has already been tested against the scene, and may call scene.get_at() in negative or over scene size, and crash
  """
  # Create deltas (differences) for the step in X and Y depending on the step and start-end positions
  # Delta X
  if start_pos[0] < end_pos[0]:
    dx = 1
  elif start_pos[0] > end_pos[0]:
    dx = -1
  else:
    dx = 0
  
  # Delta Y
  if start_pos[1] < end_pos[1]:
    dy = 1
  elif start_pos[1] > end_pos[1]:
    dy = -1
  else:
    dy = 0
  
  # Ensure we can actually move across the line, or fail
  if dx == 0 and dy == 0:
    raise Exception('What the fuck?  The start and end positions are the same...  Handle this case later.')
  
  # Determine the distance required to travel in X and Y directions based on the start/end positions
  distance_x = abs(start_pos[0] - end_pos[0])
  distance_y = abs(start_pos[1] - end_pos[1])

  # Start the current position at the starting position
  current_pos = [start_pos[0], start_pos[1]]
  
  # Loop until we reach the end position, or find a collision
  end_pos_reached = False
  has_collision = False
  distance_travelled = 0
  
  while not end_pos_reached and not has_collision:
    # Get the pixel value at the current position
    scene_value = scene.get_at(current_pos)[:3]
    
    if log:
      print 'Col: dx: %s dy: %s  Start: %s  End: %s Cur: %s  distX: %s  distY: %s Pix: %s' % (dx, dy, start_pos, end_pos, current_pos, distance_x, distance_y, scene_value)
    
    # If the pixel matches the scene_obstacle_color, there is a collision
    if scene_value == scene_obstacle_color:
      has_collision = True
    
    # Else, increment the current_pos by the dx and dy, multiplied by the step
    else:
      # Increment the current_pos
      current_pos = [current_pos[0] + (dx * step), current_pos[1] + (dy * step)]
      distance_travelled += step
      
      # If the current_pos is past the end_pos, then test the end_pos position, and set end_pos_reached (final test it required)
      if distance_x != 0 and distance_travelled >= distance_x:
        # We reached the end, but make the last pixel test anyway, just to be sure we have checked them all
        end_pos_reached = True
        
        # Get the pixel value at the current position
        scene_value = scene.get_at(end_pos)[:3]

        # If the pixel matches the scene_obstacle_color, there is a collision
        if scene_value == scene_obstacle_color:
          has_collision = True
      
      elif distance_y != 0 and distance_travelled >= distance_y:
        # We reached the end, but make the last pixel test anyway, just to be sure we have checked them all
        end_pos_reached = True
        
        # Get the pixel value at the current position
        scene_value = scene.get_at(end_pos)[:3]

        # If the pixel matches the scene_obstacle_color, there is a collision
        if scene_value == scene_obstacle_color:
          has_collision = True
  
  return has_collision  


def MovePosCollideWithScene(pos, move, bounding_box_size, scene_image, scene_obstacle_color=(255,255,255), log=False):
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
    # Test every N pixels, to not miss collisions that are smaller than the bounding box
    step_test = 1
    
    #TODO(g): Collision detection with scene_image
    # Make all 4 corners of the bounding box
    corner_top_left = [target_pos[0], target_pos[1]]
    corner_top_right = [target_pos[0] + bounding_box_size[0], target_pos[1]]
    corner_bottom_left = [target_pos[0], target_pos[1] + bounding_box_size[1]]
    corner_bottom_right = [target_pos[0] + bounding_box_size[0], target_pos[1] + bounding_box_size[1]]

    if log:
      print ''

    # Test the bounding box, using step (N pixels) to get better resolution on obstacle collision
    if TestCollisionByPixelStep(corner_top_left, corner_top_right, step_test, scene_image, log=log):
      has_collision = True
    elif TestCollisionByPixelStep(corner_top_left, corner_bottom_left, step_test, scene_image, log=log):
      has_collision = True
    elif TestCollisionByPixelStep(corner_top_right, corner_bottom_right, step_test, scene_image, log=log):
      has_collision = True
    elif TestCollisionByPixelStep(corner_bottom_left, corner_bottom_right, step_test, scene_image, log=log):
      has_collision = True

    # # Get pixel values for each of the corners
    # scene_top_left = scene_image.get_at(corner_top_left)[:3]
    # scene_top_right = scene_image.get_at(corner_top_right)[:3]
    # scene_bottom_left = scene_image.get_at(corner_bottom_left)[:3]
    # scene_bottom_right = scene_image.get_at(corner_bottom_right)[:3]
    # 
    # # Test for colission
    # if scene_top_left == scene_obstacle_color:
    #   has_collision = True
    # elif scene_top_right == scene_obstacle_color:
    #   has_collision = True
    # elif scene_bottom_left == scene_obstacle_color:
    #   has_collision = True
    # elif scene_bottom_right == scene_obstacle_color:
    #   has_collision = True

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
  background.blit(guy0, guy0_pos)
  background.blit(guy1, guy1_pos)

  if guy0_pos[0] < guy1_pos[0]:
	  guy0_pos = MovePosCollideWithScene(guy0_pos, [1, 0], sprite_size, scene_mask)
  elif guy0_pos[0] > guy1_pos[0]:
	  guy0_pos = MovePosCollideWithScene(guy0_pos, [-1, 0], sprite_size, scene_mask)

  # if guy0_pos[1] < guy1_pos[1]:
  #   guy0_pos = MovePosCollideWithScene(guy0_pos, [0, 1], sprite_size, scene_mask)
  # elif guy0_pos[1] > guy1_pos[1]:
  #   guy0_pos = MovePosCollideWithScene(guy0_pos, [0, -1], sprite_size, scene_mask)
  

  for event in pygame.event.get(): 
    if event.type == pygame.QUIT: 
          sys.exit(0) 

  keys = pygame.key.get_pressed()  #checking pressed keys
  if keys[pygame.K_LEFT]:
    guy1_pos = MovePosCollideWithScene(guy1_pos, [-2, 0], sprite_size, scene_mask)
  if keys[pygame.K_RIGHT]:
    guy1_pos = MovePosCollideWithScene(guy1_pos, [2, 0], sprite_size, scene_mask)
  # if keys[pygame.K_UP]:
  #   guy1_pos = MovePosCollideWithScene(guy1_pos, [0, -2], sprite_size, scene_mask)
  # if keys[pygame.K_DOWN]:
  #   guy1_pos = MovePosCollideWithScene(guy1_pos, [0, 2], sprite_size, scene_mask)
  
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


