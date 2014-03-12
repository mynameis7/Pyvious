import pygame,sys,random,os
from pygame.locals import *
from constants import *
import player as Player
import environment as Env
import enemies as Enemy
import textfield as Text



##REVISE:
##new class which contains enemy, and enemy data for later saving.
##pros: easier saving,loading, scaling

class Enemy_obj(pygame.sprite.Sprite):
    def __init__(self,enemy,enemy_num,path_num,t):
        pygame.sprite.Sprite.__init__(self)
        self.enemy = enemy
        self.image = self.enemy.image
        self.rect = self.enemy.rect
        self.enemynum = enemy_num
        self.pathnum = path_num
        self.time = t
        self.link = None
    def __str__(self):
        out = "%s:%s:%s:%s:(%s,%s)"%(self.time,self.enemynum,0,self.pathnum,self.enemy.rect.center)
    def sync(self):
        if self.link:
            self.link.time = self.time
            self.link.sync()
def make_path_img(path):
    global time_scale
    surf = pygame.Surface((1000,1000)).convert()
    x,y = (400,400)
    points = []
    for i in xrange(0,30000,1):
        points.append((x,y))
        vel = path(i)
        x += vel[0]
        y += vel[1]/time_scale
    pygame.draw.lines(surf,WHITE,False,points)
    surf.set_colorkey(BLACK)
    return surf
def path_img_pts(path,pos):
    x,y = pos
    points = []
    for i in xrange(0,30000,1):
        points.append((x,y))
        vel = path(i)
        x += vel[0]
        y += vel[1]
    pygame.draw.lines(DISPLAYSURF,WHITE,False,points)
def nearest_block(pos,sidelen):
    x,y = pos
    x /= sidelen
    x = int(round(x,1))
    x *= sidelen
    y /= sidelen
    y = int(round(y,1))
    y *= sidelen
    x += sidelen/2
    y += sidelen/2
    return x,y
def nearest_point(pos,sidelen):
    x,y = pos
    x += sidelen/2
    y += sidelen/2
    x /= sidelen
    y /= sidelen
    x*= sidelen
    y*= sidelen
    return x,y
def edit_level(enemies,off,curr_timeline):
    global time_scale,grid
    enem = None
    curr_enemy = 0
    curr_path = 1
    last_curr_path = 0
    curr_option = ''
    last_curr_enem = 0
    offset = off
    curr_path_img = make_path_img(Enemy.EnemyPath.paths[curr_path])
    display_grid = pygame.Surface((800,600)).convert()
    last_off = False
    for i in xrange(800/grid+1):
        for j in xrange(600/grid+1):
            pygame.draw.line(display_grid,RED,(i*grid,0),(i*grid,600),1)
            pygame.draw.line(display_grid,RED,(0,j*grid),(800,j*grid),1)
    font = pygame.font.Font(None,30)
    boss = None
    selected = pygame.sprite.Group()    

    while True:
        DISPLAYSURF.blit(display_grid,(0,0))
        for i in xrange(600/grid,-1,-1):
            DISPLAYSURF.blit(font.render("%s ms"%(int(grid*i+offset*grid)*time_scale),False,WHITE),(0,(600/grid-i)*grid))
        #pos = nearest_point(pygame.mouse.get_pos(),grid)
        #DISPLAYSURF.blit(font.render('%s,%s'%(pos[0],600-24-pos[1]+offset*grid),False,WHITE),(800-100,0))
        last_off = offset
        last_curr_enemy = curr_enemy
        last_curr_path = curr_path
        if boss:
            enem = boss
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return
                #sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1 and enem and not pygame.sprite.spritecollide(enem,enemies,False,pygame.sprite.collide_mask):
                    if pygame.key.get_mods() & KMOD_CAPS:
                        enem.rect.topleft = nearest_block(pygame.mouse.get_pos(),grid)
                    else:
                        enem.rect.center = nearest_block(pygame.mouse.get_pos(),grid)
                    if pygame.key.get_mods() & (KMOD_LSHIFT|KMOD_RSHIFT):
                        enem.rect.center = pygame.mouse.get_pos()
                    #time = (600-24-pos[1]+offset*grid)/time_scale
                    enemies.add(enem)
                    p = Enemy.EnemyPath.paths[curr_path]
                    if boss:
                        curr_enemy = 1
                        boss = None
                    enem = Enemy.Enemies.types[curr_enemy](p,pygame.mouse.get_pos())
                    enem.image = pygame.transform.scale(enem.image,(grid,grid))
                    enem.rect = enem.image.get_rect()
                elif event.button == 1 and not enem:
                    if not len(selected) or (pygame.key.get_mods()&(KMOD_LCTRL|KMOD_RCTRL)):
                        start = nearest_point(event.pos,grid)
                        end = (0,0)
                        surf = display_grid
                        rect = pygame.Rect(0,0,0,0)
                        while pygame.mouse.get_pressed()[0]:
                            pygame.event.pump()
                            end = nearest_point(pygame.mouse.get_pos(),grid)
                            DISPLAYSURF.blit(surf,(0,0))
                            for i in xrange(600/grid,-1,-1):
                                DISPLAYSURF.blit(font.render("%s ms"%(int(grid*i+offset*grid)*time_scale),False,WHITE),(0,(600/grid-i)*grid))

                            enemies.draw(DISPLAYSURF)
                            w = start[0]-end[0]
                            h = start[1]-end[1]
                            if w > 0: w += 1
