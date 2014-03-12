import pygame,math,random
from constants import *
import environment as Env
import player as Player
class Shape(pygame.sprite.Sprite):
    def __init__(self,path,tpe = 'air',pos = (400,0)):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((32,32)).convert()
        pygame.draw.circle(self.image,[RED,BLUE,GREEN][random.randrange(0,3)],(16,16),16)
        self.rect = self.image.get_rect(center = pos)
        self.image.set_colorkey(BLACK)
        self.mask = pygame.mask.from_surface(self.image)
        self.path = path
        self.curr = pygame.time.get_ticks
        self.start = self.curr()
        self.x,self.y = pos
        self.type = tpe
        self.expl_rad = 32
    def update(self,**kwargs):
        vel = self.path((self.curr()-self.start)/10)
        self.x += vel[0]
        self.y += vel[1]
        self.rect.center = (self.x,self.y)
        if self.x < -200 or self.x > WIDTH + 200 or self.y > HEIGHT + 200:
            self.kill()
class AirEnemy(pygame.sprite.Sprite):
    type_ = 'air'
    def __init__(self, path, pos=(400,0), health=1):
        pygame.sprite.Sprite.__init__(self)
        self.orig_img = pygame.image.load('images/enemies/AirEnemy.png').convert()#pygame.Surface((32,32)).convert()
        self.image = self.orig_img
        #pygame.draw.circle(self.image,BLUE,(16,16),16)
        self.rect = self.image.get_rect(center = pos)
        self.image.set_colorkey(BLACK)
        self.mask = pygame.mask.from_surface(self.image)
        self.path = path
        self.curr = pygame.time.get_ticks
        self.start = self.curr()
        self.x,self.y = pos
        self.health = health
        self.val = 100
        self.expl_rad = 64
        self.shot_ready = False
        self.rect = self.image.get_rect(center = pos)
    def update(self,*args):
        vel = self.path((self.curr()-self.start)/10.0)
        self.x += vel[0]/2.0
        self.y += vel[1]/2.0
        direc = math.degrees(math.atan2(-vel[1],vel[0]))
        self.image = pygame.transform.rotate(self.orig_img,direc)
        new_rect = self.image.get_rect(center = (self.x,self.y))
        self.rect = new_rect
        #self.rect.center = (self.x,self.y)
        if self.x < -200 or self.x > WIDTH + 200 or self.y > HEIGHT + 200:
            self.kill()
class Fighter(AirEnemy):
    def __init__(self,path,pos=(400,0),health = 1):
        AirEnemy.__init__(self,path,pos,health)
        self.shot_ready = False
        self.last_shot = self.curr()+random.randrange(0,1000)
        self.orig_img = pygame.image.load('images/enemies/fighter.png').convert()
        self.orig_img.set_colorkey(BLACK)
        self.image = self.orig_img
        self.shot_cnt = 0
    def update(self,player,*args):
        vel = self.path((self.curr()-self.start)/10.0)
        self.x += vel[0]/2.0
        self.y += vel[1]/2.0
        direc = math.degrees(math.atan2(-vel[1],vel[0]))
        self.image = pygame.transform.rotate(self.orig_img,direc)
        new_rect = self.image.get_rect(center = (self.x,self.y))
        self.rect = new_rect
        #self.rect.center = (self.x,self.y)
        if self.x < -200 or self.x > WIDTH + 200 or self.y > HEIGHT + 200:
            self.kill()
        d = math.degrees(math.atan2(self.y-player.y,player.x-self.x))
        if int(d) in xrange(int(direc)-30,int(direc)+31) and self.curr()-self.last_shot > 250 and self.shot_cnt < 5:
            self.shot_ready = True
        if self.shot_cnt > 5:
            self.shot_ready = False
    def shoot(self,player):
        self.shot_ready = False
        self.last_shot = self.curr()
        self.shot_cnt += 1
        vel = self.path((self.curr()-self.start)/10)
        direc = math.degrees(math.atan2(-vel[1],vel[0]))
        bullets = [Env.Bullet(loc = self.rect.center,direc = direc-5+5*i,vel = 3) for i in xrange(3)]
        return pygame.sprite.Group(bullets)#Env.Bullet(loc = self.rect.center,direc = direc,vel = 5)
