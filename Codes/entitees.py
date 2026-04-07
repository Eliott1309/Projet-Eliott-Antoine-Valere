import pygame
import random

class Enemy:
    def __init__(self):
        self.rect = pygame.Rect(
            random.randint(100, 700),
            random.randint(100, 500),
            40, 40
        )
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

    def draw(self, screen):
        pygame.draw.rect(screen, (200, 50, 50), self.rect)