##                            else: w -= 1
                            if h > 0: h += 1
##                            else: h -= 1
##                            left = start[0] if w >0 else end[0]
##                            top = start[1] if h<0 else end[1]
                            rect = pygame.Rect(start,(-w,-h))
                            rect.normalize()
                            pygame.draw.rect(DISPLAYSURF,GREEN,rect,1)
                            pygame.display.update()
                        for E in enemies:
                            if E.rect.colliderect(rect) or E.rect.collidepoint(pygame.mouse.get_pos()):
                                selected.add(E)
                    else:
                        coll = False
                        for E in selected:
                            if E.rect.collidepoint(pygame.mouse.get_pos()):
                                coll = True
                        if not coll:
                            for E in enemies:
                                if E.rect.collidepoint(pygame.mouse.get_pos()):
                                    coll = True
                                    selected.add(E)
                        if coll:
                            start = nearest_point(event.pos,grid)
                            dx,dy = 0,0
                            surf = display_grid
                            while pygame.mouse.get_pressed()[0]:
                                last_offset = offset
                                pygame.event.pump()
                                x,y = nearest_point(pygame.mouse.get_pos(),grid)
                                dx = start[0]-x
                                dy = start[1]-y
                                DISPLAYSURF.blit(surf,(0,0))
                                enemies.draw(DISPLAYSURF)
                                for i in xrange(600/grid,-1,-1):
                                    DISPLAYSURF.blit(font.render("%s ms"%(int(grid*i+offset*grid)*time_scale),False,WHITE),(0,(600/grid-i)*grid))

                                for E in selected:
                                    enemies.remove(E)
                                    DISPLAYSURF.blit(E.image,E.rect.move(-dx,-dy))
                                    pygame.draw.rect(DISPLAYSURF,GREEN,E.rect.move(-dx,-dy),1)
                                pygame.display.update()
                            for E in selected:
                                E.rect.move_ip(-dx,-dy)
                                enemies.add(E)
                            selected.empty()
                elif event.button == 3:
                    for E in enemies:
                        a,b = pygame.mouse.get_pos()
                        if E.rect.inflate(-2,-2).collidepoint((a,b)):
                            E.kill()
                elif event.button == 4:
                    offset += 1
                elif event.button == 5:
                    offset -= 1
            if event.type == KEYDOWN:
                if event.key in (K_w,K_s,K_a,K_d) and (not enem or enem == boss):
                    boss = None
                    curr_enemy = 1
                    p = Enemy.EnemyPath.paths[curr_path]
                    enem = Enemy.Enemies.types[curr_enemy](p,nearest_point(pygame.mouse.get_pos(),grid))
                    enem.image = pygame.transform.scale(enem.image,(grid,grid))
                    enem.rect = enem.image.get_rect()
                
                if enem and enem != boss:                       
                    if event.key == K_s and curr_enemy > 1:
                        curr_enemy -= 1
                    elif event.key == K_w and curr_enemy < 6:
                        curr_enemy += 1

                    elif event.key == K_a and curr_path > 1:
                        curr_path -= 1
                    elif event.key == K_d and curr_path < 13:
                        curr_path += 1
                        
                if event.key == K_RETURN:
                    save_level(enemies,offset)
                    print "SAVED!"
                    run_level('levels/temp.txt')
                elif event.key == K_ESCAPE:
                    curr_option = ''
                    enem = None

                elif event.key == K_UP:
                    offset +=1
                elif event.key == K_DOWN:
                    offset -= 1
                elif event.key == K_q:
                    for enemy in enemies:
                        enemy.rect.move_ip(0,grid)
                elif event.key == K_e:
                    for enemy in enemies:
                        enemy.rect.move_ip(0,-grid)
                elif event.key == K_b:
                    boss = Enemy.Boss((400,0))
                    boss.image = pygame.transform.scale(boss.image,(grid*4,grid*4))
                    boss.rect = boss.image.get_rect()
                elif event.key == K_DELETE:
                    if selected:
                        for E in selected:
                            E.kill()
                elif event.key == K_F5:
                    save_levelGUI(enemies,offset)
