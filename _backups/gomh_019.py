#!/usr/bin/env python

import pygame
import sys
import math
import random


SCALE = 0.5
sprite_size = [int(85*SCALE), int(112*SCALE)]

# Initialize the screen
pygame.init()
SCREEN_SIZE = (640, 480)
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption('Get Off My Head')
#pygame.mouse.set_visible(0)

# Create the background
background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((0, 0, 0))


# Scrolling here.  X and Y (Y to be implemented later...)
SCROLL_OFFSET = [0, 0]


def LoadImage(filename):
  image = pygame.image.load(filename)
  image = pygame.transform.scale(image, (int(image.get_width()*SCALE), int(image.get_height()*SCALE)))
  image = image.convert_alpha()
  return image

# Load the SF character sprites
sf_sprites = LoadImage('sf_sprites.png')

# Load scene and it's collision mask
scene = pygame.image.load('sf_back.png')
scene_mask = pygame.image.load('sf_back_mask.png')

# Create Actor Animations Sets (ghetto style, only left/right)
animations = {}
# for row in range(0, SF_SPRITE_MATRIX[1]):
#   for col in range(0, SF_SPRITE_MATRIX[0]):
for row in range(0, 4):
  for col in range(0, 4):
    key = (col, row)
    
    face_right = pygame.Surface(sprite_size)
    face_right.convert_alpha() 
    face_right.blit(sf_sprites, (0,0), [sprite_size[0] * col, sprite_size[1] * row, sprite_size[0], sprite_size[1]])
    face_left = pygame.transform.flip(face_right, True, False)
    
    animations[key] = [face_right, face_left]


# Starting Health
STARTING_HEALTH = 12
HEALTH_GAINED_BY_KILL = 4

