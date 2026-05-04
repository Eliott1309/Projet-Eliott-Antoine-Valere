import random
import pygame
from config_carte import SCREEN_WIDTH, SCREEN_HEIGHT


class Item:
    def __init__(self, x, y, item_type):
        self.rect = pygame.Rect(x - 14, y - 14, 28, 28)
        self.type = item_type

    def draw(self, screen, assets):
        if self.type in assets:
            pulse = 2 if pygame.time.get_ticks() // 260 % 2 == 0 else 0
            screen.blit(assets[self.type], self.rect.inflate(pulse, pulse))


class Chest:
    def __init__(self, x, y, chest_type="start"):
        self.rect = pygame.Rect(x - 18, y - 18, 36, 36)
        self.opened = False
        self.open_timer = 0
        self.chest_type = chest_type

    def draw(self, screen, assets):
        if self.opened:
            return
        bob = 2 if pygame.time.get_ticks() // 300 % 2 == 0 else 0
        draw_rect = self.rect.move(0, -bob)
        screen.blit(assets["chest"], draw_rect)
        if pygame.time.get_ticks() // 180 % 5 == 0:
            pygame.draw.line(screen, (255, 240, 160), draw_rect.topleft, draw_rect.center, 1)

    def open(self):
        self.opened = True
        if self.chest_type == "start":
            return random.choice(["sword", "crossbow"])
        rewards = ["heart", "heart", "damage_boost", "speed_boost", "range_boost",
                   "range_boost", "sword", "crossbow", "bow", "magic_wand"]
        return random.choice(rewards)


class ExitPortal:
    def __init__(self):
        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2
        self.rect = pygame.Rect(cx - 24, cy - 24, 48, 48)
        self.active = False
        self.anim = 0

    def update(self):
        if self.active:
            self.anim = (self.anim + 1) % 60

    def draw(self, screen):
        if not self.active:
            return
        pulse = abs(30 - self.anim) / 30
        radius = int(28 + 10 * pulse)
        halo = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(halo, (160, 80, 255, 80), (radius, radius), radius)
        screen.blit(halo, (self.rect.centerx - radius, self.rect.centery - radius))
        pygame.draw.circle(screen, (200, 130, 255), self.rect.center, 20)
        pygame.draw.circle(screen, (255, 255, 255), self.rect.center, 20, 2)
        font = pygame.font.Font(None, 20)
        label = font.render("SORTIE", True, (255, 255, 255))
        screen.blit(label, (self.rect.centerx - label.get_width() // 2, self.rect.bottom + 6))