##                elif event.key == K_EQUALS:
##                    time_scale *= 2.0
##                elif event.key == K_MINUS:
##                    time_scale /= 2.0
##        pygame.event.pump()
        if curr_enemy>0 and enem and enem!= boss:
            if pygame.key.get_mods() & KMOD_CAPS:
                enem.rect.center = nearest_point(pygame.mouse.get_pos(),grid)
            else:
                enem.rect.center = nearest_block(pygame.mouse.get_pos(),grid)
            if pygame.key.get_mods() & (KMOD_LSHIFT|KMOD_RSHIFT):
                enem.rect.center = pygame.mouse.get_pos()
            DISPLAYSURF.blit(enem.image,enem.rect)
            path_img_pts(enem.path,enem.rect.center)
            fnt = pygame.font.Font(None,20)
            
            DISPLAYSURF.blit(fnt.render('PATH#:%s'%curr_path,False,WHITE),(300,0))
            DISPLAYSURF.blit(fnt.render('ENEMY#:%s'%curr_enemy,False,WHITE),(300,20))
            #DISPLAYSURF.blit(curr_path_img,enem.rect.move(-400+16,-400+16))
        if enem == boss and enem and boss:
            
            if pygame.key.get_mods() & KMOD_CAPS:
                enem.rect.center = nearest_point(pygame.mouse.get_pos(),grid)
            else:
                enem.rect.center = nearest_block(pygame.mouse.get_pos(),grid)
            if pygame.key.get_mods() & (KMOD_LSHIFT|KMOD_RSHIFT):
                enem.rect.center = pygame.mouse.get_pos()
            DISPLAYSURF.blit(enem.image,enem.rect)
        if offset < 0:
            offset = 0
            
##        if curr_path > 11: curr_path = 11
##        elif curr_path <1: curr_path = 1
##        
##        if curr_enemy > 4: curr_enemy = 4
##        elif curr_enemy < 1: curr_enemy = 1
        
        if last_curr_path != curr_path:
            curr_path_img = make_path_img(Enemy.EnemyPath.paths[curr_path])
            if enem:
                enem.path = Enemy.EnemyPath.paths[curr_path]
                
        if last_curr_enemy != curr_enemy:
            p = Enemy.EnemyPath.paths[curr_path]
            enem = Enemy.Enemies.types[curr_enemy](p,nearest_point(pygame.mouse.get_pos(),grid))
            enem.image = pygame.transform.scale(enem.image,(grid,grid))
            enem.rect = enem.image.get_rect()
        if len(selected):
            for E in selected:
                pygame.draw.rect(DISPLAYSURF,GREEN,E.rect,1)
        for enemy in enemies:
            DISPLAYSURF.blit(enemy.image,enemy.rect)
            if last_off < offset:
                enemy.rect.move_ip(0,grid)
            elif last_off > offset:
                enemy.rect.move_ip(0,-grid)
            if enemy.rect.collidepoint(pygame.mouse.get_pos()) and type(enemy)!=Enemy.Boss:
                path_img_pts(enemy.path,enemy.rect.center)
        pygame.display.update()
