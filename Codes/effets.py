import math
import random
import pygame


class ScreenShake:
    def __init__(self):
        self.timer = 0
        self.intensity = 0

    def trigger(self, intensity=6, duration=10):
        if intensity >= self.intensity:
            self.timer = duration
            self.intensity = intensity

    def get_offset(self):
        if self.timer > 0:
            self.timer -= 1
            strength = self.intensity * (self.timer / max(1, self.timer + 1))
            return (random.randint(-int(strength), int(strength)),
                    random.randint(-int(strength), int(strength)))
        self.intensity = 0
        return (0, 0)


class Particle:
    def __init__(self, x, y, color, dx=0, dy=0, life=30, size=4, gravity=0.12, fade=True):
        self.x, self.y = float(x), float(y)
        self.dx = dx + random.uniform(-1.2, 1.2)
        self.dy = dy + random.uniform(-1.2, 1.2)
        self.color = color
        self.life = life
        self.max_life = life
        self.size = size
        self.gravity = gravity
        self.fade = fade

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.dy += self.gravity
        self.dx *= 0.95
        self.life -= 1

    def draw(self, screen):
        if self.life <= 0:
            return
        ratio = self.life / self.max_life
        alpha = int(255 * ratio) if self.fade else 255
        current_size = max(1, int(self.size * ratio))
        surface = pygame.Surface((current_size * 2 + 2, current_size * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(surface, (*self.color, alpha), (current_size + 1, current_size + 1), current_size)
        screen.blit(surface, (int(self.x) - current_size - 1, int(self.y) - current_size - 1))


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit_blood(self, x, y, count=8):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1.5, 4.5)
            self.particles.append(Particle(
                x, y,
                color=(random.randint(160, 220), random.randint(0, 30), random.randint(0, 30)),
                dx=math.cos(angle) * speed,
                dy=math.sin(angle) * speed,
                life=random.randint(18, 35),
                size=random.randint(2, 5),
                gravity=0.18,
            ))

    def emit_dust(self, x, y, count=3):
        for _ in range(count):
            self.particles.append(Particle(
                x + random.randint(-10, 10), y + random.randint(-5, 5),
                color=(random.randint(130, 170), random.randint(110, 140), random.randint(80, 110)),
                dx=random.uniform(-0.6, 0.6),
                dy=random.uniform(-1.5, -0.2),
                life=random.randint(12, 22),
                size=random.randint(2, 4),
                gravity=0.04,
            ))

    def emit_magic(self, x, y, count=12, color=(160, 90, 255)):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1.0, 5.0)
            self.particles.append(Particle(
                x, y, color=color,
                dx=math.cos(angle) * speed,
                dy=math.sin(angle) * speed,
                life=random.randint(20, 40),
                size=random.randint(3, 7),
                gravity=-0.05,
            ))

    def emit_sparks(self, x, y, count=6, color=(255, 220, 80)):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2.0, 6.0)
            self.particles.append(Particle(
                x, y, color=color,
                dx=math.cos(angle) * speed,
                dy=math.sin(angle) * speed,
                life=random.randint(10, 20),
                size=random.randint(2, 4),
                gravity=0.25,
            ))

    def emit_explosion(self, x, y):
        self.emit_magic(x, y, count=20, color=(160, 90, 255))
        self.emit_sparks(x, y, count=12, color=(255, 160, 60))
        self.emit_blood(x, y, count=6)

    def update(self):
        self.particles = [p for p in self.particles if p.life > 0]
        for particle in self.particles:
            particle.update()

    def draw(self, screen):
        for particle in self.particles:
            particle.draw(screen)


class DynamicLighting:
    def __init__(self, width, height):
        self._surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self._light_cache = {}

    def _get_light_texture(self, radius):
        if radius in self._light_cache:
            return self._light_cache[radius]
        texture = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        for r in range(radius, 0, -1):
            alpha = int(200 * (((radius - r) / radius) ** 2.2))
            pygame.draw.circle(texture, (0, 0, 0, alpha), (radius, radius), r)
        self._light_cache[radius] = texture
        return texture

    def draw(self, screen, player, extra_lights=None):
        self._surface.fill((0, 0, 0, 165))
        px, py = player.rect.center
        self._surface.blit(self._get_light_texture(400), (px - 400, py - 400), special_flags=pygame.BLEND_RGBA_SUB)
        if extra_lights:
            for lx, ly, radius, _color in extra_lights:
                self._surface.blit(self._get_light_texture(radius), (lx - radius, ly - radius), special_flags=pygame.BLEND_RGBA_SUB)
        screen.blit(self._surface, (0, 0))


class FadeTransition:
    def __init__(self, width, height):
        self.surface = pygame.Surface((width, height))
        self.surface.fill((0, 0, 0))
        self.alpha = 0
        self.state = "idle"
        self.speed = 18
        self.callback = None

    def start(self, callback=None):
        if self.state == "idle":
            self.state = "fade_out"
            self.alpha = 0
            self.callback = callback

    @property
    def is_active(self):
        return self.state != "idle"

    def update(self):
        if self.state == "fade_out":
            self.alpha = min(255, self.alpha + self.speed)
            if self.alpha >= 255:
                if self.callback:
                    self.callback()
                    self.callback = None
                self.state = "fade_in"
        elif self.state == "fade_in":
            self.alpha = max(0, self.alpha - self.speed)
            if self.alpha <= 0:
                self.state = "idle"

    def draw(self, screen):
        if self.state != "idle":
            self.surface.set_alpha(self.alpha)
            screen.blit(self.surface, (0, 0))