class GroundEnemy(pygame.sprite.Sprite):
    type_ = 'ground'
    def __init__(self, path, pos=(400,0), health=1):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((32,32)).convert()
        self.rect = self.image.get_rect(center = pos)
        self.image.fill(GREEN)
        pygame.draw.rect(self.image,GREEN,self.rect.inflate(-2,-2))
        self.image.set_colorkey(BLACK)
        self.mask = pygame.mask.from_surface(self.image)
        self.path = path
        self.curr = pygame.time.get_ticks
        self.start = self.curr()
        self.x,self.y = pos
        self.health = health
        self.val = 100
        self.expl_rad = 64
    def update(self,*args):
        vel = self.path((self.curr()-self.start)/10)
        self.x += vel[0]
        self.y += vel[1]
        self.rect.center = (self.x,self.y)
        if self.x < -200 or self.x > WIDTH + 200 or self.y > HEIGHT + 200:
            self.kill()
class Turret(GroundEnemy):
    def __init__(self,path,pos = (400,0),health = 1):
        GroundEnemy.__init__(self,path,pos,health)
        self.orig_img = pygame.image.load('images/enemies/Turret.png').convert()
        self.image = self.orig_img
        self.rect = self.image.get_rect()
        self.image.set_colorkey(BLACK)
        self.mask = pygame.mask.from_surface(self.image)
        self.curr = pygame.time.get_ticks
        self.start = self.curr()
        self.last_shot = self.curr()#+random.randrange(0,1500)
        self.shot_ready = False
        self.val = 500
        self.dir = 0
        self.expl_rad = 64
        self.shot_cnt = 0
    def update(self,player,*args):
        self.rect.center = (self.x,self.y)
        if self.curr()-self.last_shot > 2000:
            self.shot_ready = True
        self.dir = math.degrees(math.atan2(self.y-player.y,player.x-self.x))
        self.image = pygame.transform.rotate(self.orig_img,self.dir)
        new_rect = self.image.get_rect(center = self.rect.center)
        self.rect = new_rect
        self.mask = pygame.mask.from_surface(self.image)
        if self.shot_cnt > 5:
            self.shot_ready = False
        #pygame.draw.lines(pygame.display.get_surface(),GREEN,True,self.mask.outline())
    def shoot(self,player):
        self.shot_ready = False
        self.shot_cnt += 1
        direc = math.degrees(math.atan2(self.y-player.y,player.x-self.x))
        self.last_shot = self.curr()
        return Env.Bullet(loc = self.rect.center,direc = direc,vel = 1)
class Chaser(AirEnemy):
    def __init__(self,path,pos=(400,0),health=1):
        AirEnemy.__init__(self,path,pos,health)
        self.orig_img = pygame.image.load('images/enemies/Chaser.png').convert()
        self.orig_img.set_colorkey(BLACK)
        self.image = self.orig_img.subsurface(0,0,32,32)
        self.direc = 0
        self.expl_rad = 64
    def update(self,player,*args):
        if self.direc == 0:
            self.direc = math.atan2(self.y-player.y,player.x-self.x)
        else:
            ang = math.atan2(self.y-player.y,player.x-self.x)%(2*math.pi)
            diff1 = (ang-self.direc)%(math.pi*2)
            diff2 = (math.pi*2-diff1)%(math.pi*2)
            if diff1 > diff2:      
                self.direc -= .02
            else:
                self.direc += .02
            if self.direc > 2*math.pi: self.direc -= 2*math.pi
            elif self.direc < 0: self.direc += 2*math.pi
        self.x += 2*math.cos(self.direc)
        self.y -= 2*math.sin(self.direc)
        frame = ((self.curr()-self.start)/750)%2
        angle = (self.curr()-self.start)/2%360
        timg = pygame.transform.rotate(self.orig_img.subsurface(0,32*frame,32,32),angle)
        self.image = timg
        self.mask = pygame.mask.from_surface(self.image)
        new_rect = timg.get_rect(center = (self.x,self.y))
        self.rect = new_rect
