import pygame
import sys
from map import Map, SCREEN_HEIGHT, SCREEN_WIDTH, DOOR_THICKNESS

def lancer_jeu():
    """Lance le jeu principal."""
    pygame.init()

    # Fenêtre
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mini Isaac")

    clock = pygame.time.Clock()

    # Couleurs
    WHITE = (255, 255, 255)
    RED = (200, 50, 50)
    BLUE = (50, 100, 255)
    BLACK = (0, 0, 0)

    class Player:
        def __init__(self):
            """Initialise le joueur avec une position et une vitesse."""
            self.rect = pygame.Rect(400, 300, 40, 40)
            self.speed = 5

        def move(self, keys):
            """Déplace le joueur selon les touches pressées."""
            if keys[pygame.K_w]:
                self.rect.y -= self.speed
            if keys[pygame.K_s]:
                self.rect.y += self.speed
            if keys[pygame.K_a]:
                self.rect.x -= self.speed
            if keys[pygame.K_d]:
                self.rect.x += self.speed
        def collide_walls(self, current_room):
            """Empêche le joueur de traverser les murs et les portes fermées."""
            if self.rect.left < 0:
                self.rect.left = 0
            if self.rect.right > SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH
            if self.rect.top < 0:
                self.rect.top = 0
            if self.rect.bottom > SCREEN_HEIGHT:
                self.rect.bottom = SCREEN_HEIGHT

            # Bloque les portes fermées ou inexistantes
            for direction, door_rect in current_room.doors.items():
                # Porte inactive (mur) ou porte active mais salle non vidée
                is_blocked = (
                    direction not in current_room.active_doors or
                    not current_room.cleared
                )
                if is_blocked and self.rect.colliderect(door_rect):
                    if direction == "up":
                        self.rect.top = door_rect.bottom
                    elif direction == "down":
                        self.rect.bottom = door_rect.top
                    elif direction == "left":
                        self.rect.left = door_rect.right
                    elif direction == "right":
                        self.rect.right = door_rect.left

        def draw(self):
            """Dessine le joueur sur l'écran."""
            pygame.draw.rect(screen, BLUE, self.rect)

    class Bullet:
        def __init__(self, x, y, dx, dy):
            """Initialise la balle avec une position et une direction."""
            self.rect = pygame.Rect(x, y, 10, 10)
            self.dx = dx
            self.dy = dy
            self.speed = 8

        def update(self):
            """Met à jour la position de la balle."""
            self.rect.x += self.dx * self.speed
            self.rect.y += self.dy * self.speed

        def draw(self):
            """Dessine la balle sur l'écran."""
            pygame.draw.rect(screen, WHITE, self.rect)

    

    player = Player()
    bullets = []
    game_map = Map()

    shoot_cooldown = 0
    running = True

    while running:
        clock.tick(60)
        screen.fill(BLACK)

        keys = pygame.key.get_pressed()


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        player.move(keys)

        
        if shoot_cooldown > 0:
            shoot_cooldown -= 1

        if shoot_cooldown == 0:
            if keys[pygame.K_i]:
                bullets.append(Bullet(player.rect.centerx, player.rect.centery, 0, -1))
                shoot_cooldown = 10
            if keys[pygame.K_k]:
                bullets.append(Bullet(player.rect.centerx, player.rect.centery, 0, 1))
                shoot_cooldown = 10
            if keys[pygame.K_j]:
                bullets.append(Bullet(player.rect.centerx, player.rect.centery, -1, 0))
                shoot_cooldown = 10
            if keys[pygame.K_l]:
                bullets.append(Bullet(player.rect.centerx, player.rect.centery, 1, 0))
                shoot_cooldown = 10

        
        for bullet in bullets[:]:
            bullet.update()

            if not screen.get_rect().colliderect(bullet.rect):
                bullets.remove(bullet)
                continue

            for enemy in game_map.current_room.enemies:
                if enemy.hp > 0 and bullet.rect.colliderect(enemy.rect):
                    bullets.remove(bullet)
                    enemy.hp -= 1
                    break

        
        game_map.update(player)
        game_map.draw(screen)  

        
        player.draw()

        for bullet in bullets:
            bullet.draw()

        pygame.display.flip()
    
    
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    lancer_jeu()