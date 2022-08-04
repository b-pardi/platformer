import pygame
import math
import os

WHITE = (255, 255, 255)
global animation_higher_db
animation_higher_db = {}
global animation_db
animation_db = {}

'''
Physics
'''

def collision_test(test_obj, obj_list):
    collided = []
    for obj in obj_list:
        if obj.colliderect(test_obj):
            collided.append(obj)
    return collided

class physics_object(object):
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)

    '''
    separate x and y axis, test for each individually
    movement just list x and y of directions moved
    rect is the rectangle being moved, i.e. the player 
    '''
    def move(self, mvmt, platforms):
        # dict to keep track of where collision occurs for later use
        collision_directions = {'top' : False, 'bottom' : False, 'right' : False, 'left' : False, 'data' : []}
        self.x += mvmt[0]
        self.rect.x = int(self.x)
        collided = collision_test(self.rect, platforms)
        for block in collided:
            dir_markers = [False, False, False, False] # marks what side collision occured
            if mvmt[0] > 0: # moving right
                # when player moving right and collides with tile in front of it,
                # put the rect to the left of tile
                self.rect.right = block.left
                collision_directions['right'] = True
                dir_markers[0] = True
            elif mvmt[0] < 0: # moving left
                self.rect.left = block.right
                collision_directions['left'] = True
                dir_markers[1] = True
            collision_directions['data'].append([block, dir_markers])
            self.x = self.rect.x

        # repeat above process for y direction
        self.y += mvmt[1]
        self.rect.y = int(self.y)
        collided = collision_test(self.rect, platforms)
        for block in collided:
            dir_markers = [False, False, False, False]
            if mvmt[1] > 0: # falling down
                self.rect.bottom = block.top
                collision_directions['bottom'] = True
                dir_markers[2] = True
            elif mvmt[1] < 0: # going up
                self.rect.top = block.bottom
                collision_directions['top'] = True
                dir_markers[3] = True
            collision_directions['data'].append([block, dir_markers])
            self.y_change = 0
            self.y = self.rect.y
        return collision_directions

   
# 3D collision handling
class cuboid(object):
    def __init__(self,x,y,z,x_size,y_size,z_size):
        self.x = x
        self.y = y
        self.z = z
        self.x_size = x_size
        self.y_size = y_size
        self.z_size = z_size
        
    def set_pos(self,x,y,z):
        self.x = x
        self.y = y
        self.z = z
        
    def collidecuboid(self,cuboid_2):
        cuboid_1_xy = pygame.Rect(self.x,self.y,self.x_size,self.y_size)
        cuboid_1_yz = pygame.Rect(self.y,self.z,self.y_size,self.z_size)
        cuboid_2_xy = pygame.Rect(cuboid_2.x,cuboid_2.y,cuboid_2.x_size,cuboid_2.y_size)
        cuboid_2_yz = pygame.Rect(cuboid_2.y,cuboid_2.z,cuboid_2.y_size,cuboid_2.z_size)
        if (cuboid_1_xy.colliderect(cuboid_2_xy)) and (cuboid_1_yz.colliderect(cuboid_2_yz)):
            return True
        else:
            return False


'''
Entities
'''

def simple_entity(x,y,e_type):
    return entity(x,y,1,1,e_type)

def flip(img, flip_x=True, flip_y=False):
    flipped = pygame.transform.flip(img, flip_x, flip_y)
    return flipped

def blit_center(target_surface, src_surface, pos):
    x = int(src_surface.get_width()/2)
    y = int(src_surface.get_height()/2)
    target_surface.blit(src_surface, (pos[0]-x, pos[1]-y))

