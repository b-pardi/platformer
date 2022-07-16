from cv2 import line
import pygame
import sys

pygame.init()
clock = pygame.time.Clock()
FPS = 60
WINDOW_SIZE = (800, 600)
screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)\
# surfaces are just images
# write all onto display, to scale up to screen size for consistency
display = pygame.Surface((300, 200))
pygame.display.set_caption("Le Geam")

# animations
global animation_frames
animation_frames = {}

# dictionary stores how long the fn of each animation frame,
# and uses frame_durations to track how many game frames each animation frame stays for

def load_anim(path, frames_durations):
    global animation_frames
    # loads path to file, takes last dir of path and grabs the name from it
    # naming matches file tree
    anim_name = path.split('/')[-1]
    anim_frame_data = []
    n = 0
    for frame in frames_durations:
        anim_frame_id = anim_name + '_' + str(n)
        img_loc = path + '/' + anim_frame_id + '.png'
        anim_img = pygame.image.load(img_loc).convert()
        anim_img.set_colorkey((255,255,255))
        animation_frames[anim_frame_id] = anim_img.copy()
        for i in range(frame):
            anim_frame_data.append(anim_frame_id)
        n+=1
    return anim_frame_data
#print(load_anim('player_animations/idle', [7, 7, 40]))

def change_action(cur_action, frame, new_action):
    if cur_action != new_action:
        cur_action = new_action
        frame = 0
    return cur_action, frame

anim_db = {}
anim_db['run'] = load_anim('player_animations/run', [7, 7])
anim_db['idle'] = load_anim('player_animations/idle', [7, 7, 40])

player_action = 'idle'
player_frame = 0
player_flip = False # flip player when moving left/right

# load images
player_img = pygame.image.load("imgs/playera.png")
grass_img = pygame.image.load("imgs/grass.png")
dirt_img = pygame.image.load("imgs/dirt.png")
TILE_SIZE = grass_img.get_width()

# initial vars
player_loc = [50,50]
moving_left = False
moving_right = False
player_ymomentum = 0

# air timer for quality of life when jumping of ledges
air_timer = 0

# declare rects
player_rect = pygame.Rect(50, 50, player_img.get_width(), player_img.get_height())
collide_rect = pygame.Rect(100, 100, 100, 50)

# move tiles for scrolling screen
true_scroll = [0,0]

# parallax scrolling, first value scalar to change how fast it moves,
# second value is pygame rect object (x, y, w, h)
# lower scalar values move quicker (render them first!!)
background_objects = [[0.25,[120,10,70,400]],[0.25,[280,30,40,400]],[0.5,[30,40,40,400]],[0.5,[130,90,100,400]],[0.5,[300,80,120,400]]]

# game_map[y][x]
def load_map(path):
    with open(path + ".txt", 'r') as fp:
        line_data = fp.read().split('\n')
        map = []
        for row in line_data:
            map.append(list(row))
    return map
    
game_map = load_map("maps/map")

def collision_test(rect, tiles):
    collided = []
    for tile in tiles:
        if rect.colliderect(tile):
            collided.append(tile)
    return collided

# separate x and y axis, test for each individually
# movement just list x and y of directions moved
# rect is the rectangle being moved, i.e. the player
def move(rect, mvmt, tiles):
    # dict to keep track of where collision occurs for later use
    collision_directions = {'top' : False, 'bottom' : False, 'right' : False, 'left' : False}
    rect.x += mvmt[0]
    collided = collision_test(rect, tiles)
    for tile in collided:
        if mvmt[0] > 0: # moving right
            # when player moving right and collides with tile in front of it,
            # put the rect to the left of tile
            rect.right = tile.left
            collision_directions['right'] = True
        elif mvmt[0] < 0: # moving left
            rect.left = tile.right
            collision_directions['left'] = True

    rect.y += mvmt[1]
    collided = collision_test(rect, tiles)
    for tile in collided:
        if mvmt[1] > 0: # falling down
            rect.bottom = tile.top
            collision_directions['bottom'] = True
        elif mvmt[1] < 0: # going up
            rect.top = tile.bottom
            collision_directions['top'] = True
    return rect, collision_directions