class Tank(GroundEnemy):
    def __init__(self,path,pos=(400,0),health=1):
        GroundEnemy.__init__(self,path,pos,health)
        self.turret = Turret(EnemyPath.path1,pos)
        self.turret_img = self.turret.image#pygame.transform.scale(self.turret.image,(20,20))
        self.orig_img = pygame.image.load('images/enemies/Tank.png').convert()
        self.orig_img.set_colorkey(BLACK)
        self.path = path
        self.image = self.orig_img
        self.shot_ready = False
    def update(self,player,*args):
        self.shot_ready = self.turret.shot_ready
        vel = self.path((self.curr()-self.start)/40)
        self.x += vel[0]/8.0
        self.y += vel[1]/8.0
        direc = math.degrees(math.atan2(-vel[1],vel[0]))
        self.image = pygame.transform.rotate(self.orig_img,direc)
        self.rect = self.image.get_rect(center = (self.x,self.y))
        turr_loc = (10*math.cos(math.radians(-direc)),16*math.sin(math.radians(-direc)))
        self.turret.x,self.turret.y = self.rect.center
        self.turret.update(player)
        r = self.turret_img.get_rect(topleft = turr_loc)
        #self.image.blit(self.turret.image,r)
        self.mask = pygame.mask.from_surface(self.image)
    def shoot(self,player):
        return self.turret.shoot(player)
