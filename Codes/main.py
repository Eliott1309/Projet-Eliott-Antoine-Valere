import pygame
import sys
import subprocess
from assets import load_assets
from jeu import lancer_jeu
import os
base = os.path.dirname(os.path.abspath(__file__))

#test
def start():
    lancer_jeu()

pygame.init()



#fenetre
WIDTH, HEIGHT = 1080,720

#resssource
'''permet de mettre les images, musiques etc en fond'''

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Bindings of Isaac") #mettre nouveau nom du jeu 

base = os.path.dirname(os.path.abspath(__file__))  # â† juste avant les ressources

background = pygame.image.load(os.path.join(base, "assets", "bg.jpeg"))
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

pygame.mixer.music.load(os.path.join(base, "assets", "music.mp3"))
pygame.mixer.music.play(-1)
#couleurs
'''J'initie les couleurs pour que ca soit plus simple de les mettre pour les boutons'''
WHITE = (255, 255, 255)
TRANSLUCENT_BLUE = (0, 80, 200, 180)
HOVER_BLUE = (0,140, 255, 220) 
SHADOW = (0, 0, 0)
assets = load_assets()

#polices
try : 
    FONT_TITLES = pygame.font.Font("../Assets/medieval.ttf", 72)
    FONT_BUTTON = pygame.font.Font("../Assets/medieval.ttf", 36)

except :
    FONT_TITLES = pygame.font.Font(None, 72)
    FONT_BUTTON = pygame.font.Font(None, 36)

class Button:
    def __init__(self,text,center_y,action):
        self.text = text
        self.action = action
        self.center_y = center_y
        self.width, self.height = 320,70 
        self.rect = pygame.Rect(0,0, self.width, self.height)
        self.rect.center = (WIDTH//2, center_y)

    def draw(self, win, mouse_pos): #Je cree une fonction pour changer de couleur un bouton quand il est survole
        is_hover = self.rect.collidepoint(mouse_pos)
        color = HOVER_BLUE if is_hover else TRANSLUCENT_BLUE
        button_surface = pygame.Surface((self.width,self.height), pygame.SRCALPHA)
        pygame.draw.rect(button_surface, color, (0,0,self.width, self.height), border_radius=16) #je cree un rectangle pour les boutons
        win.blit(button_surface, self.rect) #afficher le bouton 

        text_surf = FONT_BUTTON.render(self.text, True, WHITE) #crer limage du texte
        text_rect = text_surf.get_rect(center=self.rect.center) #centre le texte

#je cree une legere ombre
        shadow = FONT_BUTTON.render(self.text, True, SHADOW) 
        win.blit(shadow, (text_rect.x+2, text_rect.y+2))
        win.blit(text_surf, text_rect)

    
    def is_clicked(self, mouse_pos, mouse_pressed):
        return self.rect.collidepoint(mouse_pos) and mouse_pressed[0] #retourne true si ya clic gauche sur le bouton


#liste des boutons

buttons = [
    Button("Nouvelle Partie", 320, "new",),
    Button("Charger Partie", 400, "load"),
    Button("Options", 480, "options"),
    Button("Quitter", 560, "quit")
]
option_buttons = [
    Button("Changer clavier", 390, "switch_layout"),
    Button("Retour", 500, "back")
]




#boucle principale du menu

running = True
clock = pygame.time.Clock()
keyboard_layout = "azerty"
menu_state = "main"


while running:
    clock.tick(60)
    screen.blit(background, (0,0))

    mouse_pos = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()

    title = FONT_TITLES.render("Bindings of Isaac", True, WHITE) #partie esthetique du menu
    shadow = FONT_TITLES.render("Bindings of Isaac", True, SHADOW) #titre a changer
    screen.blit(shadow, (WIDTH//2 - title.get_width()//2 + 3, 103)) #j'affiche l'ombre legerement decalee 
    screen.blit(title, (WIDTH//2 - title.get_width()//2 , 100)) #affichage du texte principal

    #je definis ce que font les boutons
    if menu_state == "main":
        for btn in buttons:
            btn.draw(screen, mouse_pos)
            if btn.is_clicked(mouse_pos, mouse_pressed):
                pygame.time.delay(200)
                if btn.action == "new":
                    print("Nouvelle Partie")
                    running = False
                    pygame.quit()
                    lancer_jeu(keyboard_layout, assets)
                elif btn.action == "load":
                    running = False
                    pygame.quit()
                    lancer_jeu(keyboard_layout, assets, charger=True)
                elif btn.action == "options":
                    menu_state = "options"
                elif btn.action == "quit":
                    running = False

    elif menu_state == "options":
        option_title = FONT_BUTTON.render("Options", True, WHITE)
        screen.blit(option_title, (WIDTH//2 - option_title.get_width()//2, 250))

        current = FONT_BUTTON.render("Clavier : " + keyboard_layout.upper(), True, WHITE)
        screen.blit(current, (WIDTH//2 - current.get_width()//2, 310))

        for btn in option_buttons:
            btn.draw(screen, mouse_pos)
            if btn.is_clicked(mouse_pos, mouse_pressed):
                pygame.time.delay(200)
                if btn.action == "switch_layout":
                    if keyboard_layout == "azerty":
                        keyboard_layout = "qwerty"
                    else:
                        keyboard_layout = "azerty"
                elif btn.action == "back":
                    menu_state = "main"

    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
             running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()
    
    pygame.display.flip()

pygame.quit()
print("fermeture du jeu")