while 1: # game loop
    # fill screen each iter to not leave trail of images moving on screen
    display.fill((0, 200, 200))

    # make scroll follow player
    # adjust to center display on player (half display w/h + half player w/h)
    display_xcenter = 152
    display_ycenter = 106
    true_scroll[0] += (player_rect.x - true_scroll[0] - display_xcenter)/16
    true_scroll[1] += (player_rect.y - true_scroll[1] - display_ycenter)/10
    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0]) # convert to ints to avoid visual tearing of tiles
    scroll[1] = int(scroll[1])

    # drawing parallax scrolling
    pygame.draw.rect(display, (7, 80, 75), pygame.Rect(0, 120, 300, 80))
    for bg_obj in background_objects: # base data * distance scalar for x, & y, obj width, obj height
        obj_rect = pygame.Rect(bg_obj[1][0] - scroll[0] * bg_obj[0],
                                bg_obj[1][1] - scroll[1] * bg_obj[0],
                                bg_obj[1][2], bg_obj[1][3])
        if bg_obj[0] == 0.5:
            pygame.draw.rect(display, (14, 222, 150), obj_rect)
        else:
            pygame.draw.rect(display, (10, 90, 80), obj_rect)

    # render game map iterating through each cell of 2D game map
    tile_rects = []
    y = 0
    for row in game_map:
        x = 0
        for tile in row:
            # x and y are coordinates of tiles in map,
            # mult by size of image to get screen coordinate for placement
            if tile == '1':
                display.blit(dirt_img, (x*TILE_SIZE-scroll[0], y*TILE_SIZE-scroll[1]))
            if tile == '2':
                display.blit(grass_img, (x*TILE_SIZE-scroll[0], y*TILE_SIZE-scroll[1]))
            if tile != '0':
                # need to keep track of ground tiles for collision physics later
                tile_rects.append(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            x += 1
        y += 1

    # update movement velocity (not position)
    player_mvmt = [0, 0]
    if moving_right:
        player_mvmt[0] += 2
    if moving_left:
        player_mvmt[0] -= 2
    player_mvmt[1] += player_ymomentum
    player_ymomentum += 0.4
    if player_ymomentum > 3:
        player_ymomentum = 3

    # set action for player animations
    if player_mvmt[0] > 0:
        player_action, player_frame = change_action(player_action, player_frame, 'run')
        player_flip = False
    if player_mvmt[0] == 0:
        player_action, player_frame = change_action(player_action, player_frame, 'idle')
    if player_mvmt[0] < 0:
        player_action, player_frame = change_action(player_action, player_frame, 'run')
        player_flip = True

    # call move function on player
    player_rect, collisions = move(player_rect, player_mvmt, tile_rects)

    # check for touching floor collisions for falling off ledges,
    # ait timer improves floor collision physics
    if collisions['bottom'] == True:
        player_ymomentum = 0
        air_timer = 0
    else:
        air_timer += 1

    if collisions['left'] == True or collisions['right'] == True:
        air_timer = 1

    # touching ceiling collision for jumping and hitting head
    if collisions['top'] == True:
        player_ymomentum = 0

    # coords increase from top left, to bottom right
    player_frame += 1
    if player_frame >= len(anim_db[player_action]):
        player_frame = 0
    # access the img id corresponding to the player_frame of the current action
    player_img_id = anim_db[player_action][player_frame]
    # access the id of the loaded images list
    player_img = animation_frames[player_img_id]
    display.blit(pygame.transform.flip(player_img, player_flip, False), (player_rect.x - scroll[0], player_rect.y - scroll[1])) # put img loaded onto screen

    for event in pygame.event.get(): # event loop
        if event.type == pygame.QUIT: # check for window quit
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN: # when keydown, set movements True
            if event.key == pygame.K_RIGHT: # move right
                moving_right = True
            if event.key == pygame.K_LEFT: # move left
                moving_left = True
            if event.key == pygame.K_SPACE: # jump
                # player has 6 frames allotted air time before jumping
                if air_timer <= 6:
                    player_ymomentum = -5
        if event.type == pygame.KEYUP: # when keyup, set movements False
            if event.key == pygame.K_RIGHT:
                moving_right = False
            if event.key == pygame.K_LEFT:
                moving_left = False
                
    # scale display size to the size of screen
    screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0, 0))
    pygame.display.update() # update display
    clock.tick(FPS) # maintain framerate