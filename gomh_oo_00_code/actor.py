"""
Actor class
"""


import pygame
import math
import random

import gomh_oo_00_code
from gomh_oo_00_code import collision


class Actor:
  def __init__(self, config, id, name, start_pos, speed, image_size, image_right, image_left, starting_health):
    print('Creating Actor: %s: %s: %s' % (id, name, start_pos))

    self.config = config
    
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
    closest_actor = None
    closest_dist = None
    
    for actor in self.config.ACTORS:
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
    if self.id != self.config.PLAYER_ACTOR_ID:
      self.UpdateNPC()
    
    #TODO(g): Replace actor. with self., this is a short-cut
    actor = self
    
    # Fall, if you can
    if actor.jump == 0:
      [fall_pos, collision_actor] = collision.MovePosCollide(self.config, actor, [0, actor.fall], self.config.ACTORS, self.config.scene_mask)
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
        [jump_pos, collision_actor] = collision.MovePosCollide(self.config, actor, [0, -1], self.config.ACTORS, self.config.scene_mask)

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
    [player_below_test_pos, collision_actor] = collision.MovePosCollide(self.config, actor, [0, 1], self.config.ACTORS, self.config.scene_mask)
    if player_below_test_pos == actor.pos and collision_actor != None:
      #print 'Standing on player: %s --- %s' % (self, collision_actor)
      killed_target = collision_actor.Hit(actor=self)
    
    
    # Take Scene Damage (fire anyone?)
    #TODO(g): Only testing right/left means that sitting in it or standing on it doesnt count, for every case
    # Test Right
    [damage_test_pos, collision_actor] = collision.MovePosCollide(self.config, actor, [1, 0], self.config.ACTORS, self.config.scene_mask, scene_obstacle_color=(255,66,246))
    if damage_test_pos == actor.pos:
      self.Hit(1)
    # Test Left
    [damage_test_pos, collision_actor] = collision.MovePosCollide(self.config, actor, [-1, 0], self.config.ACTORS, self.config.scene_mask, scene_obstacle_color=(255,66,246))
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
    
    [target_pos, collision_actor] = collision.MovePosCollide(self.config, self, move, self.config.ACTORS, self.config.scene_mask)
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
        actor.health += self.config.HEALTH_GAINED_BY_KILL
      
      return True
    
    else:
      return False
  
  
  def Respawn(self):
    global scene
    
    self.health = self.starting_health
    
    # Respawn anywhere in the map, at the fixed height
    found_good_respawn_point = False
    while not found_good_respawn_point:
      respawn_x = random.randint(0, self.config.scene.get_width() - self.image_size[0])
      self.pos = [respawn_x, 130]
      
      #TODO(g): Could be colliding with scene, in a different scene than the test one
      [target_pos, collision_actor] = collision.MovePosCollide(self.config, self, [0,0], self.config.ACTORS, self.config.scene_mask)
      if collision_actor == None:
        found_good_respawn_point = True


  def Jump(self):
    global ACTORS
    global scene_mask
    
    [ground_test_pos, collision_actor] = collision.MovePosCollide(self.config, self, [0, 1], self.config.ACTORS, self.config.scene_mask)
    # If we are free to jump
    if ground_test_pos == self.pos and self.jump == 0:
      # Test if there is an actor (or obstacle) directly above us
      [actor_on_head_test_pos, collision_actor] = collision.MovePosCollide(self.config, self, [0, -1], self.config.ACTORS, self.config.scene_mask)
      if actor_on_head_test_pos != self.pos:
        self.jump = 17
      
      # Else, if there was an actor standing on our head
      elif collision_actor != None:
        collision_actor.jump += 17

