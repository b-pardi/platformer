import pygame, sys
import random as rand
import framework as f
import objects as o
#import menus as m

'''
fix menu texts not blitting to buttons
add flickering event for when player touches death balls
add health bar and have it decrease when above occurs
put particles into class
apply particles to occur when damage taken (few)
add rocket launcher
make launcher track mouse direction
physics for launching player via rocket
particles for rocket
enemy death minecraft style where they turn red for a sec and poof away
'''

# initializers and global constants
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.set_num_channels(32) # sets how many different sounds can play at once
clock = pygame.time.Clock()
FPS = 60
click = False
WHITE = (255,255,255)
BLACK = (255, 255, 255)
FONT = pygame.font.Font("data/Pixeled.ttf", 20)
WINDOW_SIZE = (800, 600)
DISPLAY_SIZE = (300, 200)
MONITOR_SIZE = (pygame.display.Info().current_w, pygame.display.Info().current_h)
SCALE_WINDOWED = (WINDOW_SIZE[0]/DISPLAY_SIZE[0], WINDOW_SIZE[1]/DISPLAY_SIZE[1])
SCALE_FULLSCREEN = (MONITOR_SIZE[0]/DISPLAY_SIZE[0], MONITOR_SIZE[1]/DISPLAY_SIZE[1])
# surfaces are just images
# write all onto display, to scale up to screen size for consistency
screen = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
display = pygame.Surface(DISPLAY_SIZE)
pygame.display.set_caption("Le Geam")
f.load_animations('data/entities/')




# load images
player_img = pygame.image.load("data/imgs/playera.png")
grass_img = pygame.image.load("data/imgs/grass.png")
dirt_img = pygame.image.load("data/imgs/dirt.png")
plant_img = pygame.image.load("data/imgs/plant.png").convert()
plant_img.set_colorkey(WHITE)
jumper_img = pygame.image.load("data/imgs/jumper.png").convert()
jumper_img.set_colorkey(WHITE)
TILE_SIZE = grass_img.get_width()
menu_img = pygame.image.load("data/imgs/menus/tree_bg.jpg")
quit_img = pygame.image.load("data/imgs/menus/close.jpg")
options_img = pygame.image.load("data/imgs/menus/options.jpg")
start_img = pygame.image.load("data/imgs/menus/start.jpg")

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
pygame.mixer.music.set_volume(0.2)
# paramater is how many times music plays, -1 is indefinite
pygame.mixer.music.play(-1)

# declare entities
player = f.entity(100, 100, player_img.get_width(), player_img.get_height(), 'player')

enemies = []
for i in range(5):
    y_velocity = 0
    enemy_dim = 13
    enemies.append([y_velocity, f.entity(rand.randint(0,600) - 300, 160, enemy_dim,enemy_dim, 'enemy')])

# declare objects
jumper_objects = []
for i in range(5):
    jumper_objects.append(o.jumper((rand.randint(0,600) - 300, 120), jumper_img))

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

click = False # for menus
def main_menu():
    WINDOW_SIZE = (800, 600)
    scale = SCALE_WINDOWED
    fullscreen = False
    main_menu_text = f.render_text('main menu', FONT, BLACK, 20, 20)
    start_text = f.render_text('Start', FONT, BLACK)
    opt_text = f.render_text('Options', FONT, BLACK)
    screen = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)

    while 1:
        display.fill((0,120,120))
        mx, my = pygame.mouse.get_pos()

        game_button = pygame.Rect(DISPLAY_SIZE[0]/2-25, DISPLAY_SIZE[1]/2-20, 50, 20)
        opt_button = pygame.Rect(DISPLAY_SIZE[0]/2-25, DISPLAY_SIZE[1]/2+20, 50, 20)
        pygame.draw.rect(display, WHITE, game_button)
        pygame.draw.rect(display, WHITE, opt_button)

        if game_button.collidepoint((mx/scale[0], my/scale[1])):
            pygame.draw.rect(display, (20, 200, 20), game_button)
            if click:
                game = Game()
                game.run()
        if opt_button.collidepoint((mx/scale[0], my/scale[1])):
            if click:
                options()

        click = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                if not fullscreen:
                    WINDOW_SIZE = (event.w, event.h)
                    scale = (WINDOW_SIZE[0]/DISPLAY_SIZE[0], WINDOW_SIZE[1]/DISPLAY_SIZE[1])

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode(MONITOR_SIZE, pygame.FULLSCREEN)
                        scale = SCALE_FULLSCREEN
                    else:
                        screen = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
                        scale = SCALE_WINDOWED

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

        if fullscreen:
            screen.blit(pygame.transform.scale(display, MONITOR_SIZE), (0, 0))
        else:
            screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0, 0))
        screen.blit(main_menu_text[0], main_menu_text[1])
        #screen.blit(start_text[0], start_text[1], int(DISPLAY_SIZE[0]/2-25), int(DISPLAY_SIZE[1]/2-20))
        screen.blit(opt_text[0], opt_text[1])

        pygame.display.update()
        clock.tick(60)

def options():
    pass


#[loc, vel, timer]
particles = []


