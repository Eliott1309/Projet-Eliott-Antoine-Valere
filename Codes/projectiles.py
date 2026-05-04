import pygame



class Bullet:
    def __init__(self, x, y, dx, dy, damage=1, max_distance=800,
                 color=(255, 255, 255), size=10, pierce=1, magic=False, image=None):
        self.rect = pygame.Rect(x, y, size, size)
        self.dx, self.dy = dx, dy
        self.speed = 8
        self.damage = damage
        self.max_distance = max_distance
        self.distance_travelled = 0
        self.color = color
        self.pierce = pierce
        self.magic  = magic
        self.image = image
        self.hit_enemies = set()
        self.trail = []

    def update(self):
        self.trail.append((self.rect.centerx, self.rect.centery))
        if len(self.trail) > 6:
            self.trail.pop(0)
        self.rect.x += self.dx * self.speed
        self.rect.y += self.dy * self.speed
        self.distance_travelled += self.speed

    def draw(self, surface):
        for i, (tx, ty) in enumerate(self.trail):
            ratio = i / max(1, len(self.trail))
            alpha = int(180 * ratio)
            size = max(1, int(self.rect.width * ratio * 0.7))
            s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (size, size), size)
            surface.blit(s, (tx - size, ty - size))
        if self.image:
            angle = 0
            if self.dx < 0:
                angle = 180
            elif self.dy < 0:
                angle = 90
            elif self.dy > 0:
                angle = -90
            image = pygame.transform.rotate(self.image, angle)
            surface.blit(image, image.get_rect(center=self.rect.center))
        else:
            pygame.draw.rect(surface, self.color, self.rect)

class Explosion:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.radius = 55
        self.timer  = 12

    def update(self): self.timer -= 1

    def draw(self, surface):
        pygame.draw.circle(surface, (170, 90, 255), (self.x, self.y), self.radius, 3)

class EnemyBullet:
    def __init__(self, x, y, dx, dy, damage=1, color=(255, 90, 70), size=8, speed=4):
        length = max(1, (dx*dx + dy*dy) ** 0.5)
        self.rect = pygame.Rect(x - size//2, y - size//2, size, size)
        self.dx = dx / length
        self.dy = dy / length
        self.damage = damage
        self.color = color
        self.speed = speed
        self.trail = []

    def update(self):
        self.trail.append((self.rect.centerx, self.rect.centery))
        if len(self.trail) > 5:
            self.trail.pop(0)
        self.rect.x += self.dx * self.speed
        self.rect.y += self.dy * self.speed

    def draw(self, surface):
        for i, (tx, ty) in enumerate(self.trail):
            ratio = i / max(1, len(self.trail))
            alpha = int(140 * ratio)
            size = max(1, int(self.rect.width * ratio * 0.5))
            s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (size, size), size)
            surface.blit(s, (tx - size, ty - size))
        pygame.draw.circle(surface, self.color, self.rect.center, self.rect.width//2)