def load_level(timeline='levels/temp.txt'):
    global time_scale,grid
    enemies = pygame.sprite.Group()
    f = open(timeline)
    for line in f:
        line = line.strip()
        line = line.split(':')
        if (eval(line[1]))=='B':
            y = 600-24-int(line[0])/time_scale
            x = eval(line[4])[0]
            E = Enemy.Boss()
            E.rect = E.image.get_rect()
            E.rect.topleft = (x,y)
            enemies.add(E)
        else:
            y = 600-24-int(line[0])/time_scale
            x = eval(line[4])[0]
            path = Enemy.EnemyPath.paths[eval(line[3])]
            enemy = Enemy.Enemies.types[eval(line[1])]
            E = enemy(path,(x,y))
            E.image = pygame.transform.scale(E.image,(grid,grid))
            E.rect = E.image.get_rect()
            E.rect.topleft = (x,y)
            enemies.add(E)
    f.close()
    return enemies

def save_levelGUI(enemies,offset):
    surf = DISPLAYSURF.copy()
    r = pygame.Rect(0,0,800,600)
    pygame.draw.rect(surf,(0,0,0,128),r,0)
    f = pygame.font.Font(None,30)
    save_message = f.render('Name of File',False,WHITE)
    TField = Text.TextField('all')
    txt = TField.text_input(surf,'Name of File')
    if not (txt.endswith('.txt') or txt.endswith('.TXT')):
        txt += '.txt'
    txt = 'levels/%s'%txt
    save_level(enemies,offset,txt)
    print txt
def save_level(enemies,offset,f = 'levels/temp.txt'):
    global time_scale,grid
    orig  = offset
    while offset > 0:
        for enemy in enemies:
            enemy.rect.move_ip(0,-grid)
        offset -= 1
    timeline = []
    for enemy in enemies:
        x,y = enemy.rect.topleft
        if type(enemy) != Enemy.Boss:
            enem_num = Enemy.get_enemy(enemy)
            path_num = Enemy.get_path(enemy.path)
            time = (-y+600-24)*time_scale
            evt = [time,enem_num,0,path_num,(x,0)]
            timeline.append(evt)
        else:
            time = (-y+600-24)*time_scale
            evt = [time,'B',0,1,(x,0)]
            timeline.append(evt)
    timeline = sorted(timeline,key = lambda l:l[0])
    f = open(f,'w')
    for line in timeline:
        out = repr(line)
        out = filter(lambda c:c not in (' []'),out)
        out = out.replace(',',':',4)
        out += '\n'
        f.write(out)
    f.close()
    while offset < orig:
        for enemy in enemies:
            enemy.rect.move_ip(0,grid)
        offset += 1
def load_level_list(timeline):
    global time_scale,grid
    enemies = pygame.sprite.Group()
    for line in timeline:
        line = line.strip()
        line = line.split(':')
        if (eval(line[1]))=='B':
            y = 600-24-eval(line[0])/time_scale
            x = eval(line[4])[0]
            E = Enemy.Boss()
            E.rect = E.image.get_rect()
            E.rect.topleft = (x,y)
            enemies.add(E)
        else:
            y = 600-24-eval(line[0])/time_scale
            x = eval(line[4])[0]
            path = Enemy.EnemyPath.paths[eval(line[3])]
            enemy = Enemy.Enemies.types[eval(line[1])]
            E = enemy(path,(x,y))
            E.image = pygame.transform.scale(E.image,(grid,grid))
            E.rect = E.image.get_rect()
            E.rect.topleft = nearest_block((x,y),grid)
            E.rect.move_ip(-grid/2,-grid/2)
            enemies.add(E)
    return enemies
