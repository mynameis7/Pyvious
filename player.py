import pygame, sys, math, random
from pygame.locals import *
#from enemies import *
import environment as Env
from constants import *

class Cursor(object):
    def __init__(self):
        self.image = pygame.Surface((16,16)).convert()
        self.image.fill((255,0,0))
        self.rect = self.image.get_rect(center = (400,400))
        self.x = 400
        self.y = 400
        self.velocity = 0
        self.direction = math.radians(0)
        self.active = True
        self.last_pressed = (0,0,0)
    def update(self):
        if self.active:
            e = math.e
            self.direction = getDirec(self.x, self.y)
            self.dist = getDist(self.x, self.y)
            self.velocity = 7*(1-math.pow(e,-self.dist/100))
            if pygame.key.get_mods()&(KMOD_RSHIFT|KMOD_LSHIFT):
                self.velocity /= 2
##            self.velocity = 10*math.log(getDist(self.x, self.y)+1)/10
            self.x += self.velocity*math.cos(self.direction)
            self.y -= self.velocity*math.sin(self.direction)

        self.rect.center = (self.x, self.y)
##        self.rect = self.rect.clamp(pygame.Rect(0,0,800,600))
        #self.rect = self.rect.clamp()
    def get_pos(self):
        self.update()
        return self.x,self.y
    def set_pos(self,pos):
        self.x,self.y = pos
        self.rect.center = pos
    pos = property(get_pos,set_pos)
    def get_pressed(self):
        self.last_pressed = list(pygame.mouse.get_pressed())
        return pygame.mouse.get_pressed()
    pressed = property(get_pressed)
    def get_released(self):
        rel = [0,0,0]
        for i in xrange(3):
            rel[i] = self.last_pressed[i]^pygame.mouse.get_pressed()[i]
            self.last_pressed[i] = 0
        return rel
    released = property(get_released)
def getDist(headx, heady):
    return math.hypot(pygame.mouse.get_pos()[0] - headx*1.0, pygame.mouse.get_pos()[1] - heady*1.0)

def getDirec(headx, heady):
    dy = (heady - pygame.mouse.get_pos()[1])*1.0
    dx = (pygame.mouse.get_pos()[0] - headx)*1.0
    return math.atan2(dy,dx)

class Target(pygame.sprite.Sprite):
    def __init__(self,loc):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((16,16)).convert()
        pygame.draw.line(self.image,RED,(8,0),(8,16))
        pygame.draw.line(self.image,RED,(0,8),(16,8))
        self.rect = self.image.get_rect(center = loc)
        self.image.set_colorkey(BLACK)
        self.x,self.y = loc
    def update(self):
        self.y += .5
        self.rect.center = (self.x,self.y)
            
