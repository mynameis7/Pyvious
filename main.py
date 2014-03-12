import pygame,sys,random,os
from pygame.locals import *
from constants import *
import player as Player
import environment as Env
import enemies as Enemy
import interface
import Screens
def compile_timeline(filepath):
    timeline = []
    with open(filepath) as f:
        for line in f:
            timeline.append(line.strip())
    return timeline
class Level(object):
    def __init__(self,num=1,score=0):
        self.timeline = Env.EventQueue()
        ##[time:enemy:pattern:path:location on screen]
        #f = compile_timeline('levels\\testlvel.txt')
        #self.timeline.load(f)
        self.BGimage = pygame.image.load('images/BG.png').convert()
        self.width,self.length = self.BGimage.get_size()
        self.offset = 0
        self.image = pygame.Surface((800,600))
        self.num = num
        self.score = score
        self.scrolling = True
    def init(self):
        global DISPLAYSURF
        DISPLAYSURF = pygame.display.set_mode((WIDTH,HEIGHT))
    def load(self,filename):
        self.timeline = Env.EventQueue()
        f = compile_timeline(filename)
        self.timeline.load(f)
    def loadList(self,timeline):
        self.timeline = Env.EventQueue()
        self.timeline.load(timeline)
    def update(self):
        if self.scrolling:
            self.offset += .5
            self.offset %= self.length
            if self.length-self.offset<600:
                temp = pygame.Surface((800,600))
                height1 = ((self.length-self.offset))
                y2 = self.length-(self.offset-self.length)-600
                height2 = 600-height1

                remd = self.BGimage.subsurface(0,0,800,height1)
                wrap = self.BGimage.subsurface(0,y2,800,height2)
                temp.blit(remd,(0,600-height1))
                temp.blit(wrap,(0,0))
                self.image = temp
            else:
                self.image = self.BGimage.subsurface(0,self.length-self.offset-600,800,600)
    def run(self,gun = 0):
        fpsClock = pygame.time.Clock()
        pygame.mouse.set_pos(400,400)
        player = Player.Ship()
        player.gun_level = gun
        air_enemies = pygame.sprite.Group()
        air_explosions = pygame.sprite.Group()
        ground_enemies = pygame.sprite.Group()
        ground_explosions = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        enemy_bullets = pygame.sprite.Group()
        curr = pygame.time.get_ticks
        start = curr()
        dead_air = pygame.sprite.Group()
        dead_ground = pygame.sprite.Group()
        
        timg = pygame.Surface((800,600))
        UI = interface.Interface()
        HUD = interface.HUD()
        VALID_EVENTS = [QUIT,KEYDOWN,KEYUP,MOUSEMOTION,ADD_ENEMY,JOYAXISMOTION,JOYBUTTONDOWN,JOYBUTTONUP]
        offset = 0

        collide_enemies = pygame.sprite.Group()
        collide_bullets = pygame.sprite.Group()
        BOSS = pygame.sprite.GroupSingle()
        win = False
        if self.score:
            player.score = self.score
        player.rect.center = (400,500)
        pygame.mixer.music.load('music/LevelTheme.ogg')
        pygame.mixer.music.set_volume(.5)
        pygame.mixer.set_reserved(2)
        pygame.mixer.music.play(-1)

        while True:
            self.update()
            timg.blit(self.image,(0,0))
            for event in pygame.event.get():#VALID_EVENTS):
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYDOWN:
##                    if not player.control in ('wasd','arrow'):
                    if event.key == K_ESCAPE:
                        stopped = curr()
                        S = pygame.Surface((WIDTH,HEIGHT))
                        S.blit(timg,(0,0))
                        S.blit(UI.image,(800,0))
                        Screens.Pause(S)
                        start = start + (curr()-stopped)
                    if event.key in (K_w,K_s,K_a,K_d) and not player.control == 'wasd':
                        player.control = 'wasd'
                        pygame.mouse.set_visible(False)
                        player.cursor.active = False
                    elif event.key in (K_LEFT,K_RIGHT,K_UP,K_DOWN) and not player.control == 'arrow':
                        pygame.mouse.set_visible(False)
                        player.control = 'arrow'
                        player.cursor.active = False
                elif event.type in (MOUSEMOTION,MOUSEBUTTONDOWN) and not player.control == 'mouse':
                    pygame.mouse.set_pos(player.rect.center)
                    pygame.mouse.set_visible(True)
                    player.control = 'mouse'
                    player.cursor.active = True
                elif event.type in (JOYAXISMOTION,JOYBUTTONDOWN,JOYBUTTONUP):
                    player.x,player.y = player.rect.center
                    if event.type == JOYAXISMOTION and abs(event.value) > .03 and event.axis in (0,1):
                        player.control = 'joy'
                        player.cursor.active = False
                        pygame.mouse.set_visible(False)
                elif event.type == ADD_ENEMY:
                    if event.enemy == 'B':
                        BOSS.sprite = Enemy.Boss(level = self.num)
                        pygame.mixer.music.load('music/BossTheme1.ogg')
                        pygame.mixer.music.set_endevent(USEREVENT+3)
                        pygame.mixer.music.play()
                    else:
                        E = Enemy.EnemyPattern.patterns[event.pattern](event.enemy,event.path,event.offset)
                        for enemy in E:
                            player.total_enemy_health += enemy.health
                            player.enemy_count += 1
                            enemy.health += self.num/5
                        if Enemy.Enemies.types[event.enemy].type_ == 'air':
                            air_enemies.add(E)
                        else:
                            ground_enemies.add(E)
                elif event.type == USEREVENT+3:
                    pygame.mixer.music.load('music/BossTheme2.ogg')
                    pygame.mixer.music.play(-1)
                    pygame.mixer.music.set_endevent()
            pygame.event.pump()
            
            while self.timeline.next_ and curr()-start > self.timeline.next_.time:
                pygame.event.post(self.timeline.pop().event)
                
            if ground_enemies:
                for enemy in ground_enemies:
                    enemy.y += .5
                    enemy.update(player.cursor)
                    if enemy.shot_ready:
                        enemy_bullets.add(enemy.shoot(player.cursor))
                ground_enemies.draw(timg)
