import pygame,sys
from pygame.locals import *
from constants import *
class TextField(pygame.sprite.Sprite):
    def __init__(self,allowed = '', message = ''):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.text = ''
        self.active = False
        self.is_expression_box = False
        self.image = pygame.Surface((0,0))
        self.rect = self.image.get_rect()
        if allowed == 'all':
            self.allowed = ''
        elif allowed == 'numbers':
            self.allowed = '0123456789.+-/*'
            self.specific = ['sqrt','^','sin','cos','tan','ln']

        else:
            self.allowed = set(allowed+allowed.upper())
        self.message = message
    def text_input(self, surface,message = '', loc = (0,0),overlay = None,maxlen = 0):
        if type(loc) == pygame.Rect:
            loc = loc.bottomleft
        font = pygame.font.SysFont('consolas',20)
        if maxlen:
            self.image = pygame.Surface(font.size('-'*maxlen))
            print self.image.get_size()
        text = ''
        key_sequence = []
        filtr = '[],():\''
        mods = pygame.key.get_mods
        mod_keys = (K_UP,K_DOWN,K_RIGHT,K_LEFT,K_INSERT,K_HOME,
                    K_END,K_PAGEUP,K_PAGEDOWN,K_F1,K_F2,K_F3,
                    K_F4,K_F5,K_F6,K_F7,K_F8,K_F9,K_F10,K_F11,
                    K_F12,K_F13,K_F14,K_F15,K_NUMLOCK,K_CAPSLOCK,
                    K_SCROLLOCK,K_RSHIFT,K_LSHIFT,K_RCTRL,K_LCTRL,K_RALT)
        num_shift = {'1':'!','2':'@','3':'#','4':'$','5':'%',
                     '6':'^','7':'&','8':'*','9':'(','0':')',
                     '-':'_','=':'+',',':'<','.':'>','/':'?',
                     '[':'{',']':'}','\\':'|','`':'~'}
        DISPLAYSURF = pygame.display.get_surface()
        if type(overlay) != pygame.sprite.Group:
            overlay = pygame.sprite.Group()
        while True:
            img_txt = font.render(text,False,WHITE)
            mssg_txt = font.render(message,False,WHITE)
            width = 0
            if not maxlen:
                width = int(max(img_txt.get_width(),mssg_txt.get_width()))
            else:
                width = int(font.size('-'*maxlen)[0])
            self.image = pygame.Surface((width,img_txt.get_height()+mssg_txt.get_height()))
            self.image.fill(BLACK)
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_BACKSPACE:
                        text = text[:-1]
                    elif event.key in(K_RETURN,271) :
                        if not self.is_expression_box:
                            return text
                        else:
                            return text
                    else:
                        key = ''

                        #normal keys
                        if event.key <= 256:
                            #handles shift
                            if mods() & ((pygame.KMOD_LSHIFT | pygame.KMOD_RSHIFT)^pygame.KMOD_CAPS):
                                if chr(event.key) not in ('1234567890-=[]\,.//`'):
                                    key = chr(event.key).upper()
                                else:
                                    key = num_shift[chr(event.key)]
                            else:
                                key = chr(event.key)
                        #handles numpad input
                        elif event.key >256 and event.key not in mod_keys:
                            key = pygame.key.name(event.key)
                            if '[' in key:
                                key = key.strip('[]')
                        if (key in self.allowed) or (self.allowed == '' and event.key != K_ESCAPE) and len(text)+1<maxlen:
                            text += key
            img_txt = font.render(text,False,WHITE)
            self.image.blit(img_txt,(0,mssg_txt.get_height()))
            self.image.blit(mssg_txt,(0,0))
            pygame.draw.rect(self.image,BLUE,(0,mssg_txt.get_height(),width,img_txt.get_height()),1)
            DISPLAYSURF.blit(surface,(0,0))
            rect = self.image.get_rect(topleft = loc)
            rect = rect.clamp(DISPLAYSURF.get_rect())
            self.image.set_colorkey(BLACK)
            DISPLAYSURF.blit(self.image,rect)
            pygame.display.update()
