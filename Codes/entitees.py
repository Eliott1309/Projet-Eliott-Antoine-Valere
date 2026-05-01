import pygame
import random

class Enemy:
    def __init__(self, x=400, y=300):
        self.rect = pygame.Rect(x - 20, y - 20, 40, 40)
        self.speed = 2
        self.hp = 3

    def update(self, player, wall_rects=None):
        dx = 0
        dy = 0

        if player.rect.x < self.rect.x: dx = -1
        if player.rect.x > self.rect.x: dx = 1
        if player.rect.y < self.rect.y: dy = -1
        if player.rect.y > self.rect.y: dy = 1

        if wall_rects:
            # Axe X
            self.rect.x += dx * self.speed
            for wall in wall_rects:
                if self.rect.colliderect(wall):
                    if dx > 0: self.rect.right = wall.left
                    else:      self.rect.left  = wall.right

            # Axe Y
            self.rect.y += dy * self.speed
            for wall in wall_rects:
                if self.rect.colliderect(wall):
                    if dy > 0: self.rect.bottom = wall.top
                    else:      self.rect.top    = wall.bottom
        else:
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed

    def draw(self, screen, assets):
        screen.blit(assets["enemy"], self.rect)