class Game():
    def __init__(self):
        self.grass_sfx_timer = 0
        self.moving_left = False
        self.moving_right = False
        self.player_ymomentum = 0 
        self.air_timer = 0 # delay timer to improve jumping
        self.window_size = (800, 600)
        self.fullscreen = False
        self.clicking = False
        self.mx, self.my = pygame.mouse.get_pos()

        # declaring initial variables for use in game loop
        self.player_loc = [50,50] # initial location of player
        self.true_scroll = [0,0] # move tiles for scrolling screen
        self.enemy_buffer = 4 # num pixels enemy will chase player til (not on top of player)
        # parallax scrolling, first value scalar to change how fast it moves,
        # second value is pygame rect object (x, y, w, h)
        # lower scalar values move quicker (render them first!!)
        self.background_objects = [[0.25,[120,10,70,400]],[0.25,[280,30,40,400]],
                            [0.5,[30,40,40,400]],[0.5,[130,90,100,400]],[0.5,[300,80,120,400]]]

    def run(self):
        running = True
        screen = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
        while running: # game loop
            # fill screen each iter to not leave trail of images moving on screen
            display.fill((0, 200, 200))

            self.mx, self.my = pygame.mouse.get_pos()

            # sfx for walking on grass
            if self.grass_sfx_timer > 0:
                self.grass_sfx_timer -= 1

            # make scroll follow player
            # adjust to center display on player (half display w/h + half player w/h)
            display_xcenter = 152
            display_ycenter = 106
            self.true_scroll[0] += (player.x - self.true_scroll[0] - display_xcenter)/16
            self.true_scroll[1] += (player.y - self.true_scroll[1] - display_ycenter)/10
            scroll = self.true_scroll.copy()
            scroll[0] = int(scroll[0]) # convert to ints to avoid visual tearing of tiles
            scroll[1] = int(scroll[1])

            # drawing parallax scrolling
            pygame.draw.rect(display, (7, 80, 75), pygame.Rect(0, 120, 300, 80))
            for bg_obj in self.background_objects: # base data * distance scalar for x, & y, obj width, obj height
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
            if self.moving_right:
                player_mvmt[0] += 2
            if self.moving_left:
                player_mvmt[0] -= 2
            player_mvmt[1] += self.player_ymomentum
            self.player_ymomentum += 0.4
            if self.player_ymomentum > 3:
                self.player_ymomentum = 3

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
                self.player_ymomentum = 0
                self.air_timer = 0
                if player_mvmt[0] != 0 and self.grass_sfx_timer == 0:
                    self.grass_sfx_timer = 20
                    rand.choice(grass_sfx).play()
            else:
                self.air_timer += 1

            if collision_types['left'] == True or collision_types['right'] == True:
                self.air_timer = 1

            # touching ceiling collision for jumping and hitting head
            if collision_types['top'] == True:
                self.player_ymomentum = 0

            player.change_frame(1)
            player.display(display, scroll)

            # render jumper
            for jumper in jumper_objects:
                jumper.render(display, scroll)
                if jumper.collision_test(player.obj.rect):
                    self.player_ymomentum = -10

            # rendered display used to determine when to render enemies
            rendered_display = pygame.Rect(scroll[0], scroll[1], DISPLAY_SIZE[0], DISPLAY_SIZE[1])

            # render enemies
            for enemy in enemies:
                # process enemy behavior when they collide with the rect that is the current rendered display
                if rendered_display.colliderect(enemy[1].obj.rect):
                    enemy[0] += 0.2
                    if enemy[0] > 4:
                        enemy[0] = 4
                    enemy_mvmt = [0, enemy[0]]
                    if player.x > enemy[1].x + self.enemy_buffer:
                        enemy_mvmt[0] = 1
                    if player.x < enemy[1].x - self.enemy_buffer:
                        enemy_mvmt[0] = -1
                    collision_types = enemy[1].move(enemy_mvmt, tile_rects)
                    if collision_types['bottom'] == True:
                        enemy[0] = 0

                    enemy[1].display(display, scroll)
                    if player.obj.rect.colliderect(enemy[1].obj.rect):
                        self.player_ymomentum = -4

            # particles
            
            if self.clicking:
                for i in range(5):
                    particles.append([[self.mx, self.my], [rand.randint(0, 20)/10 - 1, -2], rand.randint(4, 6)])
            for i, particle in sorted(enumerate(particles), reverse=True):
                # x coord incr by x velocity
                particle[0][0] += particle[1][0]
                particle[0][1] += particle[1][1]
                particle[2] -= 0.1
                particle[1][1] += 0.12
                pygame.draw.circle(display, (150, 0, 150), [int(particle[0][0]), int(particle[0][1])], int(particle[2]))
                if particle[2] <= 0:
                    # must enumerate reverse sorted list when removing during iteration
                    # b/c when removing because of how indexing shifts down, the item after the removed one is skipped
                    particles.pop(i)

            # react to key press/release events
            for event in pygame.event.get(): # event loop
                if event.type == pygame.QUIT: # check for window quit
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.VIDEORESIZE:
                    self.window_size = (event.w, event.h)
                if event.type == pygame.KEYDOWN: # when keydown, set movements True
                    if event.key == pygame.K_RIGHT: # move right
                        self.moving_right = True
                    if event.key == pygame.K_LEFT: # move left
                        self.moving_left = True
                    if event.key == pygame.K_SPACE: # jump
                        # player has 6 frames allotted air time before jumping
                        if self.air_timer <= 6:
                            jump_sfx.play()
                            self.player_ymomentum = -5
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_F11:
                        self.fullscreen = not self.fullscreen
                        if self.fullscreen:
                            screen = pygame.display.set_mode(MONITOR_SIZE, pygame.FULLSCREEN)
                        else:
                            screen = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
                if event.type == pygame.KEYUP: # when keyup, set movements False
                    if event.key == pygame.K_RIGHT:
                        self.moving_right = False
                    if event.key == pygame.K_LEFT:
                        self.moving_left = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = True
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False
                        
            # scale display size to the size of screen
            if self.fullscreen:
                screen.blit(pygame.transform.scale(display, MONITOR_SIZE), (0, 0))
            else:
                screen.blit(pygame.transform.scale(display, self.window_size), (0, 0))
            pygame.display.update() # update display
            clock.tick(FPS) # maintain framerate

main_menu()