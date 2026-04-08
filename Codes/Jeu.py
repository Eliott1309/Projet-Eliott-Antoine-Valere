import pygame
import sys
from map import Map, SCREEN_HEIGHT, SCREEN_WIDTH

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
            self.rect = pygame.Rect(400, 300, 40, 40)
            self.speed = 5
            self.hp = 5

        def move(self, keys, game_map):
            """Déplace le joueur axe par axe avec collisions."""
            dx, dy = 0, 0

            if keys[pygame.K_a]: dx -= 1
            if keys[pygame.K_d]: dx += 1
            if keys[pygame.K_w]: dy -= 1
            if keys[pygame.K_s]: dy += 1

            # Normalisation : si on bouge en diagonale, on réduit la vitesse
            if dx != 0 and dy != 0:
                dx *= 0.7071  # 1 / √2
                dy *= 0.7071

            # Axe horizontal
            self.rect.x += dx * self.speed
            self._resolve_collisions(game_map, axis="x")

            # Axe vertical
            self.rect.y += dy * self.speed
            self._resolve_collisions(game_map, axis="y")

        def _resolve_collisions(self, game_map, axis):
            current_room = game_map.current_room

            for wall_rect in current_room.get_wall_rects():
                if self.rect.colliderect(wall_rect):
                    if axis == "x":
                        if self.rect.centerx < wall_rect.centerx:
                            self.rect.right = wall_rect.left
                        else:
                            self.rect.left = wall_rect.right
                    elif axis == "y":
                        if self.rect.centery < wall_rect.centery:
                            self.rect.bottom = wall_rect.top
                        else:
                            self.rect.top = wall_rect.bottom

            for direction, door_rect in current_room.get_door_rects().items():
                if self.rect.colliderect(door_rect):
                    if current_room.cleared:
                        dx, dy = current_room.door_directions[direction]
                        game_map.change_room(dx, dy, self)
                        return
                    else:
                        if axis == "x":
                            if self.rect.centerx < door_rect.centerx:
                                self.rect.right = door_rect.left
                            else:
                                self.rect.left = door_rect.right
                        elif axis == "y":
                            if self.rect.centery < door_rect.centery:
                                self.rect.bottom = door_rect.top
                            else:
                                self.rect.top = door_rect.bottom
        def draw(self):
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

        player.move(keys, game_map)
        
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