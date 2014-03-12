import pygame,sys,random,math
from pygame.locals import *
from constants import *
import player as Player
import environment as Env
import enemies as Enemy
import interface

def StartScreen(highscores):
    pygame.init()
    f = pygame.font.SysFont('consolas',30)
    highscores = sorted(highscores.items(),key = lambda s:s[0],reverse = True)
    scores = ['{name:<15}{score:>12}'.format(name = n,score = s)for s,n in highscores]#,False,WHITE) for s in highscores]
    DISPLAYSURF = pygame.display.set_mode((WIDTH,HEIGHT))
    logo = pygame.image.load('images/screen/Pyvious_logo.png').convert()
    logo.set_colorkey(BLACK)
    logo_rect = logo.get_rect(center = (WIDTH/2,HEIGHT/4))
    cont = pygame.image.load('images/screen/press_a_key.png').convert()
    cont.set_colorkey(BLACK)
    cont_rect = cont.get_rect(center = (WIDTH/2,HEIGHT-HEIGHT/4))
    star_sheet = pygame.image.load('images/screen/star.png').convert()
    star_sheet.set_colorkey(BLACK)
    star_rect = pygame.Rect(0,0,32,32)
    high = pygame.image.load('images/screen/Highscores.png').convert()
    high_rect = high.get_rect(center = (WIDTH/2,HEIGHT/3+75))
    high.set_colorkey(BLACK)
    HL = pygame.mask.from_surface(logo).outline()
    outline = []
    a,b = logo_rect.topleft
    for x,y in HL:
        pos = (x+a,y+b)
        outline.append(pos)
    i = 0
    j = 0
    joystick = None
    pygame.joystick.init()
    try:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
    except:
        pass
    while True:
        i %= len(outline)
        DISPLAYSURF.fill(BLACK)
        
        star_img = pygame.transform.rotate(star_sheet.subsurface(0,32*(j/10)%8,32,32),-j*1.5)
        star_rect = star_img.get_rect(center = outline[i])
        n = 0
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type in (KEYDOWN,JOYBUTTONDOWN,MOUSEBUTTONDOWN):
                img = pygame.Surface((WIDTH,HEIGHT))
                img.blit(logo,logo_rect)
                img.blit(cont,cont_rect)
                img.blit(star_img,star_rect)
                return img
        pygame.event.pump()
        cont.set_alpha(255*(not (j/90)%2))
        DISPLAYSURF.blit(logo,logo_rect)
        DISPLAYSURF.blit(cont,cont_rect)
        DISPLAYSURF.blit(high,high_rect)
        DISPLAYSURF.blit(star_img,star_rect)
        for score in scores:
            score_obj = f.render(score,False,WHITE)
            score_rect = score_obj.get_rect(center = (WIDTH/2,HEIGHT/2+n*score_obj.get_height()))
            DISPLAYSURF.blit(score_obj,score_rect)
            n += 1        
        pygame.display.update()
        i += 1
        j += 1