class Reticule(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.imgSheet = pygame.image.load('images/player/reticule.png').convert()
        self.imgSheet.set_colorkey(BLACK)
        self.image = self.imgSheet.subsurface(0,0,16,16)
        self.rect = self.image.get_rect()
        #self.image.set_colorkey(BLACK)
    def update(self):
        pass
    def set_image(self,val):
        self.image = self.imgSheet.subsurface(0,16*val,16,16)
class Bomb(pygame.sprite.Sprite):
    def __init__(self,pos):
        pygame.sprite.Sprite.__init__(self)
        self.orig_img = pygame.image.load('images/player/bomb.png').convert()
        self.orig_img.set_colorkey(BLACK)
        self.image = self.orig_img.subsurface(0,0,16,16)
        #pygame.draw.circle(self.image,RED,(4,4),4)
        #self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect(center = pos)
        self.curr = pygame.time.get_ticks
        self.start = self.curr()
        self.active = True
        self.dy = 0
        self.x,self.y = pos
    def update(self,target,*args):
        if self.active:
            self.y -= (self.curr()-self.start)/100.0
            self.y += 0.5
            #self.rect.move_ip(0,-(self.curr()-self.start)/100.0)
            self.dy += abs(-(self.curr()-self.start)/100.0)
            frame = ((self.curr()-self.start)/200)%6
            self.image = self.orig_img.subsurface(0,16*frame,16,16)
            self.rect.center = (self.x,self.y)
            if self.y < target.centery:
                self.active = False
                
class Ship(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.cursor = Cursor()
        self.sheetImg = pygame.image.load('images/player/Ship.png').convert()
        self.image = self.sheetImg.subsurface(0,0,32,32).copy()
        self.rect = self.image.get_rect()
        self.image.set_colorkey(BLACK)
        self.bullets = pygame.sprite.Group()
        self.bomb = pygame.sprite.GroupSingle()
        self.curr = pygame.time.get_ticks
        self.last_shot = 0
        self.mask = pygame.mask.from_surface(self.image)
        self.gun_level = 1
        self.firerate = 0
        self.control = 'mouse'
        self.retic = Reticule()
        self.target = pygame.sprite.GroupSingle()
        self.last_bomb = 0
        self.shot_ready = False
        self.bomb_ready = False
        self.score = 0
        self.health = 10
        self.shield = 10
        self.explos_rad = 128
        self.shots_fired = 0
        self.shots_missed = 0
        self.bombs_fired = 0
        self.bombs_missed = 0
        self.a_enemies_killed = 0
        self.g_enemies_killed = 0
        self.total_enemy_health = 0
        self.enemy_count = 0
        self.shot_cnt = 0
        self.was_hit = 0
        self.invincible = False
        self.burst_cnt = 3
        self.x,self.y = 0,0
        ##joystick stuff
        self.shoot_snd = pygame.mixer.Sound('sound/player_shoot.wav')
        self.bomb_snd = pygame.mixer.Sound('sound/player_bomb.wav')
        pygame.joystick.init()
        try:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
        except:
            pass
        self.tutorial = False
    def get_angles(self,num):
        for i in xrange(num/2):
            yield 30*(math.pow(math.e,-i/2.0))
    def get_firerate(self, max_val = 400,min_val = 300):
        return (max_val - min_val)*math.pow(29/30.0,self.firerate) + min_val
    def update_image(self):
        self.image = self.sheetImg.subsurface(0,32,32,32)
    def get_actions(self):
        pass
    def update(self):
        if self.shield < 10:
            self.shield += 1/60.0
        elif self.shield >= 10:
            self.shield = 10
            
        if self.curr()-self.was_hit < 500:
            self.invincible = True
            if self.curr()/100%2:
                self.image.set_alpha(0)
            else:
                self.image.set_alpha(255)
        if self.invincible == True and self.curr()-self.was_hit>=750:
            self.invincible = False
            self.image.set_alpha(255)
        shoot_var = False
        bomb_var = False
        
        dy = 0
        
        if self.gun_level <1:
            self.gun_level = 1
        if self.control == 'mouse':
            self.rect.center = self.cursor.pos
            self.x,self.y = self.cursor.pos
            if self.cursor.pressed[0]:
                shoot_var = True
            if self.cursor.pressed[2]:
                bomb_var = True
            dy = self.cursor.velocity*math.sin(self.cursor.direction)
        elif self.control == 'joy':
            dx = self.joystick.get_axis(0)
            dy = self.joystick.get_axis(1)
            mult = self.joystick.get_axis(2)
            mult = (-round(mult,3)+3.0)/4.0
            #deadzones
            if abs(dx)<.05:
                dx = 0
            if abs(dy)<.05:
                dy = 0
            angle = math.atan2(dy,dx)
            mag = math.sqrt(dx**2 + dy**2)
            if mag > 1:
                mag = 1
            shoot_var = self.joystick.get_button(0)
            bomb_var = self.joystick.get_button(1)
            self.x += math.cos(angle)*mag*(7*mult)
            self.y += math.sin(angle)*mag*(7*mult)
            self.rect.center = self.x,self.y
            self.cursor.pos = self.x,self.y
            dy = -math.sin(angle)*mag*(4*mult)
        else:
            vel = 5
            keys = []
            total_x = 0
            total_y = 0
            if self.control == 'wasd':
                keys = get_wasd()
                if K_w in keys:
                    total_y += 1
                if K_s in keys:
                    total_y -= 1
                if K_a in keys:
                    total_x -= 1
                if K_d in keys:
                    total_x += 1
                shoot_var = pygame.key.get_pressed()[K_j]
                bomb_var = pygame.key.get_pressed()[K_k]
            elif self.control == 'arrow':
                keys = get_arrow()
                if K_UP in keys:
                    total_y += 1
                if K_DOWN in keys:
                    total_y -= 1
                if K_LEFT in keys:
                    total_x -= 1
                if K_RIGHT in keys:
                    total_x += 1
                shoot_var = pygame.key.get_pressed()[K_z]
                bomb_var = pygame.key.get_pressed()[K_x]

            angle = math.atan2(total_y,total_x)
            if total_x != 0 or total_y != 0:
                v = vel
                if pygame.key.get_mods()&(KMOD_RSHIFT|KMOD_LSHIFT):
                    v /= 2
                dx = v*math.cos(angle)
                dy = v*math.sin(angle)
                self.rect.move_ip(dx,-dy)
##                pygame.mouse.set_pos(self.rect.center)
            self.cursor.pos = self.rect.center
            self.rect.center = self.cursor.rect.center
        if self.control in ('wasd','arrow'):
            dy /=2
        if self.control == 'mouse':
            if not self.cursor.pressed[0]:
                self.shot_ready = True
                self.shot_cnt = 0
            if not self.cursor.pressed[2]:
                self.bomb_ready = True
        if self.control == 'wasd':
            if not pygame.key.get_pressed()[K_j]:
                self.shot_ready = True
                self.shot_cnt = 0
            if not pygame.key.get_pressed()[K_k]:
                self.bomb_ready = True
        if self.control == 'arrow':
            if not pygame.key.get_pressed()[K_z]:
                self.shot_ready = True
                self.shot_cnt = 0
            if not pygame.key.get_pressed()[K_x]:
                self.bomb_ready = True
        if self.control == 'joy':
            if not self.joystick.get_button(0):
                self.shot_Ready = True
                self.shot_cnt = 0
            if not self.joystick.get_button(1):
                self.bomb_ready = True
                
        if not self.shot_ready:
            if self.curr()-self.last_shot > 100 and self.shot_cnt < self.burst_cnt: 
                self.shot_ready = True
            elif self.shot_cnt >= self.burst_cnt:
                self.shot_ready = False
                if self.curr()-self.last_shot > 250:
                    self.shot_cnt = 0
        if not self.tutorial:
            self.rect = self.rect.clamp(pygame.Rect(0,0,800,600))
        else:
            self.rect = self.rect.clamp(pygame.Rect(100,0,800,600))
        self.x,self.y = self.rect.center
        self.retic.rect.center = self.rect.move(0,-150-dy*30.0).center
        
        if shoot_var and self.shot_ready:
            #if self.shot_cnt == 0:
            pygame.mixer.Channel(0).play(self.shoot_snd)
            self.shoot()
            self.last_shot = self.curr()
            self.shot_ready = False
        if bomb_var and (not self.bomb.sprite and (self.curr()-self.last_bomb> 500 or self.last_bomb == 0)) and self.bomb_ready:
            pygame.mixer.Channel(1).play(self.bomb_snd)
            self.bomb.add(Bomb(self.rect.center))
            self.bombs_fired += 1
            self.bombs_missed += 1
            self.target.add(Target(self.retic.rect.center))
            self.last_bomb = self.curr()
            self.bomb_ready = False
        if pygame.mixer.Channel(1).get_busy() and not self.bomb.sprite:
            pygame.mixer.Channel(1).stop()       

##        if self.invincible:
##            self.shot_ready = True
##            self.bomb_ready = True
    def moveto(self,point = (400,500)):
        if self.rect.centerx != point[0]:
            self.x -= math.copysign(0.5,self.x - point[0])
        if self.rect.centery != point[1]:
            self.y -= math.copysign(0.5,self.y -point[1])
        if self.rect.center == point:
            return
        self.rect.center = self.x,self.y
        self.cursor.pos = self.rect.center
    def shoot(self):
        self.shots_fired += self.gun_level
        self.shots_missed += self.gun_level
        vel = 16
        self.shot_cnt += 1
        if self.gun_level == 1:
            self.bullets.add(Env.PlayerBullet(self.rect.midtop,direc = 90, vel = vel))
        elif self.gun_level == 2:
            self.bullets.add(Env.PlayerBullet(self.rect.move(8,0).topleft,direc = 90, vel = vel))
            self.bullets.add(Env.PlayerBullet(self.rect.move(-8,0).topright,direc = 90, vel = vel))
        elif self.gun_level == 3:
            self.bullets.add(Env.PlayerBullet(self.rect.midtop,direc = 90-10, vel = vel))
            self.bullets.add(Env.PlayerBullet(self.rect.midtop,direc = 90, vel = vel))
            self.bullets.add(Env.PlayerBullet(self.rect.midtop,direc = 90+10, vel = vel))
        elif self.gun_level >= 4:
            self.bullets.add(Env.PlayerBullet(self.rect.midtop,direc = 90-12, vel = vel))
            self.bullets.add(Env.PlayerBullet(self.rect.midtop,direc = 90-6, vel = vel))
            self.bullets.add(Env.PlayerBullet(self.rect.midtop,direc = 90, vel = vel))
            self.bullets.add(Env.PlayerBullet(self.rect.midtop,direc = 90+6, vel = vel))
            self.bullets.add(Env.PlayerBullet(self.rect.midtop,direc = 90+12, vel = vel))
##
##        else:
##            if self.gun_level%2:
##                self.bullets.add(Env.PlayerBullet(self.rect.midtop,direc = 90, vel = vel))
##                for i in self.get_angles(self.gun_level-1):
##                    self.bullets.add(Env.PlayerBullet(self.rect.topleft,direc = 90+i, vel = vel))
##                    self.bullets.add(Env.PlayerBullet(self.rect.topright,direc = 90-i, vel = vel))
##            else:
##                self.bullets.add(Env.PlayerBullet(self.rect.topleft,direc = 90, vel = vel))
##                self.bullets.add(Env.PlayerBullet(self.rect.topright,direc = 90, vel = vel))
##
##                for i in self.get_angles(self.gun_level-2):
##                    self.bullets.add(Env.PlayerBullet(self.rect.topleft,direc = 90+i, vel = vel))
##                    self.bullets.add(Env.PlayerBullet(self.rect.topright,direc = 90-i, vel = vel))
        self.last_shot = self.curr()
        
    def get_shoot_accuracy(self):
        if self.shots_fired:
            return float(self.shots_fired-self.shots_missed)/self.shots_fired#*(self.a_enemies_killed/float(self.shots_fired))
        else:
            return 0.0
    shoot_accuracy = property(get_shoot_accuracy)
    def get_bomb_accuracy(self):
        if self.bombs_fired:
            return float(self.bombs_fired-self.bombs_missed)/self.bombs_fired
        else:
            return 0.0
    bomb_accuracy = property(get_bomb_accuracy)
    def kill(self):
        pygame.sprite.Sprite.kill(self)
        self.bullets.empty()
        self.bomb.empty()
def DISP_TEXT(surf,text):
    font_obj = pygame.font.Font(None,20).render(text,True,WHITE)
    surf.blit(font_obj,(0,0))
def get_wasd():
    keys = []
    pressed = pygame.key.get_pressed()
    for i in range(len(pressed)):
        if pressed[i] and i in (K_w,K_s,K_a,K_d):
            keys.append(i)
    return keys
def get_arrow():
    keys = []
    pressed = pygame.key.get_pressed()
    for i in range(len(pressed)):
        if pressed[i] and i in (K_UP,K_DOWN,K_LEFT,K_RIGHT,K_SPACE):
            keys.append(i)
    return keys

wasd = {'[100]':0,
        '[100, 115]':315,
        '[115]':270,
        '[97, 115]':225,
        '[97]':180,
        '[97, 119]':135,
        '[119]':90,
        '[100, 119]':45}
arrow = {'[275]':0,
         '[274, 275]':315,
         '[274]':270,
         '[274, 276]':225,
         '[276]':180,
         '[273, 276]':135,
         '[273]':90,
         '[273, 275]':45}

