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
        self.max_hp = self.hp
        self.kind  = random.choice(["stalker", "shooter", "charger", "bomber"])
        self.touch_damage = 6
        self.attack_timer = random.randint(30, 120)
        self.pending_shot = None
        self.pending_burst = False
        self.flash_timer = 0

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

    #déplace l'ennemi sans le laisser entrer dans les murs
    def move(self, dx, dy, wall_rects):
        if dx == 0 and dy == 0:
            return

        length = math.hypot(dx, dy)
        dx, dy = dx / length, dy / length

        self.rect.x += dx * self.speed
        for wall in wall_rects:
            if self.rect.colliderect(wall):
                if dx > 0:
                    self.rect.right = wall.left
                elif dx < 0:
                    self.rect.left = wall.right
                self.wander_dir = self.random_dir()
                break

        self.rect.y += dy * self.speed
        for wall in wall_rects:
            if self.rect.colliderect(wall):
                if dy > 0:
                    self.rect.bottom = wall.top
                elif dy < 0:
                    self.rect.top = wall.bottom
                self.wander_dir = self.random_dir()
                break



    def update(self, player, wall_rects=None):
        if wall_rects is None:
            wall_rects = []

        self.pending_shot = None
        self.pending_burst = False
        if self.flash_timer > 0:
            self.flash_timer -= 1

        d, dx, dy = self.dist(player)

        self.attack_timer -= 1
        if self.kind == "shooter" and d < DETECTION_RADIUS * 1.4 and self.attack_timer <= 0:
            self.pending_shot = (self.rect.centerx, self.rect.centery, dx, dy, 7, (255, 120, 80), 7)
            self.attack_timer = 95
            self.flash_timer = 12
        elif self.kind == "bomber" and d < 52 and self.attack_timer <= 0:
            self.pending_burst = True
            self.attack_timer = 120
            self.flash_timer = 18

        if self.state not in ("alert", "chase") and d < DETECTION_RADIUS:
            self.state       = "alert"
            self.alert_timer = 40

        if self.state == "chase" and d > DETECTION_RADIUS * 1.8:
            self.state = "wander"

        if self.state == "idle":
            self.ai_idle()
        elif self.state == "alert":
            self.alert_timer -= 1
            if self.alert_timer <= 0:
                self.state = "chase"
        elif self.state == "chase":
            if self.kind == "charger" and self.attack_timer <= 0 and d < DETECTION_RADIUS * 1.2:
                old_speed = self.speed
                self.speed = old_speed * 2.3
                self.move(dx, dy, wall_rects)
                self.speed = old_speed
                self.attack_timer = 85
                self.flash_timer = 14
                return
            self.ai_chase(dx, dy, d, wall_rects)
        elif self.state == "wander":
            self.ai_wander(wall_rects)
        elif self.state == "patrol":
            self.ai_patrol(wall_rects)

    def ai_idle(self):
        if random.random() < 0.005:
            self.state        = "wander"
            self.wander_timer = WANDER_CHANGE

    def ai_chase(self, dx, dy, d, wall_rects):
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

    def ai_wander(self, wall_rects):
        self.wander_timer -= 1
        if self.wander_timer <= 0:
            self.wander_dir   = self.random_dir()
            self.wander_timer = WANDER_CHANGE + random.randint(-20, 20)
        self.move(self.wander_dir[0], self.wander_dir[1], wall_rects)

    def ai_patrol(self, wall_rects):
        if not self.patrol_points:
            self.ai_wander(wall_rects)
            return
        target = self.patrol_points[self.patrol_index]
        dx = target[0] - self.rect.centerx
        dy = target[1] - self.rect.centery
        if math.hypot(dx, dy) < 8:
            self.patrol_index = (self.patrol_index + 1) % len(self.patrol_points)
        else:
            self.move(dx, dy, wall_rects)

    def draw(self, screen, assets):
        if self.kind == "shooter":
            tint = (255, 160, 90)
        elif self.kind == "charger":
            tint = (255, 80, 80)
        elif self.kind == "bomber":
            tint = (180, 90, 255)
        else:
            tint = (255, 255, 255)

        if self.flash_timer > 0:
            halo = pygame.Surface((64, 64), pygame.SRCALPHA)
            pygame.draw.circle(halo, (*tint[:3], 95), (32, 32), 30)
            screen.blit(halo, (self.rect.centerx - 32, self.rect.centery - 32))

        if self.state == "alert":
            # Halo rouge pulsant pour signaler la mise en alerte
            pulse = max(0, self.alert_timer)
            halo = pygame.Surface((60, 60), pygame.SRCALPHA)
            alpha = int(180 * pulse / 40)
            pygame.draw.circle(halo, (255, 60, 60, alpha), (30, 30), 28)
            screen.blit(halo, (self.rect.centerx - 30, self.rect.centery - 30))

        bob = 1 if pygame.time.get_ticks() // 180 % 2 == 0 else -1
        draw_rect = self.rect.move(0, bob)
        level = getattr(self, "level", 1)
        suffix = f"_{level}" if level in (2, 3) else ""
        sprite_key = {
            "stalker": f"enemy_stalker{suffix}",
            "shooter": f"enemy_shooter{suffix}",
            "charger": f"enemy_charger{suffix}",
            "bomber":  f"enemy_bomber{suffix}",
        }.get(self.kind, "enemy")
        if sprite_key not in assets:
            sprite_key = sprite_key.replace(suffix, "")
        screen.blit(assets.get(sprite_key, assets["enemy"]), draw_rect)

        # Petite barre de vie au-dessus
        max_hp = getattr(self, "max_hp", self.hp + 2)
        bar_w = self.rect.width
        ratio = max(0, self.hp / max_hp)
        pygame.draw.rect(screen, (80,  0,  0), (self.rect.x, self.rect.y - 6, bar_w, 4))
        pygame.draw.rect(screen, (220, 50, 50), (self.rect.x, self.rect.y - 6, int(bar_w * ratio), 4))