##                dead_enemies = pygame.sprite.groupcollide(ground_enemies,player.bomb,True,False,pygame.sprite.collide_mask)
##                if dead_enemies:
##                    player.bombs_missed -= 1
##                    player.bomb.empty()
##                    dead_ground.add(dead_enemies)
            if ground_explosions:
                ground_explosions.update()
                ground_explosions.draw(timg)
                dead_ground.add(pygame.sprite.groupcollide(ground_enemies,ground_explosions,True,False,pygame.sprite.collide_mask))
##                pygame.sprite.groupcollide(enemy_bullets,ground_explosions,True,False,pygame.sprite.collide_mask)
            player.update()
            val = bool(pygame.sprite.spritecollideany(player.retic,ground_enemies))
            player.retic.set_image(val)
            if player.bullets:
                player.bullets.update()
                player.bullets.draw(timg)
            if player.target.sprite:
                player.target.update()
                player.target.draw(timg)
                if not player.bomb.sprite:
                    player.target.empty()
            if player.bomb.sprite:
                player.bomb.update(player.target.sprite.rect)
                player.bomb.draw(timg)
                if not player.bomb.sprite.active:
                    ground_explosions.add(Env.Explosion(player.bomb.sprite.rect.center,player.explos_rad))
                    player.bomb.empty()
                    
            if air_enemies:
                for enemy in air_enemies:
                    enemy.update(player.cursor)
                    if enemy.shot_ready:
                        enemy_bullets.add(enemy.shoot(player.cursor))
                air_enemies.draw(timg)
                dead_enemies = pygame.sprite.groupcollide(air_enemies,player.bullets,False,True,pygame.sprite.collide_mask)
                player.shots_missed -= len(dead_enemies)
                dead_air.add(dead_enemies)
                collide_enemies = pygame.sprite.spritecollide(player,air_enemies,False,pygame.sprite.collide_mask)
            if BOSS.sprite:
                if BOSS.sprite.curr()-BOSS.sprite.abs_start<3500:
                    if player.rect.top < BOSS.sprite.rect.bottom+1:
                        player.rect.top = BOSS.sprite.rect.bottom+1
                    
                    pygame.draw.circle(timg,(0,0,255,128),BOSS.sprite.rect.center,70,10)
                hits = pygame.sprite.groupcollide(BOSS,player.bullets,False,True,pygame.sprite.collide_mask)
                BOSS.update(player.cursor)
                BOSS.draw(timg)
                #f = pygame.font.Font(None,20)
                #timg.blit(f.render('%s'%(round(BOSS.sprite.health/float(BOSS.sprite.max_health)*100,2)),False,WHITE),(0,0))
                HUD.update(BOSS.sprite)
                timg.blit(HUD.image,HUD.rect)
                if BOSS.sprite.shot_ready:
                    enemy_bullets.add(BOSS.sprite.shoot(player.cursor))
                if BOSS.sprite.spawn_enem:
                    loc = BOSS.sprite.rect.center
                    r1 = [3,1,5]
                    r2 = [2,1,3]
                    r3 = [10,1,11]
                    p = [r1,r2,r3]
                    bin_loc = loc[0]/(800/3),loc[1]/(600/3)
                    p = p[bin_loc[1]][bin_loc[0]]
                    boss_spawn = pygame.event.Event(ADD_ENEMY,{'time':0,'enemy':6,'pattern':1,'path':p,'offset':loc})
                    pygame.event.post(boss_spawn)
                    BOSS.sprite.last_spawn = BOSS.sprite.curr()
                if hits:
                    for coll in hits:
                        if BOSS.sprite.curr()-BOSS.sprite.abs_start>3500:
                            BOSS.sprite.health -= len(hits[coll])
                        player.shots_missed -= len(hits[coll])
                if BOSS.sprite.health <= 0:
                    pygame.mixer.music.stop()
                    expl = Env.Explosion(BOSS.sprite.rect.center,200)
                    air_explosions.add(expl)
                    ground_explosions.add(expl)
                    BOSS.sprite.kill()
                    player.score += 500*self.num
                    BOSS.empty()
                    enemy_bullets.empty()
                    air_enemies.empty()
                    ground_enemies.empty()
                    while player.rect.center != (400,500):
                        ground_explosions.update()
                        air_explosions.update()
                        pygame.event.pump()
                        player.moveto((400,500))
                        timg.blit(self.image,(0,0))
                        ground_explosions.draw(timg)
                        timg.blit(player.image,player.rect)
                        air_explosions.draw(timg)
                        UI.update(player)
                        DISPLAYSURF.blit(timg,(0,0))
                        DISPLAYSURF.blit(UI.image,(800,0))
                        pygame.display.update()
                    end = pygame.time.get_ticks()
                    while pygame.time.get_ticks() - end < 50:
                        pygame.event.pump()
                        ground_explosions.update()
                        air_explosions.update()
                        timg.blit(self.image,(0,0))
                        ground_explosions.draw(timg)
                        timg.blit(player.image,player.rect)
                        air_explosions.draw(timg)
                        UI.update(player)
                        DISPLAYSURF.blit(timg,(0,0))
                        DISPLAYSURF.blit(UI.image,(800,0))
                        pygame.display.update()
                    air_explosions.empty()
                    S = pygame.Surface((WIDTH,HEIGHT))
                    S.blit(timg,(0,0))
                    S.blit(UI.image,(800,0))
                    player.score = Screens.Success(S,player)
                    pygame.mixer.music.stop()
                    return True,player
                if pygame.sprite.spritecollide(player,BOSS,True,pygame.sprite.collide_mask):
                    player.health = 0

            if enemy_bullets:
                enemy_bullets.update(player.cursor)
                collide_bullets = pygame.sprite.spritecollideany(player,enemy_bullets,pygame.sprite.collide_mask)
                if collide_bullets and not player.invincible:
                    collide_bullets.kill()
                    if player.shield >= 5:
                        player.shield -= 5
                        player.was_hit = player.curr()
                    elif player.shield < 5:
                        player.shield = 0
                        player.health -= 1
                        player.was_hit = player.curr()
                    else:
                        player.health -= 2
                        player.was_hit = player.curr()
                    
                enemy_bullets.draw(timg)
            if air_explosions:
                air_explosions.update()
                air_explosions.draw(timg)
                dead_air.add(pygame.sprite.groupcollide(air_enemies,air_explosions,False,False,pygame.sprite.collide_mask))
                pygame.sprite.groupcollide(enemy_bullets,air_explosions,True,False,pygame.sprite.collide_mask)
            if powerups:
                powerups.update()
                collide = pygame.sprite.spritecollideany(player,powerups)
                if collide:
                    if collide.type_ == 'gun':
                        if player.gun_level < 3:
                            player.gun_level += 1
                        elif player.burst_cnt < 6:
                            player.burst_cnt += 1
                        elif player.burst_cnt >=6:
                            if player.gun_level != 4:
                                player.gun_level = 4
                            else:
                                player.burt_cnt += 1
                    elif collide.type_ == 'rate':
                        player.firerate += 1
                    elif collide.type_ == 'radius':
                        player.explos_rad += 10
                    elif collide.type_ == 'health':
                        player.health = 10
                    collide.kill()
                powerups.draw(timg)
            if collide_enemies and not player.invincible:
                for enemy in collide_enemies:
                    player.health -= 1
                    if player.shield < 5:
                        player.health -= 1
                    player.shield = 0
                    player.score += enemy.val
                    player.was_hit = player.curr()
                    air_explosions.add(Env.Explosion(enemy.rect.center,10))
                    enemy.health = 0
                    enemy.kill()
            if dead_air:
                for enemy in dead_air:
                    enemy.health -= 1
                    if enemy.health <= 0:
                        player.score += enemy.val
                        player.a_enemies_killed += 1
                        air_explosions.add(Env.Explosion(enemy.rect.center,enemy.expl_rad))
                        if not random.randrange(0,50):
                            powerups.add(Env.GunUP(enemy.rect.center))
                        elif not random.randrange(0,100) and player.health <= 5:
                            powerups.add(Env.HealthUP(enemy.rect.center))
                        enemy.kill()
            if dead_ground:
                if player.bombs_missed>0:
                    player.bombs_missed -= 1
                for enemy in dead_ground:
                    enemy.health -= 1
                    if enemy.health <= 0:
                        player.score += enemy.val
                        player.g_enemies_killed += 1
                        ground_explosions.add(Env.Explosion(enemy.rect.center,enemy.expl_rad))
                        if not random.randrange(0,20):
                            powerups.add(Env.RadiusUP(enemy.rect.center))
                        elif not random.randrange(0,100) and player.health <= 5:
                            powerups.add(Env.HealthUP(enemy.rect.center))  
                        enemy.kill()
                        
            if player.health <= 0:
                pygame.mixer.music.stop()
                S = pygame.Surface((WIDTH,HEIGHT))
                UI.update(player)
                S.blit(timg,(0,0))
                S.blit(UI.image,(800,0))
                player.score = Screens.GameOver(S,player)
                pygame.mixer.music.stop()
                return False,player
            timg.blit(player.image,player.rect)
            timg.blit(player.retic.image,player.retic.rect)
            UI.update(player)
            DISPLAYSURF.blit(UI.image,(800,0))
            DISPLAYSURF.blit(timg,(0,0))
            fpsClock.tick(FPS)
            pygame.display.update()
