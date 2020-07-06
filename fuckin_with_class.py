'''
https://pastebin.com/TvdVNr0B
'''

import pygame
import math
import random
import time

pygame.init()


''''setup'''



#define colors
background_color = black_col = (0,0,0)
white_col = (255,255,255)


#initialize screen
(width, height) = (1100, 700)

num_of_chunks = 8
(chunk_width, chunk_height) = (width//num_of_chunks, height//num_of_chunks)

chunk_buffer = 2

screen = pygame.display.set_mode((width, height))
screen_paused = pygame.Surface((width, height))
static_screen = pygame.Surface((width, height))

testing_num = 0

#make a rect hold balls inside
ball_range_xy = (1100, 500) #maximum length
ball_min_x, ball_min_y = (int((width-ball_range_xy[0])/2), int((height-ball_range_xy[1])/2))
ball_screen_rect = pygame.Rect(ball_min_x, ball_min_y, ball_range_xy[0], ball_range_xy[1])

screen.fill(background_color)
pygame.display.set_caption('Bounce')
pygame.font.init()

static_screen.fill(black_col)

# framerate control clock
clock = pygame.time.Clock()
current_FPS = 60


'''classes'''

class vec:
    #take a 2 element list as coordinates for vec
    def __init__(self, xy):
        self.x = xy[0]
        self.y = xy[1]
    #print a vector
    def printv(self):
        print(self.x, self.y)
    #multiply a vector by a scalar
    def scalar(self, s):
        return vec([self.x * s, self.y * s])
    #add two vectors
    def plus(self, b):
        return vec([self.x + b.x, self.y + b.y])
    #subtract two vectors
    def minus(self, b):
        return vec([self.x - b.x, self.y - b.y])
    #vec.dot two vectors
    def dot(self,b):
        return self.x*b.x + self.y*b.y
    def mag(self):
        return math.sqrt(self.x**2 + self.y**2)


class ball: #main class handling all balls

    def __init__(self, i, j, Na):
        self.pos = vec([i, j])
        self.vel = vec([random.uniform(-2,2), random.uniform(-2,2)])
        if Na:
            self.act_img = Na_ion_img
        else:
            self.act_img = K_ion_img
        self.ball_img = pygame.transform.smoothscale(self.act_img, (2*radius, 2*radius))
        self.ball_rect = self.ball_img.get_rect()
        self.ball_rect.center = (self.pos.x, self.pos.y)
        
        self.chunks_in = []
        self.unmoved = True
        self.elem = Na
        
        self.in_pump = None
        self.target_pos = None

    def chunking (self, chunk_dict):
        self.unmoved = True
        self.chunks_in.clear()
        chunk_x = divmod(self.pos.x,chunk_width)
        chunk_y = divmod(self.pos.y,chunk_height)
        self.chunks_in.append("{}{}".format(chunk_x[0], chunk_y[0]))
        if chunk_x[1] >= chunk_width - radius - chunk_buffer and chunk_x[0] != num_of_chunks:
            self.chunks_in.append("{}{}".format(chunk_x[0]+1, chunk_y[0]))
        elif chunk_x[1] <= radius + chunk_buffer and chunk_x[0] != 0:
            self.chunks_in.append("{}{}".format(chunk_x[0]-1, chunk_y[0]))
        if chunk_y[1] >= chunk_width - radius - chunk_buffer and chunk_x[0] != 0:
            self.chunks_in.append("{}{}".format(chunk_x[0], chunk_y[0]+1))
        elif chunk_y[1] <= radius + chunk_buffer and chunk_y[0] != num_of_chunks:
            self.chunks_in.append("{}{}".format(chunk_x[0], chunk_y[0]-1))

        for item in self.chunks_in:
            if chunk_dict.get(item) == None:
                chunk_dict[item] = [self]
            else:
                chunk_dict[item].append(self)


    def Check_Walls(self, click_state, wallist):
        pump = self.in_pump
        if pump != None:
            self.ball_in_pump(pump)
            return
        top = (top_wally-radius, top_wally+wall_width+radius)
        bottom = (bottom_wally-radius, bottom_wally+wall_width+radius)
        
        if top[0] < self.pos.y < top[1] or bottom[0] < self.pos.y < bottom[1]:
            collision = self.check_static_coll(static_dict)
            if collision:
                return
            if top[0] < self.pos.y < top[1]:
                if top[0] < self.pos.y < top[0] + 4:
                    self.pos.y = top[0]
                    self.vel, nothing = new_velocities(self.vel, vec([0,0]), -1, vec([0,-1]))
                    return
                elif top[1] - 4 < self.pos.y < top[1]:
                    self.pos.y = top[1]
                    self.vel, nothing = new_velocities(self.vel, vec([0,0]), -1, vec([0,1]))
                    return
                
            elif bottom[0] < self.pos.y < bottom[1]:
                if bottom[0] < self.pos.y < bottom[0] + 4:
                    self.pos.y = bottom[0]
                    self.vel, nothing = new_velocities(self.vel, vec([0,0]), -1, vec([0,-1]))
                    return
                elif bottom[1] - 4 < self.pos.y < bottom[1]:
                    self.pos.y = bottom[1]
                    self.vel, nothing = new_velocities(self.vel, vec([0,0]), -1, vec([0,1]))
                    return
                     #check if ball is within either set of wall y values
        
        elif top[0]-20 < self.pos.y < top[1]+20 or bottom[0]-20 < self.pos.y < bottom[1]+20:
            for pump in static_dict["pumps"]:                    
                self.pump_collision(pump)
                        
        if self.pos.x > ball_screen_rect.right - radius : #right walls
            self.pos.x = ball_screen_rect.right - radius #ensure ball can't get stuck within walls
            self.vel, nothing = new_velocities(self.vel, vec([0,0]), -1, vec([-1,0]))
        elif self.pos.x < ball_screen_rect.left + radius: #left walls
            self.pos.x = ball_screen_rect.left + radius
            self.vel, nothing = new_velocities(self.vel, vec([0,0]), -1, vec([1,0]))  
        elif self.pos.y > ball_screen_rect.bottom - radius : #right walls
            self.pos.y = ball_screen_rect.bottom - radius #ensure ball can't get stuck within walls
            self.vel, nothing = new_velocities(self.vel, vec([0,0]), -1, vec([0,-1]))
        elif self.pos.y < ball_screen_rect.top + radius: #left walls
            self.pos.y = ball_screen_rect.top + radius
            self.vel, nothing = new_velocities(self.vel, vec([0,0]), -1, vec([0,1]))  

    def check_static_coll(self, static_dict):              
        if click_state["Na_channel_open"]:
            if self.elem:
                for (w, elem) in static_dict["channels"]:
                    if elem:
                        if w.left+radius - 4 < self.pos.x < w.right-radius + 4:
                            if w.left - 4 < self.pos.x - radius < w.left:
                                self.pos.x = w.left + radius
                                self.vel, nothing = new_velocities(self.vel, vec([0,0]), -1, vec([1,0]))
                            elif w.right < self.pos.x + radius < w.right +4:
                                self.pos.x = w.right - radius
                                self.vel, nothing = new_velocities(self.vel, vec([0,0]), -1, vec([-1,0]))
                            return True
        elif click_state["Na_channel_open"]:
            if self.elem:
                for (w, elem) in static_dict["channels"]:
                    if elem:
                        if w.left+radius - 4 < self.pos.x < w.right-radius + 4:
                            if w.left - 4 < self.pos.x - radius < w.left:
                                self.pos.x = w.left + radius
                                self.vel, nothing = new_velocities(self.vel, vec([0,0]), -1, vec([1,0]))
                            elif w.right < self.pos.x + radius < w.right +4:
                                self.pos.x = w.right - radius
                                self.vel, nothing = new_velocities(self.vel, vec([0,0]), -1, vec([-1,0]))
                            return True
        
            
    def ball_in_pump (self, pump):
        if self.target_pos == pump.target_pos_active:
            point = pump.target_pos_active
            dist = vec.mag(vec.minus(self.pos, point))
            if dist <= .5:
                self.vel = vec((0,0))
                self.pos = point
                pump.target_pos_index += 1
                if pump.target_pos_index == 3:
                    pump.angle_counter += 1
                    if pump.upper:
                        pump.active_hitbox = pump.hitbox_lower
                    else:
                        pump.active_hitbox = pump.hitbox_upper
                if pump.target_pos_index < 5:
                    pump.target_pos_active = pump.list_of_targets[pump.target_pos_index]
                    pump.accepting_balls = True
                elif pump.target_pos_index == 5:
                    pump.angle_counter += 1
                    pump.target_pos_active = pump.list_of_targets[0]
                    if pump.upper:
                        pump.active_hitbox = pump.hitbox_upper
                    else:
                        pump.active_hitbox = pump.hitbox_lower
        if pump.target_pos_index == 3 and pump.accepting_elem:
            if self.target_pos != None:
                if pump.upper:
                    self.vel = vec([.1,-1])
                else:
                    self.vel = vec([.1, 1])
                self.target_pos = None
            else:
                point = pump.active_hitbox
                dist = vec.mag(vec.minus(self.pos, point))
                if dist >= 40:
                    self.in_pump = None
                    pump.ball_in.remove(self)
                    if not pump.ball_in:
                        pump.accepting_balls = True
                        pump.accepting_elem = False
        elif pump.target_pos_index == 5 and not pump.accepting_elem:
            if self.target_pos != None:
                if pump.upper:
                    self.vel = vec([.1,1])
                else:
                    self.vel = vec([.1,-1])
                self.target_pos = None
            else:
                point = pump.active_hitbox
                dist = vec.mag(vec.minus(self.pos, point))
                if dist >= 40:
                    self.in_pump = None
                    pump.ball_in.remove(self)
                    if not pump.ball_in:
                        pump.accepting_balls = True
                        pump.accepting_elem = True
                        pump.target_pos_index = 0
                        
    def pump_collision(self, pump):
        
        if pump.accepting_balls and pump.accepting_elem == self.elem:
            point = pump.active_hitbox
            dist = vec.mag(vec.minus(self.pos, point))
            if dist <= 45 + radius:
                point = pump.target_pos_active
                
                self.in_pump = pump
                self.target_pos = point
                self.vel = vec.scalar(vec.minus(point, self.pos), 1/30)
                
                pump.ball_in.append(self)
                pump.accepting_balls = False
                
                return
        
        #if ball collides when busy, bounce        
        point = pump.hitbox_main
        dist = vec.mag(vec.minus(self.pos, point))
        
        if dist < 45 + radius:
            #check to see if the ball is one of the balls active
            for ball in pump.ball_in:
                if ball == self:
                    return
            n = vec.minus(self.pos, point)

            move = radius + 45 - dist
            self.pos = vec.plus(self.pos, vec.scalar(n, move/(vec.mag(n))))
            self.vel, nothing = new_velocities(self.vel, vec([0,0]), -1, n)    
    
    def update(self, chunkscreen):

        #move
        if self.unmoved:
            self.pos = vec.plus(self.pos, self.vel)
            self.unmoved = False

        #collide with walls
        self.Check_Walls(click_state, list_of_walls)

        chunkscreen[chunk].remove(self)
        
        if self.in_pump != None:
            return

        for b in chunkscreen[chunk]:
            if b.in_pump != None:
                continue
            dist = vec.mag(vec.minus(b.pos, self.pos))
            if dist < 2*radius and b is not self:
                #axis of collision
                n = vec.minus(self.pos, b.pos)
                #move the balls apart so they don't get stuck together
                move = 2*radius - dist
                self.pos = vec.plus(self.pos, vec.scalar(n, move/(2*vec.mag(n))))
                b.pos = vec.plus(b.pos, vec.scalar(n, -move/(2*vec.mag(n))))
                #compute new velocities    
                self.vel, b.vel = new_velocities(self.vel, b.vel, 1, n)
        
    def draw(self):
        self.ball_rect.center = (int(self.pos.x), int(self.pos.y))
        screen.blit(self.ball_img, self.ball_rect)


class ion_pump:
    def __init__(self, coord, upper):
        #60, 220
        self.coord = coord
        self.act_img_l = pygame.image.load(r'images\ion_pump_l2.png')
        self.act_img_l = pygame.transform.smoothscale(self.act_img_l, (22, 80))
        self.act_rect_l = self.act_img_l.get_rect()
        #pump_rect_l.center = (69, 250)
        self.act_rect_l.center = (coord[0]+9, coord[1]+30)
        
        self.act_img_cu = pygame.image.load(r'images\ion_pump_cu.png')
        self.act_img_cu = pygame.transform.smoothscale(self.act_img_cu, (60, 80))
        self.act_rect_cu = self.act_img_cu.get_rect()
        #pump_rect_r.center = (113, 250)
        self.act_rect_cu.center = (coord[0]+30, coord[1]+30)
        
        self.act_img_cm = pygame.image.load(r'images\ion_pump_cm.png')
        self.act_img_cm = pygame.transform.smoothscale(self.act_img_cm, (60, 80))
        self.act_rect_cm = self.act_img_cm.get_rect()
        #pump_rect_r.center = (113, 250)
        self.act_rect_cm.center = (coord[0]+30, coord[1]+30)
        
        self.act_img_cl = pygame.image.load(r'images\ion_pump_cl.png')
        self.act_img_cl = pygame.transform.smoothscale(self.act_img_cl, (60, 80))
        self.act_rect_cl = self.act_img_cl.get_rect()
        #pump_rect_r.center = (113, 250)
        self.act_rect_cl.center = (coord[0]+30, coord[1]+30)
        
        self.list_of_img = [(self.act_img_cl, self.act_rect_cl), (self.act_img_cm, self.act_rect_cm), (self.act_img_cu, self.act_rect_cu)]
        
        self.act_img_r = pygame.image.load(r'images\ion_pump_r2.png')
        self.act_img_r = pygame.transform.smoothscale(self.act_img_r, (22, 80))
        self.act_rect_r = self.act_img_r.get_rect()
        #pump_rect_r.center = (113, 250)
        self.act_rect_r.center = (coord[0]+53, coord[1]+30)

        self.upper = upper
        if upper:
            angle = 340
            self.image_c = self.list_of_img[2][0]
            self.rect_c = self.list_of_img[2][1]
        else:
            angle = 20
            self.image_c = self.list_of_img[0][0]
            self.rect_c = self.list_of_img[0][1]

        #put into initial rotation
        self.image_l = pygame.transform.rotozoom(self.act_img_l, angle, 1)
        self.rect_l = self.image_l.get_rect()
        self.rect_l.center = self.act_rect_l.center
        self.image_r = pygame.transform.rotozoom(self.act_img_r, 360-angle, 1)
        self.rect_r = self.image_r.get_rect()
        self.rect_r.center = self.act_rect_r.center
        
        self.angle_counter = 0
        
        self.hitbox_upper = vec((coord[0]+30,coord[1]+40))
        self.hitbox_lower = vec((coord[0]+30,coord[1]+20))
        self.hitbox_main = vec((coord[0]+30,coord[1]+30))
        
        self.ion_pos = None
        self.ball_in = []
        self.accepting_balls = True
        self.accepting_elem = True
        
        if upper:
            self.top_open = False
            self.list_of_targets = [vec((self.coord[0] + 13, self.coord[1] + 53)), \
                                    vec((self.coord[0] + 21, self.coord[1] + 33)), \
                                    vec((self.coord[0] + 29, self.coord[1] + 13)), \
                                    vec((self.coord[0] + 45, self.coord[1] + 16)), \
                                    vec((self.coord[0] + 40, self.coord[1] + 39))]
            self.active_hitbox = self.hitbox_upper
        
        else:
            self.top_open = True
            self.list_of_targets = [vec((self.coord[0] + 28, self.coord[1] + 44)), \
                                    vec((self.coord[0] + 21, self.coord[1] + 26)), \
                                    vec((self.coord[0] + 14, self.coord[1] + 8)), \
                                    vec((self.coord[0] + 45, self.coord[1] + 45)), \
                                    vec((self.coord[0] + 40, self.coord[1] + 20))]
            self.active_hitbox = self.hitbox_lower
        
        self.target_pos_index = 0
        self.target_pos_active = self.list_of_targets[0]

    def update(self):
        if 1 <= self.angle_counter < 30:
            angle = self.angle_counter*4/3
            if self.upper:
                angle = 340 + angle
            else:
                angle = 20 - angle
            self.image_l = pygame.transform.rotozoom(self.act_img_l, angle, 1)
            self.rect_l = self.image_l.get_rect()
            self.rect_l.center = self.act_rect_l.center

            self.image_r = pygame.transform.rotozoom(self.act_img_r, 360-angle, 1)
            self.rect_r = self.image_r.get_rect()
            self.rect_r.center = self.act_rect_r.center
            
            if self.angle_counter == 10:
                self.image_c = self.list_of_img[1][0]
                self.rect_c = self.list_of_img[1][1]
            elif self.angle_counter == 20:
                if self.upper:
                    self.image_c = self.list_of_img[0][0]
                    self.rect_c = self.list_of_img[0][1]
                else:
                    self.image_c = self.list_of_img[2][0]
                    self.rect_c = self.list_of_img[2][1]
                
            self.angle_counter += 1

        elif 30 < self.angle_counter <= 60:
            angle = (self.angle_counter - 30)*4/3
            if self.upper:
                angle = 380-angle
            else:
                angle += -20
            self.image_l = pygame.transform.rotozoom(self.act_img_l, angle, 1)
            self.rect_l = self.image_l.get_rect()
            self.rect_l.center = self.act_rect_l.center

            self.image_r = pygame.transform.rotozoom(self.act_img_r, 360 - angle, 1)
            self.rect_r = self.image_r.get_rect()
            self.rect_r.center = self.act_rect_r.center
            self.angle_counter += 1

            if self.angle_counter == 40:
                self.image_c = self.list_of_img[1][0]
                self.rect_c = self.list_of_img[1][1]
            elif self.angle_counter == 50:
                if self.upper:
                    self.image_c = self.list_of_img[2][0]
                    self.rect_c = self.list_of_img[2][1]
                else:
                    self.image_c = self.list_of_img[0][0]
                    self.rect_c = self.list_of_img[0][1]
            elif self.angle_counter > 60:
                self.angle_counter = 0

        screen.blit(self.image_c, self.rect_c)
        screen.blit(self.image_l, self.rect_l)
        screen.blit(self.image_r, self.rect_r)
    

        
'''functions'''

def font_func(font_size, font_string, text_color, text_backg, location = (0,0)):
    text_font = pygame.font.SysFont("monospace", font_size)
    text_x = text_font.render(font_string, True, text_color, text_backg)
    text_box = text_x.get_rect()
    text_box = text_box.move(location)
    return text_x, text_box


def new_velocities(v1, v2, m2, n):
    #setp 1 : compute a vector perpendicular to n
    perp_n = vec([-n.y, n.x])

    #step 2 : decompose velocity into componets along n and perp to n
    v1_along_n = vec.dot(v1, n)/(vec.mag(n)**2)
    v1_perp_n = vec.dot(v1, perp_n)/(vec.mag(n)**2)
    
    v2_along_n = vec.dot(v2, n)/(vec.mag(n)**2)
    v2_perp_n = vec.dot(v2, perp_n)/(vec.mag(n)**2)

    #step 3 : bounce the velocities along n
    if m2 == -1: #when m2 == -1 the wall is static
        v1_along_n_after = -v1_along_n
        v2_along_n_after = 0
    else:
        v1_along_n_after = (((v2_along_n - v1_along_n) + v1_along_n + v2_along_n) / (2))
        v2_along_n_after = (((v1_along_n - v2_along_n) + v1_along_n + v2_along_n) / (2))

    #step 4 : combine the components again
    v1_after = vec.plus(vec.scalar(n, v1_along_n_after), vec.scalar(perp_n, v1_perp_n))
    v2_after = vec.plus(vec.scalar(n, v2_along_n_after), vec.scalar(perp_n, v2_perp_n))

    return v1_after, v2_after


#check to see what's clicked
def click(coord):

    for b in butt_texts:
        if butt_texts[b][1].left <= coord[0] <= butt_texts[b][1].right and \
        butt_texts[b][1].top <= coord[1] <= butt_texts[b][1].bottom:
            return b
    for b in dragables:
        if dragables[b][1].left <= coord[0] <= dragables[b][1].right and \
        dragables[b][1].top <= coord[1] <= dragables[b][1].bottom:
            return b

def zoom_func(main_screen, zoom_screen = None):
    mouse_pos = pygame.mouse.get_pos()
    #create a 20 x 20 square around cursor
    zoom_rect = pygame.Rect(mouse_pos[0]-50, mouse_pos[1]-50, 100, 100)
    pygame.draw.rect(main_screen, (255,0,0), zoom_rect, 2)

def FPS_limit(fpsnum):
    #Because the clock.tick(int) can get choppy and now I can lower framerate when paused
    if click_state["Pause"] and click_state["dragables"] == False:
        clock.tick(5)
        return clock.tick()

    if fpsnum == "No Cap":
        return clock.tick()

    else:
        #convert to seconds
        deltat = (clock.tick())/1000
        #conv fps to seconds per frame
        spf = (1/fpsnum)
        if deltat < spf:
            time.sleep(spf-deltat)
            return spf
        return deltat
    

def potential_update(list_o_potentials, list_o_potential_x, balllist, click_state):
        
    if click_state["graph_update"]:
        potential_count = 60
        for ball in balllist:
            if top_wally+wall_width+radius < ball.pos.y < bottom_wally - radius + wall_width:
                potential_count -= 1
            else:
                potential_count += 1
        del list_o_potentials[0]
        list_o_potentials.append(potential_count)
        click_state["graph_update"] = False
    
    pointlist = tuple(zip(list_o_potential_x, list_o_potentials))
    
    pygame.draw.line(screen, (100,100,100), (900, 60), (1020, 60), 1)
    pygame.draw.lines(screen, white_col, False, pointlist, 1)
    screen.blit(text_potential, rect_potential)


def update_graphics(dragables, click_state, deltat):
    
    screen.blit(static_screen, (0,0))
    
    for i in static_dict["pumps"]:
        i.update()

    for b in balls:
        b.draw()

    potential_update(list_o_potentials, list_o_potential_x, balls, click_state)
    
    if click_state["z"]:
        zoom_func(screen)

    current_FPS = dragable_update(dragables, click_state, deltat)
    
    pygame.display.flip()

    return current_FPS


def dragable_update(drag_dict, click_state, deltat):
    
    if click_state["FPS_slider"]:
        mouse_pos = pygame.mouse.get_pos()
        drag_dict["FPS_slider"][1].centerx = mouse_pos[0]
        if drag_dict["FPS_slider"][1].centerx < FPS_range.left:
            drag_dict["FPS_slider"][1].centerx = FPS_range.left
        elif drag_dict["FPS_slider"][1].centerx > FPS_range.right:
            drag_dict["FPS_slider"][1].centerx = FPS_range.right
            
    current_FPS = drag_dict["FPS_slider"][1].centerx - FPS_range.left + 10
    pygame.draw.rect(screen, black_col, (FPS_clear))
    
    text_fps, butt_fps = font_func(20, "Max FPS: {}".format(current_FPS), white_col, black_col, (10,height-70))
    butt_texts["FPS"] = [text_fps, butt_fps]
    pygame.draw.rect(screen, black_col, butt_fps.inflate(20,0))
    if deltat != 0:
        message = str(1/deltat)[:5]
    else:
        message = "inf"
    text_afps, butt_afps = font_func(20, "Actual FPS: {}".format(message), white_col, black_col, (width-330,height-70))
    butt_texts["Actual FPS"] = [text_afps, butt_afps]
    pygame.draw.rect(screen, black_col, butt_fps.inflate(20,0))
    
    for b in butt_texts:
        screen.blit(butt_texts[b][0], butt_texts[b][1])

    for item in drag_dict:
        pygame.draw.rect(screen, drag_dict[item][0], drag_dict[item][1])
    if click_state["Pause"]:
        pygame.display.update([FPS_clear,butt_texts["FPS"][1], butt_fps.inflate(20,0)])    
    
    return current_FPS


def check_events(click_status, drag_dict):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_7:
                    print (pygame.mouse.get_pos())
                if event.key == pygame.K_z:
                    click_status["z"] = not click_status["z"]
                if event.key == pygame.K_a:
                    for i in list_of_pumps:
                        i.angle_counter += 1
                if event.key == pygame.K_j:
                    click_status["Na_channel_open"] = not click_status["Na_channel_open"]
                    click_status["K_channel_open"] = not click_status["K_channel_open"]

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                clicked = click(mouse_pos)
                if clicked in click_status:
                    if clicked in drag_dict:
                        click_status["dragables"] = True
                        if clicked == "FPS_slider" or clicked == "FPS_range":
                            click_status["FPS_slider"] = True
                    else:
                        click_status[clicked] = not click_status[clicked]
                        if clicked == "Pause":
                            if click_status["first_click"] == True:
                                click_status["first_click"] = False
                            else:
                                screen.blit(screen_paused,(0,0))
                                screen.blit(text_start_butt, start_butt)
                                pygame.display.flip()            
    
            elif event.type == pygame.MOUSEBUTTONUP:
                click_status["FPS_slider"] = False
                click_status["dragables"] = False
            if event.type == graph_update:
                click_status["graph_update"] = True

    return True



#ball generator
'''Object Construction'''
#GRAPHS
list_o_potential_x = [width-200+2*i for i in range(60)]
list_o_potentials = [60 for i in range(60)]
graph_update = pygame.USEREVENT + 1
pygame.time.set_timer(graph_update, 2000)
text_potential, rect_potential = font_func(20, "Potential", white_col, black_col, (width-200, 0))

#Button creation
butt_texts = {}
    #in form [text, rect]
dragables = {}
    #in form [color, rect]
list_of_walls =  []

list_of_pumps = []

text_start_butt, start_butt = font_func(20, "Start", black_col, white_col, (25,10))

text_pause_butt, pause_butt = font_func(20, "Pause", black_col, white_col, (25,10))
butt_texts["Pause"] = [text_pause_butt, pause_butt]


''' unused FPS buttons
text_15fps, butt_15fps = font_func(20, "15 FPS", black_col, white_col, (500,10))
butt_texts["15 FPS"] = [text_15fps, butt_15fps]

text_30fps, butt_30fps = font_func(20, "30 FPS", black_col, white_col, (600,10))
butt_texts["30 FPS"] = [text_30fps, butt_30fps]

text_60fps, butt_60fps = font_func(20, "60 FPS", black_col, white_col, (700,10))
butt_texts["60 FPS"] = [text_60fps, butt_60fps]

text_NoCap, butt_NoCap = font_func(20, "No Cap", black_col, white_col, (800,10))
butt_texts["No Cap"] = [text_NoCap, butt_NoCap]
'''
#Dragable construction
FPS_range = pygame.Rect(11,height-30,110,3)
dragables["FPS_range"] = [(255, 0, 255), FPS_range]

FPS_slider = pygame.Rect(FPS_range.left + 46,FPS_range.top - 10, 9, 23)
dragables["FPS_slider"] = [(255,0,255), FPS_slider]


#static objects
FPS_clear = pygame.Rect(FPS_range.left-4,FPS_range.top - 10, 119, 23)



chunk_border_bool = False
if chunk_border_bool:
    for i in range(num_of_chunks):
        k = i+1
        wall_block_i = pygame.Rect(chunk_width*k, 0, 25, height)
        list_of_walls.append(wall_block_i)
      
    for j in range(num_of_chunks):
        k = j+1
        wall_block_j = pygame.Rect(0, chunk_height*k, width, 25)
        list_of_walls.append(wall_block_j)

#pause screen appearance
screen_paused.fill(white_col)

pause_text, pause_box = font_func(100, "Paused", (10,10,10), white_col)
pause_box.center = (width//2, height//2)
screen_paused.blit(pause_text, pause_box)

screen_paused.set_alpha(120)

#screen chunks
screen_chunks = {}

#customize the balls

radius = 12
ball_cols, ball_rows = 14, 8
Na_ion_img = pygame.image.load(r'images\Na_ion.png')
K_ion_img = pygame.image.load(r'images\K_ion.png')

#customize the walls
top_wally, bottom_wally = 225, 450
wall_width, wall_length = 45, 60

#button bools
'''bool flags'''

running = True

first_click = True

click_state = {"Pause":True, "first_click":True, "FPS_slider":False, \
               "FPS_range":False, "dragables": False, "z": False, \
               "graph_update": False, "Na_channel_open": False, "K_channel_open": False}

'''main code'''

balls = set({})
for i in range(ball_cols):
    for j in range(ball_rows):
        x = 6*radius*(i + 1) + ball_screen_rect.left
        y = int(3.8*radius*(j + 1)+ball_screen_rect.top)
        if y // top_wally >= 1:
            y += wall_width
            if y // bottom_wally >= 1:
                y += wall_width
        if y >= ball_screen_rect.bottom:
            break
        if x >= ball_screen_rect.right:
            continue
        ballyboi = ball(x,y,(j+i)%2)
        balls.add(ballyboi)


#static object creation
static_dict = {"walls":[], "pumps":[], "channels":[]}

wall_img = pygame.image.load(r'images/cell_wall.png')
wall_img = pygame.transform.smoothscale(wall_img, (wall_length, wall_width))

for i in range(9):
    wall_block_i = pygame.Rect(ball_screen_rect.left + (wall_length+4*radius+10)*i, top_wally, wall_length, wall_width)
    static_dict["walls"].append(wall_block_i)
    wall_block_j = pygame.Rect(ball_screen_rect.left + (wall_length+4*radius+10)*i, bottom_wally, wall_length, wall_width)
    static_dict["walls"].append(wall_block_j)
    if i%3 == 0:
        ion_pump_i = ion_pump((ball_screen_rect.left + wall_length + (wall_length+4*radius+10)*i, top_wally-5), True)
        static_dict["pumps"].append(ion_pump_i)
        channel_i = pygame.Rect(ball_screen_rect.left + 3*wall_length + (wall_length+4*radius+10)*i, top_wally, wall_length, wall_width)
        static_dict["channels"].append((channel_i,True))
        ion_pump_j = ion_pump((ball_screen_rect.left + wall_length + (wall_length+4*radius+10)*i, bottom_wally-5), False)
        static_dict["pumps"].append(ion_pump_j)
        channel_j = pygame.Rect(ball_screen_rect.left + 3*wall_length + (wall_length+4*radius+10)*i, bottom_wally, wall_length, wall_width)
        static_dict["channels"].append((channel_j,False))


for wall_rect in static_dict["walls"]:
    static_screen.blit(wall_img, wall_rect)

actual_FPS = 5

current_FPS = update_graphics(dragables, click_state, actual_FPS)
pygame.draw.rect(screen, white_col, start_butt)
screen.blit(text_start_butt, start_butt)
pygame.display.update(start_butt)

for b in balls:
    b.chunking(screen_chunks)


while running:

    if click_state["Pause"] == False:

        ballset = balls.copy()

        for chunk in screen_chunks:
            for b in screen_chunks[chunk]:
                b.update(screen_chunks)
        for b in balls:
            b.chunking(screen_chunks)

        current_FPS = update_graphics(dragables, click_state, actual_FPS)

    else:
        if click_state["FPS_slider"] == True:
            current_FPS = dragable_update(dragables, click_state, actual_FPS)

    running = check_events(click_state, dragables)

    actual_FPS = FPS_limit(current_FPS)
 

pygame.quit()