class Actor:
  def __init__(self, id, name, start_pos, speed, image_size, image_right, image_left, starting_health=STARTING_HEALTH):
    print('Creating Actor: %s: %s: %s' % (id, name, start_pos))
    
    # Specified information
    self.id = id
    self.name = name
    self.pos = start_pos
    self.speed = speed
    self.image_size = image_size
    self.image_right = image_right
    self.image_left = image_left
    
    # Internal information
    self.jump = 0
    self.fall = 1
    self.move_left = False
    self.starting_health = starting_health
    self.health = starting_health
    self.kills = 0

  
  def __repr__(self):
    output = '%s: %s: %s' % (self.id, self.name, self.pos)
    return output
  
  
  def GetSurface(self):
    """Return the current surface for this game.
    TODO(g): Animations have not yet been introduced.
    """
    if self.move_left:
      return self.image_left
    else:
      return self.image_right


  def FindClosestActor(self):
    global ACTORS
    
    closest_actor = None
    closest_dist = None
    
    for actor in ACTORS:
      # Skip yourself
      if actor.id == self.id:
        continue
      
      dist = self.GetDistanceToActor(actor)
      
      if closest_dist == None or dist < closest_dist:
        closest_actor = actor
        closest_dist = dist
    
    return closest_actor

  
  def GetDistanceToActor(self, actor):
    dist = math.sqrt((actor.pos[0] - self.pos[0])**2 + (actor.pos[1] - self.pos[1])**2 )
    return dist


  def Update(self):
    """Process all physics and junk"""
    global PLAYER_ACTOR_ID
    if self.id != PLAYER_ACTOR_ID:
      self.UpdateNPC()
    
    #TODO(g): Replace actor. with self., this is a short-cut
    actor = self
    
    # Fall, if you can
    if actor.jump == 0:
      [fall_pos, collision_actor] = MovePosCollide(actor, [0, actor.fall], ACTORS, scene_mask)
      if fall_pos != actor.pos:
        actor.pos = fall_pos
        if actor.fall < 10:
          actor.fall += 1
      else:
        actor.fall = 1

    # Process Jumping
    if actor.jump > 0:
      hit_the_roof = False

      for count in range(0, int(actor.jump)):
        [jump_pos, collision_actor] = MovePosCollide(actor, [0, -1], ACTORS, scene_mask)

        # If we hit a ceiling, dont immediately cancell the jump, but reduce it quickly (gives a sense of upward inertia)
        if jump_pos == actor.pos:
          hit_the_roof = True
          break
        # Update the new position, cause we didnt hit the roof
        else:
          actor.pos = jump_pos

      # Reduce the jump each frame
      if not hit_the_roof:
        actor.jump -= 1
      else:
        actor.jump = actor.jump / 2
        if actor.jump <= 2:
          actor.jump = 0
    
    # Test you are standing on an actors head
    [player_below_test_pos, collision_actor] = MovePosCollide(actor, [0, 1], ACTORS, scene_mask)
    if player_below_test_pos == actor.pos and collision_actor != None:
      #print 'Standing on player: %s --- %s' % (self, collision_actor)
      killed_target = collision_actor.Hit(actor=self)
    
    
    # Take Scene Damage (fire anyone?)
    #TODO(g): Only testing right/left means that sitting in it or standing on it doesnt count, for every case
    # Test Right
    [damage_test_pos, collision_actor] = MovePosCollide(actor, [1, 0], ACTORS, scene_mask, scene_obstacle_color=(255,66,246))
    if damage_test_pos == actor.pos:
      self.Hit(1)
    # Test Left
    [damage_test_pos, collision_actor] = MovePosCollide(actor, [-1, 0], ACTORS, scene_mask, scene_obstacle_color=(255,66,246))
    if damage_test_pos == actor.pos:
      self.Hit(1)
    

  
  def UpdateNPC(self):
    """Update Non-Playing Characters"""
    #TODO(g): Rename actor. to self.
    actor = self
    
    # Find targer actor (the closest)
    target_actor = actor.FindClosestActor()
    if target_actor == None:
      raise Exception('WTF, is there only one?')
    
    # Starting AI state
    toward_target = True
    move_right = True
    target_above_self = False
    target_below_self = False
    
    # Determine if the target is Far Away
    dist = self.GetDistanceToActor(target_actor)
    if dist > self.image_size[0] * 3:
      target_far = True
    else:
      target_far = False
    
    # If above, by more than half your size, Move Away
    if self.pos[1] > target_actor.pos[1]:
      #print 'Actor Above Self: %s ----- %s' % (self, target_actor)
      target_above_self = True

    # If above, by more than half your size, Move Away
    if self.pos[1] < target_actor.pos[1] + target_actor.image_size[1]:
      #print 'Actor Below Self: %s ----- %s' % (self, target_actor)
      target_below_self = True


    # If the target is below, move the opposite direction -- Move Away
    if target_above_self and not target_far:
      if self.pos[0] > target_actor.pos[0]:
        target_move = [self.speed, 0]
      else:
        target_move = [-self.speed, 0]
    
    # Else, target is close vertically -- Move Toward
    else:
      if self.pos[0] < target_actor.pos[0]:
        target_move = [self.speed, 0]
      else:
        target_move = [-self.speed, 0]
    
    
    # Move specified amount
    blocked_by_scene = self.Walk(target_move)
    
    
    # If we want to jump
    if target_above_self or blocked_by_scene:
      actor.Jump()


  def Walk(self, move):
    """Returns boolean, True if collision with scene"""
    global ACTORS
    global scene_mask
    
    # Determine facing position
    if move[0] < 0:
      self.move_left = True
    else:
      self.move_left = False
    
    scene_collision = False
    
    [target_pos, collision_actor] = MovePosCollide(self, move, ACTORS, scene_mask)
    # If no collision, move
    if target_pos != self.pos:
      self.pos = target_pos
    
    # Else, character collision, push them
    elif collision_actor != None:
      push = [move[0] * 2, move[1] * 2]
      collision_actor.Walk(push)
    
    # Else, hit a wall
    else:
      scene_collision = True
    
    # Return boolean on whether could walk, blocked by scene
    return scene_collision



  def Hit(self, points=1, actor=None):
    """Returns boolean, True if actor was killed"""
    self.health -= points
    
    if self.health < 0:
      self.Respawn()
      
      # If an actor did this, give them the health bonus
      if actor != None:
        actor.health += HEALTH_GAINED_BY_KILL
      
      return True
    
    else:
      return False
  
  
  def Respawn(self):
    global scene
    
    self.health = self.starting_health
    
    # Respawn anywhere in the map, at the fixed height
    found_good_respawn_point = False
    while not found_good_respawn_point:
      respawn_x = random.randint(0, scene.get_width() - self.image_size[0])    
      self.pos = [respawn_x, 130]
      
      #TODO(g): Could be colliding with scene, in a different scene than the test one
      [target_pos, collision_actor] = MovePosCollide(self, [0,0], ACTORS, scene_mask)
      if collision_actor == None:
        found_good_respawn_point = True


  def Jump(self):
    global ACTORS
    global scene_mask
    
    [ground_test_pos, collision_actor] = MovePosCollide(self, [0, 1], ACTORS, scene_mask)
    # If we are free to jump
    if ground_test_pos == self.pos and self.jump == 0:
      # Test if there is an actor (or obstacle) directly above us
      [actor_on_head_test_pos, collision_actor] = MovePosCollide(self, [0, -1], ACTORS, scene_mask)
      if actor_on_head_test_pos != self.pos:
        self.jump = 17
      
      # Else, if there was an actor standing on our head
      elif collision_actor != None:
        collision_actor.jump += 17



