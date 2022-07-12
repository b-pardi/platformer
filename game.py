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

# load images
player_img = pygame.image.load("imgs/playera.png")
player_img.set_colorkey((252, 255, 255)) # makes rgb val transp (like greenscreen)
#player_img = pygame.transform.scale(player_img, (40, 40))
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

# game_map[y][x]
game_map = [['0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','2','2','2','2','2','0','0','0','0','0','0','0'],
            ['0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0'],
            ['2','2','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','2','2'],
            ['1','1','2','2','2','2','2','2','2','2','2','2','2','2','2','2','2','1','1'],
            ['1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1'],
            ['1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1'],
            ['1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1'],
            ['1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1'],
            ['1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1']]

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

while 1:
    # fill screen each iter to not leave trail of images moving on screen
    display.fill((0, 200, 200))

    tile_rects = []
    # render game map iterating through each cell of 2D game map
    y = 0
    for row in game_map:
        x = 0
        for tile in row:
            # x and y are coordinates of tiles in map,
            # mult by size of image to get screen coordinate for placement
            if tile == '1':
                display.blit(dirt_img, (x*TILE_SIZE, y*TILE_SIZE))
            if tile == '2':
                display.blit(grass_img, (x*TILE_SIZE, y*TILE_SIZE))
            if tile != '0':
                tile_rects.append(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)) # need to keep track of ground tiles for collision physics later
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

    # call move function on player
    player_rect, collisions = move(player_rect, player_mvmt, tile_rects)

    # check for touching floor collisions for falling off ledges,
    # ait timer improves floor collision physics
    if collisions['bottom'] == True:
        player_ymomentum = 0
        air_timer = 0
    else:
        air_timer += 1

    # touching ceiling collision for jumping and hitting head
    if collisions['top'] == True:
        player_ymomentum = 0

    # coords increase from top left, to bottom right
    display.blit(player_img, (player_rect.x, player_rect.y)) # put img loaded onto screen

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