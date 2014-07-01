"""
Constants
"""


# Scrolling here.  X and Y (Y to be implemented later...)
SCROLL_OFFSET = [0, 0]
SCREEN_SIZE = (640, 480)

SCALE = 0.5
sprite_size = [int(85*SCALE), int(112*SCALE)]

# Starting Health
STARTING_HEALTH = 12
HEALTH_GAINED_BY_KILL = 4

# Create our actors
ACTORS = []

# Specify the player, so that we dont use NPC AI for it
PLAYER_ACTOR_ID = 0
PLAYER_ACTOR = None
PLAYER_SPEED = 5
NPC_SPEED = 3
TOTAL_ACTORS = 6
#TOTAL_ACTORS = 2

# Screen and background
screen = None
background = None

# Load the SF character sprites
sf_sprites = None

# Load scene and it's collision mask
scene = None
scene_mask = None