class Boss(pygame.sprite.Sprite):
    def __init__(self,level = 1,pos = (400,0)):
        #self.factor = math.pow(1.25,-(level-1))
        pygame.sprite.Sprite.__init__(self)
        self.orig_img = pygame.image.load('images/enemies/boss.png').convert()
        self.orig_img.set_colorkey(BLACK)
        self.image = self.orig_img.subsurface(0,0,128,128)
        self.rect = self.image.get_rect(center = pos)
        self.curr = pygame.time.get_ticks
        self.start = self.curr()
        self.abs_start = self.curr()+3000
        self.max_health = 200 +(level-1)*100
        self.health = self.max_health
        self.direc = 0
        self.last_shot = self.curr()
        self.shot_ready = False
        self.level = level
        self.shooting = False
        self.shot_cnt = 0
        self.burst_cnt = 0
        self.max_cnt = 20
        self.shot_patt = 0
        self.loop_time = 48000
        self.shot_int = 10
        self.x,self.y = pos
        self.returning = True
        self.flip = -1
        self.limit = 1000*60*2 #2 minute to kill boss
        self.val = 10000
        self.bullets = pygame.sprite.Group()
        self.mult = 1/float(level)
        self.d_dir = 0
        self.mask = pygame.mask.from_surface(self.image)
        self.spawn_enem = False
        self.last_spawn = 3500
    def get_charge(self):
        return round((self.curr()-self.abs_start)/float(self.limit),2)
    charge = property(get_charge)
    def move_to(self,loc,vel = 0.5):
        x,y = loc
        if self.rect.centerx != x:
            self.x -= math.copysign(vel,self.x - x)
        if self.rect.centery != y:
            self.y -= math.copysign(vel,self.y - y)
        return self.rect.center == loc
    
    def update_shoot(self,player,t):
        if t > 47000:
            self.shooting = 3
            self.shot_int = 40*2
            self.direc += (2+self.level/100.0)*self.flip
        elif t > 43000:
            self.shooting = 4
            self.shot_int = 100*1.125
            self.direc += (.5+self.level/100.0)*self.flip
        elif t > 42000:
            self.shooting = 1
            self.shot_int = 1000
            self.direc += (1+self.level/100.0)*self.flip
        elif t > 36000:
            self.shooting = 1
            self.direc += (3+self.level/100.0)*self.flip
            self.shot_int = 1000
        elif t > 33750:
            self.shooting = 0
            self.shot_cnt = 0
            self.direc += (3+self.level/100.0)*self.flip
        elif t > 33000:
            self.shooting = 3
            self.shot_int = 25*3
        elif t > 31000:
            self.shooting = 3
            self.shot_int = 50*3
        elif t > 27000:
            self.shooting = 3
            self.shot_int = 100*1.5
        elif t > 25000:
            self.shot_cnt = 0
            self.shooting = 0
            self.shot_int = 100*1.5
        elif t > 23000:
            self.shooting = 2
            self.shot_int = 50*1.5
            self.d_dir = -(.25+self.level/100.0)*self.flip
            self.direc -= (.25+self.level/100.0)*self.flip
        elif t > 22000:
            self.shooting = 0
        elif t>20000:
            self.shooting = 2
            self.shot_int = 50*1.5
            self.d_dir = (.25+self.level/100.0)*self.flip
            self.direc += (.25+self.level/100.0)*self.flip

        elif t>18000:
            self.shooting = 0
            self.shot_int = 100*1.5
            self.direc += (.25+self.level/100.0)*self.flip
        elif t>14000:
            self.shooting = 1
            self.shot_int = 120*1.5
            self.direc += (1/3.0+self.level/100.0)*self.flip
        elif t>8000:
            self.shooting = 1
            self.shot_int = 120*1.5
            self.direc -= (.25+self.level/100.0)*self.flip
        elif t>4000:
            self.shooting = 1
            self.shot_int = 400
            self.direc += (2+self.level/100.0)*self.flip
        elif t>3000:
            self.shooting = 0
            self.direc += (2+self.level/100.0)*self.flip
        elif t>0:
            self.shooting = 0
            self.direc += (.1+self.level/100.0)*self.flip
            self.shot_int = 100
        else:
            self.shooting = 0
            self.direc += (.1+self.level/100.0)*self.flip
    def update_move(self,player,t):
        if t > 47000:
            self.returning = True
        elif t > 43000:
            pass
        elif t > 42000:
            self.move_to((400,200),1)
        elif t > 36000:
            d = math.atan2(self.y - player.y,self.x-player.x)
            self.x -= math.cos(d)
            self.y -= math.sin(d)
            self.x += 2*math.cos(t/100.0)*self.flip
            self.y += 2*math.sin(t/100.0)*self.flip
        elif t > 33750:
            self.x += 2*math.cos(t/100.0)*self.flip
            self.y += 2*math.sin(t/100.0)*self.flip
        elif t > 33000:
            pass
        elif t > 31000:
            pass
        elif t > 27000:
            pass
        elif t > 25000:
            pass
        elif t > 23000:
            self.move_to((400+200*(self.flip*2),300),.1)
        elif t > 22000:
            pass
        elif t>20000:
            self.move_to((400+200*self.flip,300),.1)
        elif t>18000:
            self.move_to((400+300*self.flip,300),1)
        elif t>14000:
            pass
        elif t>8000:
            self.move_to((400,200),.25)
        elif t>4000:
            pass
        elif t>3000:
            pass
        elif t>0:
            self.move_to((400,300))
        else:
            self.move_to((400,300))
    def update(self,player,*args):
        t = (self.curr()-self.start)%self.loop_time
        self.image = pygame.transform.rotate(self.orig_img,self.direc)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center = (self.x,self.y))
        if self.curr()-self.abs_start>self.limit:
            self.move_to((400,300),2)
            self.shot_int = 125
            self.shooting = 0
            if self.curr()-self.abs_start>self.limit+500:
                self.shooting = 5
                self.direc += 2
        elif not self.returning:
            self.update_shoot(player,t)
            self.update_move(player,t)
        if self.returning:
            self.shot_int = 500
            self.move_to((400,300))
            if self.rect.center == (400,300):
                self.returning = False
                self.start = self.curr()
                self.flip *= -1
            self.direc += .1
        if self.shooting and self.curr()-self.last_shot > self.shot_int:
            self.shot_ready = True
        if not self.shooting:
            if self.curr()-self.last_spawn>6000 and self.curr()-self.abs_start>6000:
                self.spawn_enem = True
            else:
                self.spawn_enem = False
    def shoot(self,*args):
        self.last_shot = self.curr()
        self.shot_ready = False
        G = None
        if self.shooting:
            if self.shooting == 1:
                G = self.shoot_patt1()
            elif self.shooting == 2:
                G = self.shoot_patt2(self.d_dir)
            elif self.shooting == 3:
                G = self.shoot_patt3()
                self.bullets.add(G)
            elif self.shooting == 4:
                G = self.shoot_patt4()
            elif self.shooting == 5:
               G = self.shoot_patt5()
            return G
        return pygame.sprite.Group()
    def shoot_patt1(self,num = 10,offset = 0,reverse = 1):
        #self.last_shot = self.curr()
        bullets = [Env.EnemyBullet(loc = self.rect.center,direc = (self.direc+i*(360/num)+offset)*reverse,vel = 3) for i in xrange(num)]
        return pygame.sprite.Group(bullets)
    def shoot_patt2(self,d_thet = 0):
        #self.last_shot = self.curr()
        bullets = [Env.EnemyBullet(loc = self.rect.center,path = EnemyPath.paths['Z'],direc = self.direc+i*360/6,vel = 4,flip = self.flip,d_dir = self.d_dir) for i in xrange(6)]
        return pygame.sprite.Group(bullets)
    def shoot_patt3(self,num = 5):
        #self.last_shot = self.curr()
        self.shot_cnt += 1
        self.shot_cnt %= num
        bullets = [BossBullet(pos = self.rect.center,path = EnemyPath.paths['V'],flip = -1+i*2, change = 15 - self.shot_cnt) for i in xrange(2)]
        return pygame.sprite.Group(bullets)
    def shoot_patt4(self):
        #self.last_shot = self.curr()
        bullets = [Env.EnemyBullet(loc = self.rect.center,path = EnemyPath.paths['O'],direc = self.direc + i*360/4) for i in xrange(4)]
