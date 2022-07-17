import pygame, sys
import random as rand
import framework as f
import engine as e

# initializers and global constants
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.set_num_channels(32) # sets how many different sounds can play at once
clock = pygame.time.Clock()
FPS = 60
WINDOW_SIZE = (800, 600)
# surfaces are just images
# write all onto display, to scale up to screen size for consistency
screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)
display = pygame.Surface((300, 200))
pygame.display.set_caption("Le Geam")
f.load_animations('data/entities/')

# declaring initial variables for use in game loop
grass_sfx_timer = 0 # time between playing grass walking sfx
player_loc = [50,50] # initial location of player
moving_left = False
moving_right = False
player_ymomentum = 0 
air_timer = 0 # delay timer to improve jumping
true_scroll = [0,0] # move tiles for scrolling screen
# parallax scrolling, first value scalar to change how fast it moves,
# second value is pygame rect object (x, y, w, h)
# lower scalar values move quicker (render them first!!)
background_objects = [[0.25,[120,10,70,400]],[0.25,[280,30,40,400]],
                    [0.5,[30,40,40,400]],[0.5,[130,90,100,400]],[0.5,[300,80,120,400]]]

# load images
player_img = pygame.image.load("data/imgs/playera.png")
grass_img = pygame.image.load("data/imgs/grass.png")
dirt_img = pygame.image.load("data/imgs/dirt.png")
plant_img = pygame.image.load("data/imgs/plant.png").convert()
plant_img.set_colorkey((255,255,255))
TILE_SIZE = grass_img.get_width()

tile_ind = {1:grass_img,
            2:dirt_img,
            3:plant_img}

# load sounds
jump_sfx = pygame.mixer.Sound("data/sounds/jump.wav")
jump_sfx.set_volume(0.4)
grass_sfx = [pygame.mixer.Sound("data/sounds/grass_0.wav"), pygame.mixer.Sound("data/sounds/grass_1.wav")]
grass_sfx[0].set_volume(0.3)
grass_sfx[1].set_volume(0.3)
pygame.mixer.music.load("data/sounds/music.wav")
# paramater is how many times music plays, -1 is indefinite
pygame.mixer.music.play(-1)

# declare entities
player = f.entity(100, 100, player_img.get_width(), player_img.get_height(), 'player')

# old method of map generation using 2D list from text file
def load_map(path): # game_map[y][x]
    with open(path + ".txt", 'r') as fp:
        line_data = fp.read().split('\n')
        map = []
        for row in line_data:
            map.append(list(row))
    return map
#game_map = load_map("maps/map")

# infinite world gen
# chunks are put into a dictionary, each chunk is a list of tiles
CHUNK_SIZE = 8
def gen_chunk(x, y):
    chunk_data = []
    for y_pos in range(CHUNK_SIZE):
        for x_pos in range(CHUNK_SIZE):
            target_x = x * CHUNK_SIZE + x_pos # real pos for the tiles
            target_y = y * CHUNK_SIZE + y_pos # as the x and are loc of chunks, not tiles
            tile_type = 0 # air tile
            if target_y > 10:
                tile_type = 2 # dirt
            elif target_y == 10:
                tile_type = 1 # grass
            elif target_y == 9 and rand.randint(1,3) == 1:
                tile_type = 3 # plants

            if tile_type != 0:
                chunk_data.append([[target_x, target_y], tile_type])
    return chunk_data
# will look as follows:
# {'1;1':chunk_data, '1;2':chunk_data}
game_map = {}

while 1: # game loop
    # fill screen each iter to not leave trail of images moving on screen
    display.fill((0, 200, 200))

    # sfx for walking on grass
    if grass_sfx_timer > 0:
        grass_sfx_timer -= 1

    # make scroll follow player
    # adjust to center display on player (half display w/h + half player w/h)
    display_xcenter = 152
    display_ycenter = 106
    true_scroll[0] += (player.x - true_scroll[0] - display_xcenter)/16
    true_scroll[1] += (player.y - true_scroll[1] - display_ycenter)/10
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
    ''' Old rendering using a game map txt file
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
        '''

    # displaying the infinite rendering
    # 1 tile is 16x16 pixels, 8 tiles per chunk, means 128x128 pixels per chunk rendered
    # display size is 300x200, 300/128 = 2.34375, 200/128 = 1.5625
    # round up and add 1 for number of chunks to render at a time
    # calculate chunk id's and send to render function
    for y in range(3):
        for x in range(4):
            # x, y relative locations based on window
            # -1 bc location of each chunk is based on the top left corner of each chunk, so more chunks rendered on right ow
            target_x = x - 1 + int(round(scroll[0]/(CHUNK_SIZE*TILE_SIZE)))
            target_y = y - 1 + int(round(scroll[1]/(CHUNK_SIZE*TILE_SIZE)))
            target_chunk = str(target_x) + ';' + str(target_y)
            if target_chunk not in game_map:
                game_map[target_chunk] = gen_chunk(target_x, target_y)
            for tile in game_map[target_chunk]:
                display.blit(tile_ind[tile[1]], (tile[0][0]*TILE_SIZE-scroll[0], tile[0][1]*TILE_SIZE-scroll[1]))
                if tile[1] in [1,2]:
                    # append dirt and grass rectangles to collideable tile list
                    tile_rects.append(pygame.Rect(tile[0][0]*TILE_SIZE, tile[0][1]*TILE_SIZE, TILE_SIZE, TILE_SIZE))

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
        player.set_action('run')
        player.set_flip(False)
    if player_mvmt[0] == 0:
        player.set_action('idle')
    if player_mvmt[0] < 0:
        player.set_action('run')
        player.set_flip(True)

    # call move function on player
    collision_types = player.move(player_mvmt, tile_rects)

    # check for touching floor collisions for falling off ledges,
    # ait timer improves floor collision physics
    if collision_types['bottom'] == True:
        player_ymomentum = 0
        air_timer = 0
        if player_mvmt[0] != 0 and grass_sfx_timer == 0:
            grass_sfx_timer = 20
            rand.choice(grass_sfx).play()
    else:
        air_timer += 1

    if collision_types['left'] == True or collision_types['right'] == True:
        air_timer = 1

    # touching ceiling collision for jumping and hitting head
    if collision_types['top'] == True:
        player_ymomentum = 0

    player.change_frame(1)
    player.display(display, scroll)

    # react to key press/release events
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
                    jump_sfx.play()
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