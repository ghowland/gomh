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
import math
import random

from graphics import *
from actor import *
from constants import *


def Main():
  """The game.  Control function."""
  # Initialize the screen
  pygame.init()
  screen = pygame.display.set_mode(SCREEN_SIZE)
  pygame.display.set_caption('Get Off My Head')
  #pygame.mouse.set_visible(0)

  # Create the background
  background = pygame.Surface(screen.get_size())
  background = background.convert()
  background.fill((0, 0, 0))

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


  # Put the previously global variables back into the global name space
  global screen, background, sf_sprites, scene, scene_mask, speed


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


if __name__ == '__main__':
  Main()