##        bullets2 = [Env.EnemyBullet(loc = self.rect.center,path = EnemyPath.paths['O'],direc = self.direc + i*360/2,flip = -1) for i in xrange(2)]

        return pygame.sprite.Group(bullets)
    def shoot_patt5(self):
        #self.last_shot = self.curr()
        bullets1 = self.shoot_patt1(num = 5)
        bullets2 = self.shoot_patt2(self.d_dir)
        #bullets3 = self.shoot_patt3()
        #bullets2 = self.shoot_patt1(num = 5,reverse = -1)
##        bullets3 = self.shoot_patt1(num = 3,offset = 240)
        return pygame.sprite.Group(bullets1,bullets2)#bullets3)
class BossBullet(pygame.sprite.Sprite):
    def __init__(self,pos,path,flip=1,change=40,offset = 0):
        pygame.sprite.Sprite.__init__(self)
        self.x,self.y = pos
        self.path = path#EnemyPath.paths[14]
        self.curr = pygame.time.get_ticks
        self.start = self.curr()
        self.orig_img = pygame.image.load('images/enemies/BossBullet.png').convert()
        self.orig_img.set_colorkey(BLACK)
        self.image = self.orig_img
        self.rect = self.image.get_rect(center = pos)
        self.flip = flip
        self.direc = 0
        self.change = change
        self.offset = offset
        self.trig = 0
    def update(self,player,*args):
        vel = self.path((self.curr()-self.start)/80,self.flip,self,player,self.change,self.trig)
        if (self.curr()-self.start)/80<self.change:
            d = math.atan2(self.y-player.y,player.x-self.x)
##            f = pygame.font.Font(None,20)
##            DISPLAYSURF.blit(f.render(str(d),False,WHITE),(0,0))
            self.image = pygame.transform.rotate(self.orig_img,math.degrees(d))
            self.rect = self.image.get_rect(center = (self.x,self.y))
            
        if (self.curr()-self.start)/80>=self.change and self.direc == 0:
            self.direc = math.atan2(player.y-self.y,player.x-self.x)
        self.x += vel[0]
        self.y += vel[1]
        self.rect.center = (self.x,self.y)
        if self.x < -200 or self.x > 1000 or self.y > 800 or self.y < -200:
            self.kill()
def get_enemy(E):
    for i in Enemies.types:
        if type(E) == Enemies.types[i]:
            return i        
class Enemies:
    types = {1:AirEnemy,
             2:GroundEnemy,
             3:Turret,
             4:Chaser,
             5:Tank,
             6:Fighter,
             'B':Boss}

