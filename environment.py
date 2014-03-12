import pygame,math,random
from pygame.locals import *
from constants import *
import enemies as Enemy

class TimedEvent(object):
    def __init__(self,time):
        self.time = time
    def get_event(self):
        return pygame.event.Event(TIMEDEVENT,{})
class EnemyAddEvent(object):
    def __init__(self,(time,enem,patt,path,offset)):
##        self.enemy = enem
##        self.pattern = patt
        self.time = time
        self.event = pygame.event.Event(ADD_ENEMY,time = time,pattern = patt,enemy = enem,path = path,offset = offset)
        self.type = ADD_ENEMY
    def __str__(self):
        return repr(self.event)
    def get_event(self):
        return self.event
class EventQueue(object):
    def __init__(self,eventlist = None):
        self.eventlist = eventlist
        self.last = None
    def get_next(self):
        if self.eventlist:
            return self.eventlist[0]
        return None
    next_ = property(get_next)
    def pop(self):
        if len(self.eventlist)>=2:
            val = self.eventlist[0]
            self.eventlist = self.eventlist[1:]
            self.last = val
            return val
        elif len(self.eventlist) == 1:
            val = self.eventlist[0]
            self.eventlist = []
            self.last = val
            return val
        else:
            return None
    def load(self,timeline):
        times = []
        pattern = []
        enemy = []
        path = []
        self.eventlist = []
        for event in timeline:
            parsed = event.split(':')
            parsed = [eval(i) for i in parsed]
            ev = EnemyAddEvent(parsed)
            self.eventlist.append(ev)
    def get_size(self):
        return len(self.eventlist)
    size = property(get_size)
class Explosion(pygame.sprite.Sprite):
    def __init__(self,center,rad = 64):
        pygame.sprite.Sprite.__init__(self)
        self.curr = pygame.time.get_ticks
        self.start = self.curr()
        self.orig_img = pygame.image.load('images/environment/explosion1.png').convert()
        self.orig_img.set_colorkey(BLACK)
        self.orig_img.set_alpha(200)
        self.image = self.orig_img.subsurface(0,0,128,128).copy()
        self.rect = self.image.get_rect(center = center)
        self.max_rad = rad
        self.x,self.y = center
        c = random.randrange(2)
        self.sound = None
        if c == 0:
            self.sound = pygame.mixer.Sound('sound/explosionA.wav')
        else:
            self.sound = pygame.mixer.Sound('sound/explosionB.wav')
        self.sound.set_volume(.5)
        self.sound.play(maxtime = int(math.pi*200))
    def update(self):
        t = (self.curr()-self.start)/200
        self.set_image()
        self.y += 0.5
        self.rect.center = (self.x,self.y)
        if t > math.pi:
            self.sound.stop()
            self.sound.set_volume(0.0)
            del self.sound
            self.kill()
    def set_image(self):
        dim = int(self.max_rad*math.sin((self.curr()-self.start)/200.0))
        frame = ((self.curr()-self.start)/10)%2
        timg = self.orig_img.subsurface(0,128*frame,128,128)
        self.image.fill(BLACK)
        if dim > 0:
            new_img = pygame.transform.scale(timg,(dim,dim))
            new_rect = new_img.get_rect(center = (64,64))
            if dim < 128:
                self.image.blit(new_img,new_rect)
            else:
                self.image = timg
                self.rect = self.image.get_rect(center = (self.x,self.y))
        self.image.set_colorkey(BLACK)
        self.mask = pygame.mask.from_surface(self.image)
    #image = property(get_image)
##    def get_rect(self):
##        return self.image.get_rect(center = self.center)
##    rect = property(get_rect)

class Bullet(pygame.sprite.Sprite):
    def rot_center(self,image,angle):
        """rotate an image while keeping its center"""
        self.image = pygame.transform.rotate(image, angle)
    def __init__(self,loc = (0,0),direc = 0, image = None, vel = 16):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        try:
            self.image = pygame.image.load('images/enemies/EnemyBullet.png').convert()
            self.image = pygame.transform.scale(self.image,(8,8))
            self.image.set_colorkey(BLACK)
        except:
            self.image = pygame.Surface((8,32))
            pygame.draw.rect(self.image,GREEN,(3,0,4,32))
            self.image.set_colorkey(BLACK)
        self.dir = direc
##        if self.dir != 90:
##            self.rot_center(self.image,self.dir-90)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.center = loc
        self.x,self.y = loc
        self.vel = vel
    def update(self,*args):
        self.x +=self.vel*math.cos(math.radians(self.dir))
        self.y -=self.vel*math.sin(math.radians(self.dir))
        self.rect.center = (self.x,self.y)
        if self.x > WIDTH + 32 or self.x < -32 or self.y > HEIGHT+32 or self.y <-32:
            self.kill()
class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self,loc,direc=0,vel=5,path = None,flip = 1,d_dir = 0):
        pygame.sprite.Sprite.__init__(self)
        self.orig_img = pygame.image.load('images/enemies/EnemyBullet.png').convert()
        self.orig_img.set_colorkey(BLACK)
        self.image = self.orig_img.subsurface(0,0,16,16)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.curr = pygame.time.get_ticks
        self.start = self.curr()
        self.vel = vel
        self.direc = direc
        self.x,self.y = loc
        self.path = path
        self.d_dir = d_dir
        if not self.path:
            self.path = Enemy.EnemyPath.paths['L']
        self.flip = flip
    def update(self,*args):
        #frame = ((self.curr()-self.start)/30)%6
        #self.image = self.orig_img.subsurface(0,16*frame,16,16)
        t = (self.curr()-self.start)/100.0
        vel = self.path(t,self.direc,self.vel,self.flip,self.d_dir)
        self.x += vel[0]#math.cos(math.radians(self.direc))*self.vel
        self.y -= vel[1]#math.sin(math.radians(self.direc))*self.vel
        self.rect.center = (self.x,self.y)
        if self.x > WIDTH + 16 or self.x < -16 or self.y > HEIGHT+16 or self.y <-316:
            self.kill()             
