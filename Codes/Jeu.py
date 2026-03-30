import pygame
import sys

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

    def move(self, keys):
        if keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_s]:
            self.rect.y += self.speed
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_d]:
            self.rect.x += self.speed

    def draw(self):
        pygame.draw.rect(screen, BLUE, self.rect)


class Bullet:
    def __init__(self, x, y, dx, dy):
        self.rect = pygame.Rect(x, y, 10, 10)
        self.dx = dx
        self.dy = dy
        self.speed = 8

    def update(self):
        self.rect.x += self.dx * self.speed
        self.rect.y += self.dy * self.speed

    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect)


class Enemy:
    def __init__(self):
        self.rect = pygame.Rect(100, 100, 40, 40)
        self.speed = 2
        self.hp = 3

    def update(self, player):
        if player.rect.x < self.rect.x:
            self.rect.x -= self.speed
        if player.rect.x > self.rect.x:
            self.rect.x += self.speed
        if player.rect.y < self.rect.y:
            self.rect.y -= self.speed
        if player.rect.y > self.rect.y:
            self.rect.y += self.speed

    def draw(self):
        pygame.draw.rect(screen, RED, self.rect)



player = Player()
enemy = Enemy()
bullets = []

shoot_cooldown = 0


running = True
while running:
    clock.tick(60)
    screen.fill(BLACK)

    keys = pygame.key.get_pressed()

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Déplacement joueur
    player.move(keys)

    # Tir 
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

    # Update balles
    for bullet in bullets[:]:
        bullet.update()

        # supprimer si hors écran
        if not screen.get_rect().colliderect(bullet.rect):
            bullets.remove(bullet)

        # collision ennemi
        if bullet.rect.colliderect(enemy.rect):
            bullets.remove(bullet)
            enemy.hp -= 1

    # Update ennemi
    if enemy.hp > 0:
        enemy.update(player)

    player.draw()

    for bullet in bullets:
        bullet.draw()

    if enemy.hp > 0:
        enemy.draw()

    pygame.display.flip()

pygame.quit()
sys.exit()