class EnemyPath:
    def path0(t,*args):
        return(0,0)
    def path1(t,*args):
        dx_t = 0
        dy_t = 3
        return dx_t,dy_t
    def path2(t,*args):
        dx_t = 3
        dy_t = 0
        return dx_t,dy_t
    def path3(t,*args):
        dx_t = -3
        dy_t = 0
        return dx_t,dy_t
    def path4(t,*args):
        dx_t = 3
        dy_t = 3
        return dx_t,dy_t
    def path5(t,*args):
        dx_t = -3
        dy_t = 3
        return dx_t,dy_t
    def path6(t,*args):
        dx_t= 5*math.sin(t/20.0)
        dy_t= 2
        return dx_t,dy_t
    def path7(t,*args):
        dx_t= 5*math.sin(-t/20.0)
        dy_t= 2
        return dx_t,dy_t        
    def path8(t,*args):
        dx_t=5*math.sin(t/10.0)+1
        dy_t=5*math.cos(t/10.0)+1
        return dx_t,dy_t
    def path9(t,*args):
        dx_t = 5*math.sin(-t/10.0)-1
        dy_t = 5*math.cos(t/10.0)+1
        return dx_t,dy_t
    def path10(t,*args):
        dx_t = 4-t/40.0
        dy_t = 3-t/40.0
        return dx_t,dy_t
    def path11(t,*args):
        dx_t = t/40.0-4
        dy_t = 3-t/40.0
        return dx_t,dy_t
    def path12(t,*args):
        dx_t = 1
        dy_t = 3-t/40.0
        return dx_t,dy_t
    def path13(t,*args):
        dx_t = -1
        dy_t = 3-t/40.0
        return dx_t,dy_t
    def pathV(t,flip,shoot,player,change,trig = 0,*args):
        dx_t = 0
        dy_t = 0
        if t < change/2:
            dx_t = (t+20)/40.0*flip
            dy_t = (t-20)/20.0#-40/(t+1)
        elif t <= change:
            dx_t = flip
            dy_t = (t-20)/20.0
        else:
            direc = shoot.direc#math.atan2(shooter.y-player.y,player.x-shooter.x)
            dx_t = math.cos(direc)*10
            dy_t = math.sin(direc)*10
        return dx_t,dy_t
    def pathO(t,direc,flip = 1,*args):
        direc = math.radians(direc)*flip
        dx_t = math.cos(math.log(t+1)+direc)*2#(math.sin(t+direc)+t*math.cos(t+direc))/(t+1)
        dy_t = math.sin(math.log(t+1)+direc)*2#(math.cos(t+direc)-t*math.sin(t+direc))/(t+1)
        return dx_t,dy_t
    def pathL(t,direc,vel,*args):
        dx_t = math.cos(math.radians(direc))*vel
        dy_t = math.sin(math.radians(direc))*vel
        return dx_t,dy_t
    def pathA(t,direc,vel,trig = 0,*args):
        direc = math.radians(direc)*flip
        dx_t = math.cos(math.log(t+1)**2+direc)*2#(math.sin(t+direc)+t*math.cos(t+direc))/(t+1)
        dy_t = math.sin(math.log(t+1)**2+direc)*2#(math.cos(t+direc)-t*math.sin(t+direc))/(t+1)
        if trig == 1:
            dx_t = 0
            dy_t = 0
        elif trig == 2:
           return pathL(t,direc,vel)
        return dx_t,dy_t
    def pathZ(t,direc,vel,flip = 1,d_theta = 0,*args):
        dx_t = 0
        dy_t = 0
        d = direc
        mod = 70*math.copysign(1,-d_theta)
        if int(t/5)%2:
            direc += mod#*math.copysign(1,d_theta)
        else:
            direc -= mod#*math.copysign(1,d_theta)
        dx_t = math.cos(math.radians(direc))*vel
        dy_t = math.sin(math.radians(direc))*vel
        return dx_t,dy_t
##    def path11(t,player,**kwargs):
        
    paths = {0:path0,
             1:path1,
             2:path2,
             3:path3,
             4:path4,
             5:path5,
             6:path6,
             7:path7,
             8:path8,
             9:path9,
             10:path10,
             11:path11,
             12:path12,
             13:path13,
             'V':pathV,
             'O':pathO,
             'L':pathL,
             'Z':pathZ}
def get_path(P):
    for k in EnemyPath.paths:
        if P == EnemyPath.paths[k]:
            return k