def gen_random_level(grd,ts,level = 1):
    import math
    #global grid,time_scale
    time = 0
    timeline = []
    num_turrets = 0
    turret_time = 0
    while time < 60000:
        enemy_num = random.randrange(3,7)
        path_num = random.randrange(1,14)
        x = 0
        
        while enemy_num in (3,5) and num_turrets > 5 and time - turret_time < 10000:
            enemy_num = random.randrange(3,7)
        if num_turrets > 5 and time - turret_time >= 10000:
            num_turrets = 0
            turret_time = 0
            
        if path_num in (2,4,6,8,10,12) and enemy_num in (6,5):
            x = random.randrange(0,400)
        elif path_num in (3,5,7,9,11,13) and enemy_num in (6,5):
            x = random.randrange(400,800)
        else:
            x = random.randrange(30,800-30)
        t,x = nearest_point((time,x),grd)
        evt = '%s:%s:0:%s:(%s,0)'%(int(t),enemy_num,path_num,x)
        timeline.append(evt)
        if enemy_num in (6,5):
            dx = 0
            dt = 0
            if path_num in (2,4,8,10):
                dx = random.randrange(2)
                dt = 1
                if not dx:
                    dt = random.randrange(2)
            elif path_num in (3,5,9,11):
                dx = -random.randrange(2)
                dt = 1
                if not dx:
                    dt = random.randrange(2)
            elif path_num in (1,6,7,12,13):
                if path_num in (6,12):
                    dx = 1
                elif path_num in (7,13):
                    dx = -1
                if x < 0 or x > 800:
                    break
            if not dt and not dx:
                dt = 1
            for i in xrange(random.randrange(3,5)):
                if enemy_num == 5:
                    num_turrets += 1
                    turret_time = t
                    if num_turrets > 5:
                        break
                t += grd*ts*dt
                x -= grd*dx
                if x <0: break
                t,x = nearest_point((t,x),grd)
                evt = '%s:%s:0:%s:(%s,0)'%(t,enemy_num,path_num,x)
                timeline.append(evt)
        time += random.randrange(10,15)*grd*ts*(.5**(level/5))#/(math.log(level+2))
    time += 2000#random.randrange(3,7)*grd*ts
    t,x = nearest_point((time,x),grd)
    evt = '%s:%s:0:%s:(%s,0)'%(t,'\'B\'',0,400)
    timeline.append(evt)
    return timeline
def run_level(timelinefile):
    import main
    pygame.mixer.quit()
    pygame.mixer.pre_init(channels = 4,buffer = 128)#1024/2)
    pygame.mixer.init()
    level = main.Level()
    level.init()
    level.load(timelinefile)
    level.run()
    DISPLAYSURF = pygame.display.set_mode((800,600))
    pygame.mouse.set_visible(True)
if __name__ == '__main__':
    #pygame.init()
    global DISPLAYSURF,time_scale,grid
    time_scale = 4
    grid = 30
    #font1 = pygame.font.Font(None,60)
    #DISPLAYSURF = pygame.display.set_mode((800,600))
    #pygame.display.iconify()
    all_enem = pygame.sprite.Group()
    done = False
    options = "1:new level\n2:edit level\n3:quit\n"
##    while not done:
##        choice = raw_input(options)
##        if choice in ('1','2','3'):
##            if choice == '1':
##                pygame.init()
##                DISPLAYSURF = pygame.display.set_mode((800,600))
##                edit_level(all_enem,0,[])
##            elif choice == '2':
##                name = raw_input("level file name:")
##                if name+'.txt' in os.listdir("levels"):
##                    pygame.init()
##                    DISPLAYSURF = pygame.display.set_mode((800,600))
##                    all_enem = load_level('levels/'+name+'.txt')
##                    edit_level(all_enem,0,[])
##            elif choice == '3':
##                pygame.quit()
##                sys.exit()
    pygame.init()
    DISPLAYSURF = pygame.display.set_mode((800,600))
    all_enem = load_level_list(gen_random_level(grid,time_scale,level = 1))#load_level('levels/testlvel.txt')
    offset = 0
    edit_level(all_enem,0,[])
    