class PlayerBullet(pygame.sprite.Sprite):
    def __init__(self,loc=(0,0),direc=0,vel=32):
        pygame.sprite.Sprite.__init__(self)
        self.orig_img = pygame.image.load('images/player/p_bullet.png').convert()
        self.orig_img.set_colorkey(BLACK)
        self.image = self.orig_img.subsurface(0,0,16,16)
        self.image = pygame.transform.rotate(self.image,direc-90)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.curr = pygame.time.get_ticks
        self.start = self.curr()
        self.vel = vel
        self.direc = direc
        self.x,self.y = loc
        self.last_frame = 0
    def update(self,*args):
        frame = ((self.curr()-self.start)/10)%4
        if frame != self.last_frame:
            self.image = self.orig_img.subsurface(0,16*frame,16,16)
            self.last_frame = frame
        self.x += math.cos(math.radians(self.direc))*self.vel
        self.y -= math.sin(math.radians(self.direc))*self.vel
        self.rect.center = (self.x,self.y)
        if self.x > WIDTH + 16 or self.x < -16 or self.y > HEIGHT+16 or self.y <-16:
            self.kill()
class Powerup(pygame.sprite.Sprite):
    def __init__(self,loc):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.Surface((32,32))
##        if self.type_ == 'gun':
##            self.image.fill(RED)
##        elif self.type_ == 'rate':
##            self.image.fill(YELLOW)
        self.x,self.y = loc
        self.rect = self.image.get_rect(center = loc)
    def update(self,*args):
        self.y += 1
        self.rect.center = (self.x,self.y)
class GunUP(Powerup):
    def __init__(self,loc):
        self.type_ = 'gun'
        Powerup.__init__(self,loc)
        self.orig_img = pygame.image.load('images/environment/firepow_up.png').convert()
        self.orig_img.set_colorkey(BLACK)
        self.image = self.orig_img.subsurface(0,0,32,32)
        self.mask = pygame.mask.from_surface(self.image)
        self.last_frame = 0
    def update(self,*args):
        frame = (pygame.time.get_ticks()/100)%2
        if frame != self.last_frame:
            self.image = self.orig_img.subsurface(0,32*frame,32,32)
            self.last_frame = frame
            self.mask = pygame.mask.from_surface(self.image)
        self.y += 1
        self.rect.center = (self.x,self.y)
        if self.rect.top > HEIGHT:
            self.kill()
class RateUP(Powerup):
    def __init__(self,loc):
        self.type_ = 'rate'
        Powerup.__init__(self,loc)
        self.orig_img = pygame.image.load('images/environment/rate_up.png').convert()
        self.orig_img.set_colorkey(BLACK)
        self.image = self.orig_img.subsurface(0,0,32,32)
    def update(self,*args):
        frame = (pygame.time.get_ticks()/100)%2
        if frame != self.last_frame:
            self.image = self.orig_img.subsurface(0,32*frame,32,32)
            self.last_frame = frame
            self.mask = pygame.mask.from_surface(self.image)
        self.y += 1
        self.rect.center = (self.x,self.y)
class RadiusUP(Powerup):
    def __init__(self,loc):
        self.type_ = 'radius'
        Powerup.__init__(self,loc)
        self.orig_img = pygame.image.load('images/environment/bomb_rad_up.png').convert()
        self.orig_img.set_colorkey(BLACK)
        self.image = self.orig_img.subsurface(0,0,32,32)
        self.last_frame = 0
    def update(self,*args):
        frame = (pygame.time.get_ticks()/100)%2
        if frame != self.last_frame:
            self.image = self.orig_img.subsurface(0,32*frame,32,32)
            self.last_frame = frame
            self.mask = pygame.mask.from_surface(self.image)
        self.y += 1
        self.rect.center = (self.x,self.y)
        if self.rect.top > HEIGHT:
            self.kill()
class HealthUP(Powerup):
    def __init__(self,loc):
        self.type_ = 'health'
        Powerup.__init__(self,loc)
        self.orig_img = pygame.image.load('images/environment/health_up.png').convert()
        self.orig_img.set_colorkey(BLACK)
        self.image = self.orig_img.subsurface(0,0,32,32)
        self.last_frame = 0
    def update(self,*args):
        frame = (pygame.time.get_ticks()/100)%2
        if frame != self.last_frame:
            self.image = self.orig_img.subsurface(0,32*frame,32,32)
            self.last_frame = frame
            self.mask = pygame.mask.from_surface(self.image)
        self.y += 1
        self.rect.center = (self.x,self.y)
        if self.rect.top > HEIGHT:
            self.kill()        
if __name__ == '__main__':
    import main
    
    evList = EventQueue()
    f = main.compile_timeline('levels\\testlvel.txt')

    #f = ['0:1:1:1','10:2:1:1']#open('timeline.txt')
    evList.load(f)
    main.main()
    #f.close()
