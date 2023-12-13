#!/usr/bin/env python
"""
GOMH - Get Off My Head

Todo:

  - Lives
  - Regain health while not being attacked.  Recharge.
  - Redo sprites for environment and characters.
  - 
"""

import pygame
import sys
import math
import random

import yaml

import gomh_oo_01_code

from gomh_oo_01_code.draw import *
from gomh_oo_01_code.util import *
from gomh_oo_01_code.actor import *


# Path to our config data
CONFIG_PATH = 'gomh_oo_01_data/data.yaml'


class Config:
  def __init__(self, config_path):
    with open(config_path) as fp:
      self.config_raw = yaml.safe_load(fp)

    self.SCALE = 0.5
    self.SPRITE_SIZE = Vector2(85*self.SCALE, 112*self.SCALE)

    # Scrolling here.  X and Y (Y to be implemented later...)
    self.SCROLL_OFFSET = Vector2(0, 0)
    self.SCREEN_SIZE = Vector2(640, 480)


    # Starting Health
    self.STARTING_HEALTH = 12
    self.HEALTH_GAINED_BY_KILL = 4


    # Create our actors
    self.ACTORS = []


    # Specify the player, so that we dont use NPC AI for it
    self.PLAYER_ACTOR_ID = 0
    self.PLAYER_ACTOR = None
    self.PLAYER_SPEED = 5
    self.NPC_SPEED = 3
    self.TOTAL_ACTORS = 6


def DoStuff(config):
  # Automatically load all the character
  for row in range(0, 4):
    for col in range(0, 4):
      key = (col, row)
      
      id = 4*row + col
      
      # Determine speed (player or NPC)
      if id == config.PLAYER_ACTOR_ID:
        speed = config.PLAYER_SPEED
      else:
        speed = config.NPC_SPEED
      
      # Only create this character if its not off the screen.  Thats a lot of characters anyway
      start_x = id * 150 + 220
      if len(config.ACTORS) < config.TOTAL_ACTORS:
        actor = Actor(config, id, 'Name: %s' % id, Vector2(start_x, 130), speed, config.SPRITE_SIZE, config.animations[key][0], config.animations[key][1], starting_health=config.STARTING_HEALTH)
        config.ACTORS.append(actor)
        
        # Set the player actor, by ID
        if id == config.PLAYER_ACTOR_ID:
          config.PLAYER_ACTOR = actor

  if config.PLAYER_ACTOR == None:
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
      config.PLAYER_ACTOR.Walk(Vector2(-5, 0))
    # Right
    if keys[pygame.K_RIGHT]:
      config.PLAYER_ACTOR.Walk(Vector2(5, 0))
    # Up
    if keys[pygame.K_UP]:
      config.PLAYER_ACTOR.Jump()


    # Update all our actors
    for actor in config.ACTORS:
      actor.Update()

    
    # If ESC is hit, quit
    if keys[pygame.K_ESCAPE]:
      sys.exit(0)

    # Handle scrolling the world
    scrolled_screen_x = [config.SCROLL_OFFSET.x, config.SCROLL_OFFSET.x + config.SCREEN_SIZE.x]

    boundary_x = int(config.SCREEN_SIZE.x / 2.5)
    scroll_by_pixels = 3

    # Left screen boundary
    if config.PLAYER_ACTOR.pos.x < scrolled_screen_x[0] + boundary_x:
      # Scroll faster if player is off the screen
      if config.PLAYER_ACTOR.pos.x < config.SCROLL_OFFSET.x:
        config.SCROLL_OFFSET.MoveX(-scroll_by_pixels * 3)
      else:
        config.SCROLL_OFFSET.MoveX(-scroll_by_pixels)
        
      if config.SCROLL_OFFSET.x < 0:
        config.SCROLL_OFFSET.x = 0
    
    # Right screen boundary
    elif config.PLAYER_ACTOR.pos.x > scrolled_screen_x[1] - boundary_x:
      # Scroll faster if player is off the screen
      if config.PLAYER_ACTOR.pos.x > config.SCROLL_OFFSET.x:
        config.SCROLL_OFFSET.MoveX(scroll_by_pixels * 3)
      else:
        config.SCROLL_OFFSET.MoveX(scroll_by_pixels)
      
      max_scroll_x = config.scene.get_width() - config.SCREEN_SIZE.x
      if config.SCROLL_OFFSET.x >= max_scroll_x:
        config.SCROLL_OFFSET.x = max_scroll_x

    # Render background
    Draw(config, config.scene, config.background, Vector2(0,0))
    
    # Draw all the actors
    for actor in config.ACTORS:
      Draw(config, actor.GetSurface(), config.background, actor.pos)
    
    # Draw UI
    # Draw Player Health Bar
    pygame.draw.rect(config.background, (240,240,240), pygame.rect.Rect((40, 40), (config.PLAYER_ACTOR.health * 5, 20)))

    # Render to screen   
    config.screen.blit(config.background, (0,0))
    pygame.display.flip()


def Main():
  # Create a config that wraps everything that used to be a 
  config = Config(CONFIG_PATH)

  # Initialize the screen
  pygame.init()
  config.screen = pygame.display.set_mode(config.SCREEN_SIZE.ToTuple())
  pygame.display.set_caption('Get Off My Head')
  #pygame.mouse.set_visible(0)

  # Create the background
  config.background = pygame.Surface(config.screen.get_size())
  config.background = config.background.convert()
  config.background.fill((0, 0, 0))

  # Load the SF character sprites
  sf_sprites = LoadImage(config, 'sf_sprites.png')

  # Load scene and it's collision mask
  config.scene = pygame.image.load('sf_back.png')
  config.scene_mask = pygame.image.load('sf_back_mask.png')

  # Create Actor Animations Sets (ghetto style, only left/right)
  config.animations = {}
  for row in range(0, 4):
    for col in range(0, 4):
      key = (col, row)
      
      face_right = pygame.Surface(config.SPRITE_SIZE.ToTuple())
      face_right.convert_alpha() 
      face_right.blit(sf_sprites, (0,0), [config.SPRITE_SIZE.x * col, config.SPRITE_SIZE.y * row, config.SPRITE_SIZE.x, config.SPRITE_SIZE.y])
      face_left = pygame.transform.flip(face_right, True, False)
      
      config.animations[key] = [face_right, face_left]


  DoStuff(config)


if __name__ == '__main__':
  Main()