def Success(screen,player):
    screen = screen.convert_alpha()
    pygame.init()
    DISPLAYSURF = pygame.display.set_mode((WIDTH,HEIGHT))
    success = pygame.image.load('images/screen/Success.png')
    success.set_colorkey(BLACK)
    cont = pygame.image.load('images/screen/press_a_key.png')
    pygame.mixer.music.load('music/Success.ogg')
    pygame.mixer.music.play()
    cont.set_colorkey(BLACK)
    succ_rect = success.get_rect(center = (WIDTH/2,HEIGHT/4))
    cont_rect = cont.get_rect(center = (WIDTH/2,HEIGHT-HEIGHT/4))
    joystick = None
    pygame.joystick.init()
    #shot_acc = player.shot_accuracy
    try:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
    except:
        pass
    curr = pygame.time.get_ticks
    start = curr()
    E_tot = player.enemy_count
    E_kill = player.a_enemies_killed + player.g_enemies_killed
    f = pygame.font.SysFont('consolas',20)
    Y = HEIGHT/20

    header = f.render('{0:>48}'.format('BONUS'),False,WHITE)
    head_rect = header.get_rect(center = (WIDTH/2,Y*6))
    bonus_string = '{0:<30}{1:>6}/{2:<6}+{3:>6}'
    kill_bonus = int(10000*E_kill/float(E_tot))
    kill_cnt = f.render(bonus_string.format('Enemies killed/total',E_kill,E_tot,kill_bonus),False,WHITE)
    kill_rect = kill_cnt.get_rect(center = (WIDTH/2,7*Y))
    health_bonus = int(2000*(player.health/10.0))
    health = f.render(bonus_string.format('Health final/max',player.health,10,health_bonus),False,WHITE)
    health_rect = health.get_rect(center = (WIDTH/2,8*Y))
    acc_bonus = '{0:<30}{1:^13}+{2:>6}'
    gun_bonus = int(5000*round(player.shoot_accuracy,4))
    gun = f.render(acc_bonus.format('Gun Accuracy',str(round(player.shoot_accuracy*100,2))+'%',gun_bonus),False,WHITE)
    gun_rect = gun.get_rect(center = (WIDTH/2,9*Y))
    bomb_bonus = int(5000*round(player.bomb_accuracy,4))
    bomb = f.render(acc_bonus.format('Bomb Accuracy',str(round(player.bomb_accuracy*100,2))+'%',bomb_bonus),False,WHITE)
    bomb_rect = bomb.get_rect(center = (WIDTH/2,10*Y))
    total_bonus = kill_bonus+health_bonus+gun_bonus+bomb_bonus
    final_string = '{0:^30}{1:^20}'
    score = player.score
    inc = 1000
    transp = pygame.Surface((WIDTH,HEIGHT)).convert_alpha()
    transp.fill((0,0,0,200))
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type in(KEYDOWN,JOYBUTTONDOWN,MOUSEBUTTONDOWN) and score == player.score + total_bonus:
                pygame.mixer.music.stop()
                return score
        pygame.event.pump()
        DISPLAYSURF.blit(screen,(0,0))
        DISPLAYSURF.blit(transp,(0,0))
        DISPLAYSURF.blit(success,succ_rect)
        DISPLAYSURF.blit(header,head_rect)
        if curr()-start > 1000:
            DISPLAYSURF.blit(kill_cnt,kill_rect)
        if curr()-start > 2000:
            DISPLAYSURF.blit(health,health_rect)
        if curr()-start > 3000:
            DISPLAYSURF.blit(gun,gun_rect)
        if curr()-start > 4000:
            DISPLAYSURF.blit(bomb,bomb_rect)
        if curr()-start > 5000:
            if score != player.score + total_bonus and (curr()-start)/100%2:
                if inc + score <= player.score + total_bonus:
                    score += inc
                else:
                    inc /= 10
            score_obj = f.render(final_string.format('Final Score',score),False,WHITE)
            score_rect = score_obj.get_rect(center = (WIDTH/2,Y*11))
            DISPLAYSURF.blit(score_obj,score_rect)

        if score == player.score+total_bonus:
            if (curr()-start)/500%2:
                DISPLAYSURF.blit(cont,cont_rect)
        pygame.display.update()