# Create our actors
ACTORS = []


# Specify the player, so that we dont use NPC AI for it
PLAYER_ACTOR_ID = 0
PLAYER_ACTOR = None
PLAYER_SPEED = 5
NPC_SPEED = 3
TOTAL_ACTORS = 6
#TOTAL_ACTORS = 2

# Automatically load all the character
for row in range(0, 4):
  for col in range(0, 4):
    key = (col, row)
    
    id = 4*row + col
    
    # Determine speed (player or NPC)
    if id == PLAYER_ACTOR_ID:
      speed = PLAYER_SPEED
    else:
      speed = NPC_SPEED
    
    # Only create this character if its not off the screen.  Thats a lot of characters anyway
    start_x = id * 150 + 220
    if len(ACTORS) < TOTAL_ACTORS:
      actor = Actor(id, 'Name: %s' % id, [start_x, 130], speed, sprite_size, animations[key][0], animations[key][1])
      ACTORS.append(actor)
      
      # Set the player actor, by ID
      if id == PLAYER_ACTOR_ID:
        PLAYER_ACTOR = actor

if PLAYER_ACTOR == None:
  raise Exception('WTF?  Couldnt find the player actor, you didnt specify the ID correctly or didnt add the player actor in ACTORS')



def TestCollisionByPixelStep(start_pos, end_pos, step, scene, scene_obstacle_color=(255,255,255), log=False):
  """Test for a collision against the scene, starting at start_pos, ending at end_pos, using step to increment.
  
  NOTE: This function assumes that the bounding box has already been tested against the scene, and may call scene.get_at() in negative or over scene size, and crash
  """
  start_pos = [int(start_pos[0]), int(start_pos[1])]
  end_pos = [int(end_pos[0]), int(end_pos[1])]

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
      print('Col: dx: %s dy: %s  Start: %s  End: %s Cur: %s  distX: %s  distY: %s Pix: %s' % (dx, dy, start_pos, end_pos, current_pos, distance_x, distance_y, scene_value))
    
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


def MovePosCollide(actor, move, all_actors, scene_image, scene_obstacle_color=(255,255,255), log=False):
  """Collision with actors and scene"""
  # Collision with scene
  scene_pos = MovePosCollideWithScene(actor.pos, move, actor.image_size, scene_image, scene_obstacle_color=scene_obstacle_color, log=log)
  if scene_pos == actor.pos:
    scene_collision = True
  else:
    scene_collision = False
  
  # Test against actors
  actor_collision = False
  collision_with_actor = None
  target_pos = [actor.pos[0] + move[0], actor.pos[1] + move[1]]
  target_rect = pygame.Rect(target_pos, actor.image_size)
  for test_actor in all_actors:
    # Dont count yourself
    if actor.id != test_actor.id:
      test_actor_rect = pygame.Rect(test_actor.pos, test_actor.image_size)
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
    result = [list(actor.pos), collision_with_actor]
    #print 'Collision with actor: %s' % result
    return result
    

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
    step_test = 2
    
    #TODO(g): Collision detection with scene_image
    # Make all 4 corners of the bounding box
    corner_top_left = [int(target_pos[0]), int(target_pos[1])]
    corner_top_right = [int(target_pos[0]) + int(bounding_box_size[0]), int(target_pos[1])]
    corner_bottom_left = [int(target_pos[0]), int(target_pos[1]) + int(bounding_box_size[1])]
    corner_bottom_right = [int(target_pos[0]) + int(bounding_box_size[0]), int(target_pos[1]) + int(bounding_box_size[1])]

    if log:
      print('')

    # Test the bounding box, using step (N pixels) to get better resolution on obstacle collision
    if TestCollisionByPixelStep(corner_top_left, corner_top_right, step_test, scene_image, scene_obstacle_color=scene_obstacle_color, log=log):
      has_collision = True
    elif TestCollisionByPixelStep(corner_top_left, corner_bottom_left, step_test, scene_image, scene_obstacle_color=scene_obstacle_color, log=log):
      has_collision = True
    elif TestCollisionByPixelStep(corner_top_right, corner_bottom_right, step_test, scene_image, scene_obstacle_color=scene_obstacle_color, log=log):
      has_collision = True
    elif TestCollisionByPixelStep(corner_bottom_left, corner_bottom_right, step_test, scene_image, scene_obstacle_color=scene_obstacle_color, log=log):
      has_collision = True


  # If there was a collision, dont move, create a new list form the old list 
  if has_collision:
    final_pos = [pos[0], pos[1]]
  
  # Else, there was not a collision, move the position
  else:
    final_pos = target_pos

  return final_pos