class EnemyPattern:
    def pattern0(enemy,path,offset = (0,0)):
        enemy = Enemies.types[enemy]
        path = EnemyPath.paths[path]
        return pygame.sprite.GroupSingle(enemy(path,offset))
    def pattern1(enemy,path,offset = (0,0)):
        enemy = Enemies.types[enemy]
        path = EnemyPath.paths[path]
        group = pygame.sprite.Group([enemy(path,pos = (0,0)) for i in xrange(3)])
        n = 0
        for sprite in group:
            sprite.rect.move_ip(32*math.cos(n*math.pi/2),32*math.sin(n*math.pi/2))
            sprite.x,sprite.y = sprite.rect.center
            n += 1
        if offset != (0,0):
            for sprite in group:
                sprite.rect.move_ip(offset[0],offset[1])
                sprite.x,sprite.y = sprite.rect.center
        return group
    def pattern2(enemy,path,offset = (0,0)):
        enemy = Enemies.types[enemy]
        path = EnemyPath.paths[path]
        group = pygame.sprite.Group([enemy(path,pos = (0,0)) for i in xrange(12)])
        i = 0
        for sprite in group:
            sprite.rect.move_ip(32*(i/3),32*(i%3))
            sprite.x,sprite.y = sprite.rect.center
            i += 1
        if offset != (0,0):
            for sprite in group:
                sprite.rect.move_ip(offset[0],offset[1])
                sprite.x,sprite.y = sprite.rect.center
        return group
    patterns = {0:pattern0,
                1:pattern1,
                2:pattern2}
if __name__== '__main__':
##    import main
##    main.main()
    pygame.init()
    global DISPLAYSURF
    DISPLAYSURF = pygame.display.set_mode((800,600))
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    fpsClock = pygame.time.Clock()
    lastcnt = 0
    temp = pygame.Surface((10,10))
    temp.fill(RED)
    done = False
    boss = None
    player = Player.Ship()
    while not done:
        DISPLAYSURF.fill(BLACK)
        for event in pygame.event.get():
            if event.type == QUIT:
                done = True
            elif event.type == KEYDOWN:
                if event.key in (K_1,K_2,K_3,K_4,K_5,K_6,K_7,K_8,K_9,K_0):
                    if event.key == K_1:
                        enemies.add(AirEnemy(EnemyPath.paths[1]))
                    elif event.key == K_2:
                        enemies.add(AirEnemy(EnemyPath.paths[2]))
                    elif event.key == K_3:
                        enemies.add(AirEnemy(EnemyPath.paths[3]))
                    elif event.key == K_4:
                        enemies.add(AirEnemy(EnemyPath.paths[4]))
                    elif event.key == K_5:
                        enemies.add(AirEnemy(EnemyPath.paths[5]))
                    elif event.key == K_6:
                        enemies.add(AirEnemy(EnemyPath.paths[6]))
                    elif event.key == K_7:
                        enemies.add(AirEnemy(EnemyPath.paths[7]))
                    elif event.key == K_8:
                        enemies.add(AirEnemy(EnemyPath.paths[8]))
                    elif event.key == K_9:
                        enemies.add(AirEnemy(EnemyPath.paths[10],pos = (-10,10)))
                    elif event.key == K_0:
                        enemies.add(AirEnemy(EnemyPath.paths[11],pos = (810,10)))
                    lastcnt += 1
                    print enemies
                elif event.key == K_b:
                    enemies.add(Boss(1,(400,00)))
        player.update()
        if enemies:
            f = pygame.font.Font(None,30)
            for enemy in enemies:
                enemy.update(player.cursor)
                DISPLAYSURF.blit(f.render(repr(enemy.shot_ready),False,WHITE),(0,0))
                if enemy.shot_ready:
                    bullets.add(enemy.shoot())
            enemies.draw(DISPLAYSURF)
        DISPLAYSURF.blit(player.image,player.rect)
        if bullets:
            bullets.update(player.cursor)
            bullets.draw(DISPLAYSURF)
        if lastcnt != len(enemies):
            lastcnt = len(enemies)
            print enemies
        fpsClock.tick(120)
        pygame.display.update()
    pygame.quit()
    SystemExit

