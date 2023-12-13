"""
Collision
"""


import pygame

import gomh_oo_01_code
from gomh_oo_01_code import util
from gomh_oo_01_code.util import Vector2


def TestCollisionByPixelStep(config, start_pos, end_pos, step, scene, scene_obstacle_color=(255,255,255), log=False):
  """Test for a collision against the scene, starting at start_pos, ending at end_pos, using step to increment.
  
  NOTE: This function assumes that the bounding box has already been tested against the scene, and may call scene.get_at() in negative or over scene size, and crash
  """
  # Create deltas (differences) for the step in X and Y depending on the step and start-end positions
  # Delta X
  if start_pos.x < end_pos.x:
    dx = 1
  elif start_pos.x > end_pos.x:
    dx = -1
  else:
    dx = 0
  
  # Delta Y
  if start_pos.y < end_pos.y:
    dy = 1
  elif start_pos.y > end_pos.y:
    dy = -1
  else:
    dy = 0
  
  # Ensure we can actually move across the line, or fail
  if dx == 0 and dy == 0:
    raise Exception('What the fuck?  The start and end positions are the same...  Handle this case later.')
  
  # Determine the distance required to travel in X and Y directions based on the start/end positions
  distance_x = abs(start_pos.x - end_pos.x)
  distance_y = abs(start_pos.y - end_pos.y)

  # Start the current position at the starting position
  current_pos = Vector2(start_pos.x, start_pos.y)
  
  # Loop until we reach the end position, or find a collision
  end_pos_reached = False
  has_collision = False
  distance_travelled = 0
  
  while not end_pos_reached and not has_collision:
    # Get the pixel value at the current position
    scene_value = scene.get_at(current_pos.ToTuple())[:3]
    
    if log:
      print('Col: dx: %s dy: %s  Start: %s  End: %s Cur: %s  distX: %s  distY: %s Pix: %s' % (dx, dy, start_pos, end_pos, current_pos, distance_x, distance_y, scene_value))
    
    # If the pixel matches the scene_obstacle_color, there is a collision
    if scene_value == scene_obstacle_color:
      has_collision = True
    
    # Else, increment the current_pos by the dx and dy, multiplied by the step
    else:
      # Increment the current_pos
      current_pos = Vector2(current_pos.x + (dx * step), current_pos.y + (dy * step))
      distance_travelled += step
      
      # If the current_pos is past the end_pos, then test the end_pos position, and set end_pos_reached (final test it required)
      if distance_x != 0 and distance_travelled >= distance_x:
        # We reached the end, but make the last pixel test anyway, just to be sure we have checked them all
        end_pos_reached = True
        
        # Get the pixel value at the current position
        scene_value = scene.get_at(end_pos.ToTuple())[:3]

        # If the pixel matches the scene_obstacle_color, there is a collision
        if scene_value == scene_obstacle_color:
          has_collision = True
      
      elif distance_y != 0 and distance_travelled >= distance_y:
        # We reached the end, but make the last pixel test anyway, just to be sure we have checked them all
        end_pos_reached = True
        
        # Get the pixel value at the current position
        scene_value = scene.get_at(end_pos.ToTuple())[:3]

        # If the pixel matches the scene_obstacle_color, there is a collision
        if scene_value == scene_obstacle_color:
          has_collision = True
  
  return has_collision  


def MovePosCollide(config, actor, move, all_actors, scene_image, scene_obstacle_color=(255,255,255), log=False):
  """Collision with actors and scene"""
  # Collision with scene
  scene_pos = MovePosCollideWithScene(config, actor.pos, move, actor.image_size, scene_image, scene_obstacle_color=scene_obstacle_color, log=log)
  if scene_pos == actor.pos:
    scene_collision = True
  else:
    scene_collision = False
  
  # Test against actors
  actor_collision = False
  collision_with_actor = None
  target_pos = Vector2(actor.pos.x + move.x, actor.pos.y + move.y)
  target_rect = pygame.Rect(target_pos.ToTuple(), actor.image_size.ToTuple())
  for test_actor in all_actors:
    # Dont count yourself
    if actor.id != test_actor.id:
      test_actor_rect = pygame.Rect(test_actor.pos.ToTuple(), test_actor.image_size.ToTuple())
      has_collision = test_actor_rect.colliderect(target_rect)
    
      if has_collision:
        #print 'Collision: %s with %s' % (target_pos, test_actor)
        actor_collision = True
        collision_with_actor = test_actor
        break
    else:
      #print 'Collision: Skip self: %s' % test_actor
      pass
  
  # If we didnt have collisions with scene or actors, return moved position
  if not scene_collision and not actor_collision:
    return (target_pos, collision_with_actor)
  # Else, had collision so return current position
  else:
    result = [actor.pos.Clone(), collision_with_actor]
    #print 'Collision with actor: %s' % result
    return result
    

def MovePosCollideWithScene(config, pos, move, bounding_box_size, scene_image, scene_obstacle_color=(255,255,255), log=False):
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
  target_pos = Vector2(pos.x + move.x, pos.y + move.y)

  # Test for out of scene positions, and block
  if target_pos.x < 0:
    has_collision = True
  elif target_pos.x + bounding_box_size.x >= config.scene.get_width() - 1:
    has_collision = True
  elif target_pos.y < 0:
    has_collision = True
  elif target_pos.y + bounding_box_size.y >= config.scene.get_height() - 1:
    has_collision = True
  
  # Test scene, if we havent already found a collision with the scene border
  if not has_collision:
    # Test every N pixels, to not miss collisions that are smaller than the bounding box
    step_test = 2
    
    #TODO(g): Collision detection with scene_image
    # Make all 4 corners of the bounding box
    corner_top_left = Vector2(target_pos.x, target_pos.y)
    corner_top_right = Vector2(target_pos.x + bounding_box_size.x, target_pos.y)
    corner_bottom_left = Vector2(target_pos.x, target_pos.y + bounding_box_size.y)
    corner_bottom_right = Vector2(target_pos.x + bounding_box_size.x, target_pos.y + bounding_box_size.y)

    if log:
      print('')

    # Test the bounding box, using step (N pixels) to get better resolution on obstacle collision
    if TestCollisionByPixelStep(config, corner_top_left, corner_top_right, step_test, scene_image, scene_obstacle_color=scene_obstacle_color, log=log):
      has_collision = True
    elif TestCollisionByPixelStep(config, corner_top_left, corner_bottom_left, step_test, scene_image, scene_obstacle_color=scene_obstacle_color, log=log):
      has_collision = True
    elif TestCollisionByPixelStep(config, corner_top_right, corner_bottom_right, step_test, scene_image, scene_obstacle_color=scene_obstacle_color, log=log):
      has_collision = True
    elif TestCollisionByPixelStep(config, corner_bottom_left, corner_bottom_right, step_test, scene_image, scene_obstacle_color=scene_obstacle_color, log=log):
      has_collision = True


  # If there was a collision, dont move, create a new list form the old list 
  if has_collision:
    final_pos = pos
  
  # Else, there was not a collision, move the position
  else:
    final_pos = target_pos

  return final_pos