class entity(object):
    global animation_higher_db, animation_db

    def __init__(self, x, y, width, height, entity_type):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.obj = physics_object(x, y, width, height)
        self.animation = None
        self.image = None
        self.cur_animation_frame = 0
        self.animation_tags = []
        self.flip = False
        self.offset = [0,0]
        self.rot = 0
        self.type = entity_type
        self.action_timer = 0
        self.action = ''
        self.set_action('idle')
        self.entity_data = {}
        self.alpha = None

    def set_pos(self, x, y):
        self.x = x
        self.y = y
        self.obj.x = x
        self.obj.y = y
        self.obj.rect.x = x
        self.obj.rect.y = y

    def move(self, momentum, platforms):
        collisions = self.obj.move(momentum, platforms)
        self.x = self.obj.x
        self.y = self.obj.y
        return collisions

    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def set_flip(self, is_flipped):
        self.flip = is_flipped

    def set_animation_tags(self, tags):
        self.animation_tags = tags
 
    def set_animation(self,sequence):
        self.animation = sequence
        self.animation_frame = 0

    def set_action(self, action_id, force=False):
        if (self.action == action_id) and (force == False):
            pass
        else:
            self.action = action_id
            anim = animation_higher_db[self.type][action_id]
            self.animation = anim[0]
            self.set_animation_tags(anim[1])
            self.animation_frame = 0

    def get_entity_angle(self, ent2):
        x1 = self.x+int(self.size_x/2)
        y1 = self.y+int(self.size_y/2)
        x2 = ent2.x+int(ent2.size_x/2)
        y2 = ent2.y+int(ent2.size_y/2)
        angle = math.atan((y2-y1)/(x2-x1))
        if x2 < x1:
            angle += math.pi
        return angle

    def get_center(self):
        x = self.x+int(self.size_x/2)
        y = self.y+int(self.size_y/2)
        return [x,y]
 
    def clear_animation(self):
        self.animation = None
 
    def set_image(self,image):
        self.image = image
 
    def set_offset(self,offset):
        self.offset = offset
 
    def set_frame(self,amount):
        self.animation_frame = amount
 
    def handle(self):
        self.action_timer += 1
        self.change_frame(1)

    def change_frame(self, amt):
        self.animation_frame += amt
        if self.animation != None:
            while self.animation_frame < 0:
                if 'loop' in self.animation_tags:
                    self.animation_frame += len(self.animation)
                else:
                    self.animation = 0

            while self.animation_frame >= len(self.animation):
                if 'loop' in self.animation_tags:
                    self.animation_frame -= len(self.animation)
                else:
                    self.animation_frame = len(self.animation)-1

    def get_cur_img(self):
        if self.animation == None:
            if self.image == None:
                return None
            else:
                return flip(self.image, self.flip)
        else:
            return flip(animation_db[self.animation[self.animation_frame]], self.flip)

    def get_drawn_img(self):
        img_to_render = None
        if self.animation == None:
            if self.image == None:
                return None
            else:
                img_to_render = flip(self.image, self.flip).copy()
        else:
            img_to_render = flip(animation_db[self.animation[self.animation_frame]],self.flip).copy()

        if img_to_render != None:
            x_center = int(img_to_render.get_width()/2)
            y_center = int(img_to_render.get_height()/2)
            if self.rot != None:
                img_to_render = pygame.transform.rotate(img_to_render, self.rot)
            if self.alpha != None:
                img_to_render.set_alpha(self.alpha)
            
            return img_to_render, x_center, y_center

    def display(self, surface, scroll):
        img_to_render = None
        if self.animation == None:
            if self.image != None:
                img_to_render = flip(self.image,self.flip).copy()
        else:
            img_to_render = flip(animation_db[self.animation[self.animation_frame]],self.flip).copy()
        if img_to_render != None:
            center_x = img_to_render.get_width()/2
            center_y = img_to_render.get_height()/2
            img_to_render = pygame.transform.rotate(img_to_render,self.rot)
            if self.alpha != None:
                img_to_render.set_alpha(self.alpha)
            blit_center(surface,img_to_render,(int(self.x)-scroll[0]+self.offset[0]+center_x,int(self.y)-scroll[1]+self.offset[1]+center_y))



