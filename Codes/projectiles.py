import pygame



class Bullet:
    #prepare un tir du joueur avec sa direction, ses degats et son image si il en a une
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

    #fait avancer le projectile et garde une petite trainee derriere lui
    def update(self):
        self.trail.append((self.rect.centerx, self.rect.centery))
        if len(self.trail) > 6:
            self.trail.pop(0)
        self.rect.x += self.dx * self.speed
        self.rect.y += self.dy * self.speed
        self.distance_travelled += self.speed

    #dessine le tir et sa trainee, soit avec une image soit avec un rectangle simple
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
    #cree une explosion simple avec une position, un rayon et un timer assez court
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.radius = 55
        self.timer  = 12

    #reduis le timer pour que l'explosion disparaisse toute seule
    def update(self): self.timer -= 1

    #dessine le cercle violet de l'explosion sur la surface du jeu
    def draw(self, surface):
        pygame.draw.circle(surface, (170, 90, 255), (self.x, self.y), self.radius, 3)

class EnemyBullet:
    #prepare un tir ennemi, ca normalise la direction pour qu'il parte bien droit
    def __init__(self, x, y, dx, dy, damage=1, color=(255, 90, 70), size=8, speed=4):
        length = max(1, (dx*dx + dy*dy) ** 0.5)
        self.rect = pygame.Rect(x - size//2, y - size//2, size, size)
        self.dx = dx / length
        self.dy = dy / length
        self.damage = damage
        self.color = color
        self.speed = speed
        self.trail = []

    #avance le tir ennemi et garde ses anciennes positions pour la trainee
    def update(self):
        self.trail.append((self.rect.centerx, self.rect.centery))
        if len(self.trail) > 5:
            self.trail.pop(0)
        self.rect.x += self.dx * self.speed
        self.rect.y += self.dy * self.speed

    #dessine le projectile ennemi avec un petit effet derriere lui
    def draw(self, surface):
        for i, (tx, ty) in enumerate(self.trail):
            ratio = i / max(1, len(self.trail))
            alpha = int(140 * ratio)
            size = max(1, int(self.rect.width * ratio * 0.5))
            s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (size, size), size)
            surface.blit(s, (tx - size, ty - size))
        pygame.draw.circle(surface, self.color, self.rect.center, self.rect.width//2)

