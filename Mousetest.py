import pygame, sys, math
from pygame.locals import *


FPS = 0

WIDTH = 800
HEIGHT = 600
RED = (255,0,0)
WHITE = (255,255,255)
BLACK = (0,0,0)
class Cursor(object):
    def __init__(self):
        self.image = pygame.Surface((16,16))
        self.image.fill((255,0,0))
        self.rect = self.image.get_rect(center = (400,400))
        self.x = 400
        self.y = 400
        self.velocity = 0
        self.direction = math.radians(0)

    def update(self):
        e = math.e
        self.direction = getDirec(self.x, self.y)
        self.dist = getDist(self.x, self.y)
        self.velocity = 10*(1-math.pow(e,-self.dist/100))#math.log(getDist(self.xcoord, self.ycoord)+1)/10
        self.x += self.velocity*math.cos(self.direction)
        self.y -= self.velocity*math.sin(self.direction)

        self.rect.center = (self.x, self.y)
        self.rect = self.rect.clamp(pygame.Rect(0,0,WIDTH,HEIGHT))
    def get_pos(self):
        self.update()
        return self.x,self.y
    pos = property(get_pos)
##    def move(self,pos):
##        direc = math.atan2(self.ycoord-pos[1],pos[0]-self.xcoord)
##        vel = 10
##        self.xcoord += math.cos(direc)*vel
##        self.ycoord -= math.sin(direc)*vel
##        self.rect.center = (self.xcoord,self.ycoord)
def getDist(headx, heady):
    return math.hypot(pygame.mouse.get_pos()[0] - headx*1.0, pygame.mouse.get_pos()[1] - heady*1.0)

def getDirec(headx, heady):
    dy = (heady - pygame.mouse.get_pos()[1])*1.0
    dx = (pygame.mouse.get_pos()[0] - headx)*1.0
    return math.atan2(dy,dx)
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.cursor = Cursor()
        self.image = pygame.Surface((64,64)).convert()
        pygame.draw.lines(self.image,RED,True,[(0,63),(32,0),(64,63)])
        self.rect = self.image.get_rect()
        self.image.set_colorkey(BLACK)
    def update(self):
        self.rect.center = self.cursor.pos
if __name__ == '__main__':
    pygame.init()
    fpsClock = pygame.time.Clock()
    cur1 = Cursor()
    pygame.mouse.set_pos(400,400)
    DISPLAYSURF = pygame.display.set_mode((WIDTH, WIDTH))
    player = Player()
    
    while True:
        DISPLAYSURF.fill((255,255,255))
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        player.update()
        DISPLAYSURF.blit(player.image, player.rect)
        pygame.display.update()
        fpsClock.tick(FPS)