def GameOver(screen,player):
    screen = screen.convert_alpha()
    pygame.init()
    DISPLAYSURF = pygame.display.set_mode((WIDTH,HEIGHT))
    gameover = pygame.image.load('images/screen/GameOver.png').convert()
    gameover.set_colorkey(BLACK)
    cont = pygame.image.load('images/screen/press_a_key.png').convert()
    cont.set_colorkey(BLACK)
    cont_rect = cont.get_rect(center = (WIDTH/2,HEIGHT-HEIGHT/4))
    GO_rect = gameover.get_rect(center = (WIDTH/2,HEIGHT/4))
    
    joystick = None
    pygame.joystick.init()
    try:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
    except:
        pass
    curr = pygame.time.get_ticks
    start = curr()
    transp = pygame.Surface((WIDTH,HEIGHT)).convert_alpha()
    transp.fill((0,0,0,200))
    f = pygame.font.SysFont('consolas',20)
    final_string = '{0:^30}{1:^20}'
    final_score = f.render(final_string.format('Final Score',player.score),False,WHITE)
    final_rect = final_score.get_rect(center = (WIDTH/2,HEIGHT*3/5.0))
    pygame.mixer.music.load('music/GameOver.ogg')
    pygame.mixer.music.play()
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type in(KEYDOWN,JOYBUTTONDOWN,MOUSEBUTTONDOWN) and (curr()-start)>2000:
                pygame.mixer.music.stop()
                return player.score
        pygame.event.pump()
        DISPLAYSURF.blit(screen,(0,0))
        DISPLAYSURF.blit(transp,(0,0))
        DISPLAYSURF.blit(gameover,GO_rect)
        if curr()-start > 1000:
            DISPLAYSURF.blit(final_score,final_rect)
        if curr()-start > 2000 and (curr()-start)/500%2:
            DISPLAYSURF.blit(cont,cont_rect)
        pygame.display.update()
def HighscoreScreen(new,remove,table):
    import textfield as TF
    pygame.init()
    DISPLAYSURF = pygame.display.set_mode((WIDTH,HEIGHT))
    newHigh = pygame.image.load('images/screen/NewHighscore.png').convert()
    newHigh_rect = newHigh.get_rect(center = (WIDTH/2,HEIGHT/5))
    font = pygame.font.SysFont('consolas',30)
    score = font.render('%s'%new,False,WHITE)
    score_rect = score.get_rect(center = (WIDTH/2,HEIGHT/3))
    nameField = TF.TextField('all')
    surf = pygame.Surface((WIDTH,HEIGHT))
    surf.blit(newHigh,newHigh_rect)
    surf.blit(score,score_rect)
    name = nameField.text_input(surf,message = 'Name:',loc = (400,250),maxlen = 20)
    table.pop(remove)
    table[new] = name
    with open('scores.txt','w') as f:
        for scr in table:
            f.write('{name},{score}\n'.format(name = table[scr],score = scr))
    return table