def main():
    from level_maker import gen_random_level as newLevel
    def check_highscore(score,highscores):
        highscores = sorted(highscores.keys())
        for high in highscores:
            if score > high:
                return min(highscores)
        
        return False
    pygame.mixer.pre_init(channels = 4,buffer = 1024)
    pygame.init()
    global DISPLAYSURF
    DISPLAYSURF = pygame.display.set_mode((WIDTH,HEIGHT))
    num = 0
    levels = []
    for f in os.listdir('levels'):
        if 'level' in f:
            levels.append('levels/%s'%f)
    print levels
    level_played = False
    score = 0
    gun = 0
    highscores = {}
    with open('scores.txt') as f:
        for line in f:
            line = line.split(',')
            highscores[eval(line[1])]=line[0]
    print highscores
    first = True
    while True:
        if not level_played:
            Screens.StartScreen(highscores)
        if first:
            nxt = Screens.Tutorial()
            if nxt:
                first = False
        if not first:
            pygame.display.update()
            level = Level(num+1,score)
            level.loadList(newLevel(40,4,num))
            complete,player = level.run(gun)
            score = player.score
            gun = player.gun_level
            if complete:
                level_played = True
                num += 1
            else:
                num = 0
                level_played = False
                record = check_highscore(score,highscores)
                if record:
                    highscores = Screens.HighscoreScreen(score,record,highscores)
                score = 0
    pygame.quit()
    sys.exit()
if __name__ == '__main__':
    main()
    