'''
Animations
'''

def animation_sequence(seq, base_path, colorkey=WHITE, transparency=255):
    global animation_db
    res = []
    for frame in seq:
        img_id = base_path + base_path.split('/')[-2] + '_' + str(frame[0])
        img = pygame.image.load(img_id + '.png').convert()
        img.set_colorkey(colorkey)
        img.set_alpha(transparency)
        animation_db[img_id] = img.copy()
        for i in range(frame[1]):
            res.append(img_id)
    return res

def get_frame(ID):
    global animation_db
    return animation_db[ID]

# dictionary stores how long the fn of each animation frame,
# and uses frame_durations to track how many game frames each animation frame stays for
def load_animations(path):
    global animation_higher_db
    # loads path to file, takes last dir of path and grabs the name from it
    # naming matches file tree
    with open(path + 'entity_animations.txt', 'r') as f:
        data = f.read()

    for anim in data.split('\n'):
        anim_path, times, tags = anim.split(' ')
        entity_info = anim_path.split('/')
        entity_type, anim_id, *kwargs = entity_info
        times = times.split(';')
        tags = tags.split(';')
        seq = []
        n = 0

        for time in times:
            seq.append([n, int(time)])
            n += 1
        anim = animation_sequence(seq, path+anim_path, WHITE)
        if entity_type not in animation_higher_db:
            animation_higher_db[entity_type] = {}
        animation_higher_db[entity_type][anim_id] = [anim.copy(), tags]

'''
Particle Effects
'''

def particle_file_sort(l):
    l2 = []
    for obj in l:
        l2.append(int(obj[:-4]))
    l2.sort()
    l3 = []
    for obj in l2:
        l3.append(str(obj) + '.png')
    return l3

global particle_images
particle_images = {}

def load_particle_images(path):
    global particle_images, e_colorkey
    file_list = os.listdir(path)
    for folder in file_list:
        try:
            img_list = os.listdir(path + '/' + folder)
            img_list = particle_file_sort(img_list)
            images = []
            for img in img_list:
                images.append(pygame.image.load(path + '/' + folder + '/' + img).convert())
            for img in images:
                img.set_colorkey(e_colorkey)
            particle_images[folder] = images.copy()
        except:
            pass

class particle(object):

    def __init__(self,x,y,particle_type,motion,decay_rate,start_frame,custom_color=None):
        self.x = x
        self.y = y
        self.type = particle_type
        self.motion = motion
        self.decay_rate = decay_rate
        self.color = custom_color
        self.frame = start_frame

    def draw(self,surface,scroll):
        global particle_images
        if self.frame > len(particle_images[self.type])-1:
            self.frame = len(particle_images[self.type])-1
        if self.color == None:
            blit_center(surface,particle_images[self.type][int(self.frame)],(self.x-scroll[0],self.y-scroll[1]))
        else:
            blit_center(surface,swap_color(particle_images[self.type][int(self.frame)],(255,255,255),self.color),(self.x-scroll[0],self.y-scroll[1]))

    def update(self):
        self.frame += self.decay_rate
        running = True
        if self.frame > len(particle_images[self.type])-1:
            running = False
        self.x += self.motion[0]
        self.y += self.motion[1]
        return running


'''
Miscellaneous
'''

def scale_mouse(win_size, disp_size):
    mx, my = pygame.mouse.get_pos()
    mx /= win_size[0]/disp_size[0]
    my /= win_size[1]/disp_size[1]
    return (mx, my)

def render_text(text, font, color, x=0, y=0):
    text_obj = font.render(text, 1, color)
    text_rect = text_obj.get_rect()
    text_rect.topleft = (x , y)
    return (text_obj, text_rect)

def swap_color(img,old_c,new_c):
    global e_colorkey
    img.set_colorkey(old_c)
    surf = img.copy()
    surf.fill(new_c)
    surf.blit(img,(0,0))
    surf.set_colorkey(e_colorkey)
    return surf