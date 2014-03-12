import pygame
from pygame.locals import *
from constants import *
class Interface(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.orig_image = pygame.image.load('images/interface/UI.png').convert()
        self.healthbar = pygame.image.load('images/interface/HealthBar.png').convert()
        self.shieldbar = pygame.image.load('images/interface/ShieldBar.png').convert()
        self.image = self.orig_image
        pygame.font.init()

        self.score_font = pygame.font.SysFont('consolas',30)
        self.accuracy_font = pygame.font.SysFont('consolas',20)
    def update(self,player,*args):
        self.score = player.score
        self.shield = player.shield
        self.health = player.health
        self.image = self.orig_image.convert()
        self.image.blit(self.score_font.render("%s"%self.score,False,GREEN),(20,100))
        if player.health > 0:
            curr_health = pygame.transform.scale(self.healthbar,(int(150*player.health/10.0),30))
            self.image.blit(curr_health,(20,275))

        if player.shield > 0:
            curr_shield = pygame.transform.scale(self.shieldbar,(int(150*player.shield/10.0),30))
            self.image.blit(curr_shield,(20,375))
        pygame.draw.line(self.image,BLACK,(20+75,375),(20+75,405),3)
##        self.image.blit(self.accuracy_font.render("Gun Acc : %s%s"%(round(player.shoot_accuracy*100,2),"%"),False,GREEN),(20,140))
##        self.image.blit(self.accuracy_font.render("Bomb Acc: %s%s"%(round(player.bomb_accuracy*100,2),"%"),False,GREEN),(20,200))

class HUD(pygame.sprite.Sprite):
    def __init__(self,pos = (0,0)):
        pygame.sprite.Sprite.__init__(self)
        f = pygame.font.SysFont('consolas',10)
        self.overcharge = f.render('{0:^20}'.format('Overcharge'),False,WHITE,BLUE)
        self.health = f.render('{0:^20}'.format('Health'),False,WHITE,RED)
        self.size = self.overcharge.get_size()
        self.image = pygame.Surface((self.size[0],self.size[1]*2))
        self.rect = self.image.get_rect(center = pos)

    def update(self,boss,*args):
        self.rect.center = boss.rect.center
        percent = (boss.health/float(boss.max_health))
        self.image.fill(BLACK)
        over_len = min(int(self.size[0]*boss.charge),self.size[0])
        heal_len = max(int(self.size[0]*percent),0)
        self.image.blit(self.overcharge.subsurface(0,0,over_len,self.size[1]),(0,0))
        self.image.blit(self.health.subsurface(0,0,heal_len,self.size[1]),(0,self.size[1]))
