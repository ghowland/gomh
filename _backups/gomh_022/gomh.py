#!/usr/bin/env python
"""
GOMH - Get Off My Head

Todo:

  - Lives
  - Regain health while not being attacked.  Recharge.
  - Redo sprites for environment and characters.
  - 
"""


import sys

import constants

from graphics import *
from actor import *


def Main():
  """The game.  Control function."""
  # Initialize the screen
  pygame.init()
  constants.screen = pygame.display.set_mode(constants.SCREEN_SIZE)
  pygame.display.set_caption('Get Off My Head')
  #pygame.mouse.set_visible(0)

  # Create the background
  constants.background = pygame.Surface(constants.screen.get_size())
  constants.background = constants.background.convert()
  constants.background.fill((0, 0, 0))

  # Load the SF character sprites
  constants.sf_sprites = LoadImage('sf_sprites.png')

  # Load scene and it's collision mask
  constants.scene = pygame.image.load('sf_back.png')
  constants.scene_mask = pygame.image.load('sf_back_mask.png')


  # Create Actor Animations Sets (ghetto style, only left/right)
  animations = {}
  # for row in range(0, SF_SPRITE_MATRIX[1]):
  #   for col in range(0, SF_SPRITE_MATRIX[0]):
  for row in range(0, 4):
    for col in range(0, 4):
      key = (col, row)
      
      face_right = pygame.Surface(constants.sprite_size)
      face_right.convert_alpha() 
      face_right.blit(constants.sf_sprites, (0,0), [constants.sprite_size[0] * col, constants.sprite_size[1] * row, constants.sprite_size[0], constants.sprite_size[1]])
      face_left = pygame.transform.flip(face_right, True, False)
      
      animations[key] = [face_right, face_left]


  # Automatically load all the character
  for row in range(0, 4):
    for col in range(0, 4):
      key = (col, row)
      
      id = 4*row + col
      
      # Determine speed (player or NPC)
      if id == constants.PLAYER_ACTOR_ID:
        speed = constants.PLAYER_SPEED
      else:
        speed = constants.NPC_SPEED
      
      # Only create this character if its not off the screen.  Thats a lot of characters anyway
      start_x = id * 150 + 220
      if len(constants.ACTORS) < constants.TOTAL_ACTORS:
        actor = Actor(id, 'Name: %s' % id, [start_x, 130], speed, constants.sprite_size, animations[key][0], animations[key][1])
        constants.ACTORS.append(actor)
        
        # Set the player actor, by ID
        if id == constants.PLAYER_ACTOR_ID:
          constants.PLAYER_ACTOR = actor

  if constants.PLAYER_ACTOR == None:
    raise Exception('WTF?  Couldnt find the player actor, you didnt specify the ID correctly or didnt add the player actor in ACTORS')


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
      constants.PLAYER_ACTOR.Walk([-5, 0])
      # PLAYER_ACTOR.move_left = True
      # [PLAYER_ACTOR.pos, collision_actor] = MovePosCollide(PLAYER_ACTOR, [-5, 0], ACTORS, scene_mask)
    # Right
    if keys[pygame.K_RIGHT]:
      constants.PLAYER_ACTOR.Walk([5, 0])
      # PLAYER_ACTOR.move_left = False
      # [PLAYER_ACTOR.pos, collision_actor] = MovePosCollide(PLAYER_ACTOR, [5, 0], ACTORS, scene_mask)
    # Up
    if keys[pygame.K_UP]:
      constants.PLAYER_ACTOR.Jump()


    # Update all our actors
    for actor in constants.ACTORS:
      actor.Update()

    
    # If ESC is hit, quit
    if keys[pygame.K_ESCAPE]:
      sys.exit(0)


    # Handle scrolling the world
    scrolled_screen_x = [constants.SCROLL_OFFSET[0], constants.SCROLL_OFFSET[0] + constants.SCREEN_SIZE[0]]
    boundary_x = int(constants.SCREEN_SIZE[0] / 2.5)
    scroll_by_pixels = 3
    # Left screen boundary
    if constants.PLAYER_ACTOR.pos[0] < scrolled_screen_x[0] + boundary_x:
      # Scroll faster if player is off the screen
      if constants.PLAYER_ACTOR.pos[0] < constants.SCROLL_OFFSET[0]:
        constants.SCROLL_OFFSET[0] -= scroll_by_pixels * 3
      else:
        constants.SCROLL_OFFSET[0] -= scroll_by_pixels
        
      if constants.SCROLL_OFFSET[0] < 0:
        constants.SCROLL_OFFSET[0] = 0
    
    # Right screen boundary
    elif constants.PLAYER_ACTOR.pos[0] > scrolled_screen_x[1] - boundary_x:
      # Scroll faster if player is off the screen
      if constants.PLAYER_ACTOR.pos[0] > constants.SCROLL_OFFSET[0]:
        constants.SCROLL_OFFSET[0] += scroll_by_pixels * 3
      else:
        constants.SCROLL_OFFSET[0] += scroll_by_pixels
      
      max_scroll_x = constants.scene.get_width() - constants.SCREEN_SIZE[0]
      if constants.SCROLL_OFFSET[0] >= max_scroll_x:
        constants.SCROLL_OFFSET[0] = max_scroll_x


    # Render background
    Draw(constants.scene, constants.background, (0,0))
    
    
    # Draw all the actors
    for actor in constants.ACTORS:
      Draw(actor.GetSurface(), constants.background, actor.pos)
    
    # Draw UI
    # Draw Player Health Bar
    pygame.draw.rect(constants.background, (240,240,240), pygame.rect.Rect((40, 40), (constants.PLAYER_ACTOR.health * 5, 20)))

    # Render to screen   
    constants.screen.blit(constants.background, (0,0))
    pygame.display.flip()


if __name__ == '__main__':
  Main()

