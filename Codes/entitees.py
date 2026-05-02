import pygame
import random
import math

DETECTION_RADIUS = 210   # pixels — en dessous : l'ennemi commence à chasser
WANDER_CHANGE    = 80    # frames entre deux changements de direction en errance


class Enemy:
    # Comportements possibles (tirés au sort à la création)
    BEHAVIORS = ["chaser", "patrol", "cautious"]

    def __init__(self, x=400, y=300):
        self.rect  = pygame.Rect(x - 20, y - 20, 40, 40)
        self.speed = 2
        self.hp    = 3

        self.behavior      = random.choice(self.BEHAVIORS)
        self.state         = "idle"      # idle | alert | chase | wander | patrol
        self.alert_timer   = 0           # frames de mise en alerte avant d'attaquer
        self.wander_timer  = 0           # compteur pour changer de direction
        self.wander_dir    = self.random_dir()
        self.patrol_points = []          # défini après spawn dans map.py si besoin
        self.patrol_index  = 0
        self.spawn_x       = x
        self.spawn_y       = y

    def random_dir(self):
        angle = random.uniform(0, 2 * math.pi)
        return math.cos(angle), math.sin(angle)

    def dist(self, player):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        return math.hypot(dx, dy), dx, dy

    def move(self, dx, dy, wall_rects):
        if dx == 0 and dy == 0:
            return
        length = math.hypot(dx, dy)
        dx, dy = dx / length, dy / length

        self.rect.x += dx * self.speed
        for wall in wall_rects:
            if self.rect.colliderect(wall):
                self.rect.x = self.rect.x - dx * self.speed
                self.wander_dir = self.random_dir()
                break

        self.rect.y += dy * self.speed
        for wall in wall_rects:
            if self.rect.colliderect(wall):
                self.rect.y = self.rect.y - dy * self.speed
                self.wander_dir = self.random_dir()
                break

    def update(self, player, wall_rects=None):
        if wall_rects is None:
            wall_rects = []

        d, dx, dy = self.dist(player)

        if self.state not in ("alert", "chase") and d < DETECTION_RADIUS:
            self.state       = "alert"
            self.alert_timer = 40

        if self.state == "chase" and d > DETECTION_RADIUS * 1.8:
            self.state = "wander"

        if self.state == "idle":
            self.idle()
        elif self.state == "alert":
            self.alert_timer -= 1
            if self.alert_timer <= 0:
                self.state = "chase"
        elif self.state == "chase":
            self.chase(dx, dy, d, wall_rects)
        elif self.state == "wander":
            self.wander(wall_rects)
        elif self.state == "patrol":
            self.patrol(wall_rects)

    def idle(self):
        if random.random() < 0.005:
            self.state        = "wander"
            self.wander_timer = WANDER_CHANGE

    def chase(self, dx, dy, d, wall_rects):
        if self.behavior == "chaser":
            self.move(dx, dy, wall_rects)
        elif self.behavior == "cautious":
            if d > DETECTION_RADIUS * 0.5:
                self.move(dx, dy, wall_rects)
            else:
                self.move(-dy, dx, wall_rects)
        elif self.behavior == "patrol":
            if random.random() < 0.015:
                self.move(-dx, -dy, wall_rects)
            else:
                self.move(dx, dy, wall_rects)

    def wander(self, wall_rects):
        self.wander_timer -= 1
        if self.wander_timer <= 0:
            self.wander_dir   = self.random_dir()
            self.wander_timer = WANDER_CHANGE + random.randint(-20, 20)
        self.move(self.wander_dir[0], self.wander_dir[1], wall_rects)

    def patrol(self, wall_rects):
        if not self.patrol_points:
            self.wander(wall_rects)
            return
        target = self.patrol_points[self.patrol_index]
        dx = target[0] - self.rect.centerx
        dy = target[1] - self.rect.centery
        if math.hypot(dx, dy) < 8:
            self.patrol_index = (self.patrol_index + 1) % len(self.patrol_points)
        else:
            self.move(dx, dy, wall_rects)

    def draw(self, screen, assets):
        if self.state == "alert":
            # Halo rouge pulsant pour signaler la mise en alerte
            pulse = max(0, self.alert_timer)
            halo = pygame.Surface((60, 60), pygame.SRCALPHA)
            alpha = int(180 * pulse / 40)
            pygame.draw.circle(halo, (255, 60, 60, alpha), (30, 30), 28)
            screen.blit(halo, (self.rect.centerx - 30, self.rect.centery - 30))

        screen.blit(assets["enemy"], self.rect)

        # Petite barre de vie au-dessus
        max_hp = getattr(self, "max_hp", self.hp + 2)
        bar_w = self.rect.width
        ratio = max(0, self.hp / max_hp)
        pygame.draw.rect(screen, (80,  0,  0), (self.rect.x, self.rect.y - 6, bar_w, 4))
        pygame.draw.rect(screen, (220, 50, 50), (self.rect.x, self.rect.y - 6, int(bar_w * ratio), 4))