def GetPosScrolled(pos):
  global SCROLL_OFFSET
  
  scrolled_pos = [pos[0] - SCROLL_OFFSET[0], pos[1] - SCROLL_OFFSET[1]]
  
  return scrolled_pos


def Draw(surface, target_surface, pos):
  target_surface.blit(surface, GetPosScrolled(pos))


cur_time = pygame.time.get_ticks()
while True:
  #print 'Actors: %s' % ACTORS
  last_time = cur_time
  cur_time = pygame.time.get_ticks()
  ellapsed_time = cur_time - last_time
  if ellapsed_time:
    fps = 1000 / ellapsed_time
    #print 'FPS: %s' % fps


  # Event pump
  for event in pygame.event.get(): 
    if event.type == pygame.QUIT: 
          sys.exit(0) 


  # Player input handling
  keys = pygame.key.get_pressed()  #checking pressed keys
  # Left
  if keys[pygame.K_LEFT]:
    PLAYER_ACTOR.Walk([-5, 0])
    # PLAYER_ACTOR.move_left = True
    # [PLAYER_ACTOR.pos, collision_actor] = MovePosCollide(PLAYER_ACTOR, [-5, 0], ACTORS, scene_mask)
  # Right
  if keys[pygame.K_RIGHT]:
    PLAYER_ACTOR.Walk([5, 0])
    # PLAYER_ACTOR.move_left = False
    # [PLAYER_ACTOR.pos, collision_actor] = MovePosCollide(PLAYER_ACTOR, [5, 0], ACTORS, scene_mask)
  # Up
  if keys[pygame.K_UP]:
    PLAYER_ACTOR.Jump()


  # Update all our actors
  for actor in ACTORS:
    actor.Update()

  
  # If ESC is hit, quit
  if keys[pygame.K_ESCAPE]:
    sys.exit(0)


  # Handle scrolling the world
  scrolled_screen_x = [SCROLL_OFFSET[0], SCROLL_OFFSET[0] + SCREEN_SIZE[0]]
  boundary_x = int(SCREEN_SIZE[0] / 2.5)
  scroll_by_pixels = 3
  # Left screen boundary
  if PLAYER_ACTOR.pos[0] < scrolled_screen_x[0] + boundary_x:
    # Scroll faster if player is off the screen
    if PLAYER_ACTOR.pos[0] < SCROLL_OFFSET[0]:
      SCROLL_OFFSET[0] -= scroll_by_pixels * 3
    else:
      SCROLL_OFFSET[0] -= scroll_by_pixels
      
    if SCROLL_OFFSET[0] < 0:
      SCROLL_OFFSET[0] = 0
  
  # Right screen boundary
  elif PLAYER_ACTOR.pos[0] > scrolled_screen_x[1] - boundary_x:
    # Scroll faster if player is off the screen
    if PLAYER_ACTOR.pos[0] > SCROLL_OFFSET[0]:
      SCROLL_OFFSET[0] += scroll_by_pixels * 3
    else:
      SCROLL_OFFSET[0] += scroll_by_pixels
    
    max_scroll_x = scene.get_width() - SCREEN_SIZE[0]
    if SCROLL_OFFSET[0] >= max_scroll_x:
      SCROLL_OFFSET[0] = max_scroll_x


  # Render background
  Draw(scene, background, (0,0))
  
  
  # Draw all the actors
  for actor in ACTORS:
    Draw(actor.GetSurface(), background, actor.pos)
  
  # Draw UI
  # Draw Player Health Bar
  pygame.draw.rect(background, (240,240,240), pygame.rect.Rect((40, 40), (PLAYER_ACTOR.health * 5, 20)))

  # Render to screen   
  screen.blit(background, (0,0))
  pygame.display.flip()