class Boss(Enemy):
    def __init__(self, x, y, boss_kind, level):
        super().__init__(x, y)
        self.kind = "boss"
        self.boss_kind = boss_kind
        self.level = level
        self.rect = pygame.Rect(x - 38, y - 38, 76, 76)
        self.speed = 1.4 if boss_kind == "warden" else 1.8
        self.touch_damage = 10 if boss_kind == "warden" else 8
        self.hp = 38 + level * 7
        self.max_hp = self.hp
        self.attack_timer = 80
        self.pending_ring = []
        self.pending_shot = None
        self.pending_burst = False

    def update(self, player, wall_rects=None):
        if wall_rects is None:
            wall_rects = []
        self.pending_ring = []
        self.pending_shot = None
        self.pending_burst = False
        self.flash_timer = max(0, self.flash_timer - 1)
        d, dx, dy = self.dist(player)
        self.attack_timer -= 1

        if self.boss_kind == "warden":
            # Boss niveau 5 : alterne charges et ondes circulaires.
            if self.attack_timer <= 0:
                if random.random() < 0.55:
                    for i in range(12):
                        angle = i * (2 * math.pi / 12)
                        self.pending_ring.append((self.rect.centerx, self.rect.centery, math.cos(angle), math.sin(angle), 8, (255, 80, 80), 9))
                    self.attack_timer = 120
                else:
                    old_speed = self.speed
                    self.speed = 5.2
                    self.move(dx, dy, wall_rects)
                    self.speed = old_speed
                    self.attack_timer = 55
                self.flash_timer = 20
            else:
                self.move(dx, dy, wall_rects)

        else:
            # Boss niveau 10 : magie, tirs en etoile et explosions proches.
            if self.attack_timer <= 0:
                for i in range(16):
                    angle = i * (2 * math.pi / 16) + random.uniform(-0.12, 0.12)
                    self.pending_ring.append((self.rect.centerx, self.rect.centery, math.cos(angle), math.sin(angle), 7, (170, 90, 255), 8))
                if d < 115:
                    self.pending_burst = True
                self.attack_timer = 90
                self.flash_timer = 24
            self.move(dx if d > 150 else -dx, dy if d > 150 else -dy, wall_rects)

    def draw(self, screen, assets):
        color = (190, 50, 50) if self.boss_kind == "warden" else (140, 70, 230)
        if self.flash_timer > 0:
            pygame.draw.circle(screen, (255, 220, 120), self.rect.center, 48, 3)
        sprite_key = "boss_warden" if self.boss_kind == "warden" else "boss_sorcerer"
        if sprite_key in assets:
            screen.blit(assets[sprite_key], self.rect)
        else:
            pygame.draw.ellipse(screen, color, self.rect)
            pygame.draw.ellipse(screen, (255,255,255), self.rect, 2)
            eye_y = self.rect.y + 25
            pygame.draw.circle(screen, (20,20,20), (self.rect.x + 26, eye_y), 5)
            pygame.draw.circle(screen, (20,20,20), (self.rect.x + 50, eye_y), 5)
        bar_w = 260
        ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(screen, (45, 0, 0), (SCREEN_CENTER_X() - bar_w//2, 34, bar_w, 12))
        pygame.draw.rect(screen, color, (SCREEN_CENTER_X() - bar_w//2, 34, int(bar_w * ratio), 12))
        pygame.draw.rect(screen, (255,255,255), (SCREEN_CENTER_X() - bar_w//2, 34, bar_w, 12), 1)


def SCREEN_CENTER_X():
    return 400