def Tutorial():
    import main
    pygame.init()
    root = 'images/screen/Tutorial/'
    DISPLAYSURF = pygame.display.set_mode((WIDTH,HEIGHT))
    control = pygame.image.load('%s%s.png'%(root,'Controls')).convert()
    enemies = pygame.image.load('%s%s.png'%(root,'Enemies')).convert()
    boss = pygame.image.load('%s%s.png'%(root,'Boss')).convert()
    powerups = pygame.image.load('%s%s.png'%(root,'Powerups')).convert()
    control.set_colorkey(BLACK)
    enemies.set_colorkey(BLACK)
    boss.set_colorkey(BLACK)
    player = Player.Ship()
    player.tutorial = True
    curr = pygame.time.get_ticks
    start = curr()
    page = 0
    ground_explosions = pygame.sprite.Group()
    level = main.Level()
    fpsClock = pygame.time.Clock()
    font = pygame.font.SysFont('consolas',30)
    tryit = font.render('Try it now!',False,WHITE)
    tryit_rect = tryit.get_rect(center = (WIDTH/2,525))
    infoln1 = font.render('Tutorial',False,WHITE)
    infoln2 = font.render('Press [Enter] or [JOY-HAT right] to advance a page',False,WHITE)
    infoln3 = font.render('Press [Backspace] or [JOY-HAT left] to go back a page.',False,WHITE)
    info1_rect = infoln1.get_rect(center = (WIDTH/2,HEIGHT/2-40))
    info2_rect = infoln2.get_rect(center = (WIDTH/2,HEIGHT/2))
    info3_rect = infoln3.get_rect(center = (WIDTH/2,HEIGHT/2+40))
    
    joystick = None
    pygame.joystick.init()
    try:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
    except:
        pass

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == JOYHATMOTION:
                if event.value[0]>0:
                    page += 1
                elif event.value[0]<0:
                    page -= 1
            elif event.type == KEYDOWN:
                if event.key == K_RETURN:
                    page += 1
                elif event.key == K_BACKSPACE:
                    page -= 1
                elif event.key in (K_w,K_s,K_a,K_d,K_j,K_k) and not player.control == 'wasd':
                    player.control = 'wasd'
                    pygame.mouse.set_visible(False)
                    player.cursor.active = False
                elif event.key in (K_LEFT,K_RIGHT,K_UP,K_DOWN,K_z,K_x) and not player.control == 'arrow':
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
        if page <0:
            return False
        elif page > 4:
            return True
        if page == 0:
            DISPLAYSURF.fill(BLACK)
            DISPLAYSURF.blit(infoln1,info1_rect)
            DISPLAYSURF.blit(infoln2,info2_rect)
            DISPLAYSURF.blit(infoln3,info3_rect)

        if page == 1:
            level.update()
            DISPLAYSURF.fill(BLACK)
            DISPLAYSURF.blit(level.image,(100,0))
            DISPLAYSURF.blit(control,(0,0))
            if (curr()-start)/500%2:
                DISPLAYSURF.blit(tryit,tryit_rect)
            player.update()
            player.rect = player.rect.clamp(pygame.Rect(100,0,800,600))
            DISPLAYSURF.blit(player.image,player.rect)
            if player.bullets:
                player.bullets.update()
                player.bullets.draw(DISPLAYSURF)
            if player.target.sprite:
                player.target.update()
                player.target.draw(DISPLAYSURF)
                if not player.bomb.sprite:
                    player.target.empty()
            if player.bomb.sprite:
                player.bomb.update(player.target.sprite.rect)
                player.bomb.draw(DISPLAYSURF)
                if not player.bomb.sprite.active:
                    ground_explosions.add(Env.Explosion(player.bomb.sprite.rect.center,player.explos_rad))
                    player.bomb.empty()
            if ground_explosions:
                ground_explosions.update()
                ground_explosions.draw(DISPLAYSURF)
            DISPLAYSURF.blit(player.retic.image,player.retic.rect)
        elif page == 2:
            DISPLAYSURF.fill(BLACK)
            DISPLAYSURF.blit(powerups,(0,0))
        elif page == 3:
            DISPLAYSURF.fill(BLACK)
            DISPLAYSURF.blit(enemies,(0,0))
        elif page == 4:
            DISPLAYSURF.fill(BLACK)
            DISPLAYSURF.blit(boss,(0,0))            
        fpsClock.tick(FPS)
        pygame.display.update()
def Pause(screen):
    DISPLAYSURF = pygame.display.get_surface()
    screen = screen.convert_alpha()
    font = pygame.font.SysFont('consolas',50)
    paus = font.render('PAUSE',True,WHITE)
    paus_rect = paus.get_rect(center = (WIDTH/2,HEIGHT/2))
    font = pygame.font.SysFont('consolas',30)
    info = font.render('Press [Escape] to unpause',True,WHITE)
    tut_info = font.render('Press [T] to see the tutorial again',True,WHITE)
    info_rect = info.get_rect(center = (WIDTH/2,HEIGHT/2+50))
    tut_rect = tut_info.get_rect(center = (WIDTH/2, HEIGHT/2+100))
    trans = pygame.Surface((WIDTH,HEIGHT)).convert_alpha()
    trans.fill((0,0,0,200))
    blink = 0
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return
                elif event.key == K_t:
                    Tutorial()
        pygame.event.pump()
        DISPLAYSURF.blit(screen,(0,0))
        DISPLAYSURF.blit(trans,(0,0))
        blink += 1
        if not blink/100%2:
            DISPLAYSURF.blit(paus,paus_rect)
            DISPLAYSURF.blit(info,info_rect)
            DISPLAYSURF.blit(tut_info,tut_rect)
        pygame.display.update()
if __name__ == '__main__':
    Tutorial()
    pygame.quit()
    sys.exit()
##highscores =[]
##with open('scores.txt') as f:
##    for line in f:
##        line = line.split(',')
##        highscores.append((line[0],eval(line[1])))
##StartScreen(highscores)
##HighscoreScreen(100,50,{120:'tommy',50:'andy',110:'potter'})
