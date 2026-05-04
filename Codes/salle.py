import random
import pygame
from entitees import Enemy, Boss
from config_carte import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, COLS, ROWS, ROOM_TEMPLATES, make_empty
from objets_salle import Item, Chest, ExitPortal


class Room:
    def __init__(self, x, y, level=1, is_start=False, is_exit=False):
        self.x = x
        self.y = y
        self.level = level
        self.is_start = is_start
        self.is_exit = is_exit
        self.is_boss_room = is_exit and level in (5, 10)
        self.active_doors = set()
        self.visited = False
        self.cleared = is_start
        self.items = []
        self.reward_spawned = False
        self.chest = Chest(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80) if is_start else None
        self.reward_chests = []
        self.portal = ExitPortal() if is_exit else None
        self.decorations = []
        self.grid = make_empty() if is_start else random.choice(ROOM_TEMPLATES)()
        self.door_directions = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
        self._wall_cache = None
        self._apply_borders()
        self._create_decorations()
        self.enemies = []
        self._spawn_enemies()

    def _apply_borders(self):
        for col in range(COLS):
            self.grid[0][col] = 1
            self.grid[ROWS - 1][col] = 1
        for row in range(ROWS):
            self.grid[row][0] = 1
            self.grid[row][COLS - 1] = 1

    def _create_decorations(self):
        free_tiles = self._free_tiles()
        random.shuffle(free_tiles)
        for x, y in free_tiles[:random.randint(8, 16)]:
            self.decorations.append((x, y, random.choice(["stone", "crack", "rune", "dust"])))

    def _free_tiles(self):
        return [(c * TILE_SIZE + TILE_SIZE // 2, r * TILE_SIZE + TILE_SIZE // 2)
                for r in range(2, ROWS - 2) for c in range(2, COLS - 2)
                if self.grid[r][c] == 0]

    def _spawn_enemies(self):
        if self.is_boss_room:
            boss_kind = "warden" if self.level == 5 else "sorcerer"
            self.enemies.append(Boss(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, boss_kind, self.level))
            return
        if self.is_start:
            return
        free_tiles = self._free_tiles()
        for _ in range(random.randint(1 + self.level // 2, 2 + self.level)):
            if not free_tiles:
                return
            ex, ey = random.choice(free_tiles)
            enemy = Enemy(ex, ey)
            enemy.level = self.level
            enemy.hp = 2 + self.level
            enemy.max_hp = enemy.hp
            enemy.speed = min(1.8 + self.level * 0.28, 4.0)
            if enemy.behavior == "patrol" and len(free_tiles) >= 2:
                enemy.patrol_points = list(random.sample(free_tiles, 2))
                enemy.state = "patrol"
            self.enemies.append(enemy)

    def _open_door(self, direction):
        mid_col, mid_row = COLS // 2, ROWS // 2
        if direction == "up":
            for c in range(mid_col - 1, mid_col + 2): self.grid[0][c] = 2
        elif direction == "down":
            for c in range(mid_col - 1, mid_col + 2): self.grid[ROWS - 1][c] = 2
        elif direction == "left":
            for r in range(mid_row - 1, mid_row + 2): self.grid[r][0] = 2
        elif direction == "right":
            for r in range(mid_row - 1, mid_row + 2): self.grid[r][COLS - 1] = 2

    def add_door(self, direction):
        self.active_doors.add(direction)
        self._open_door(direction)
        self._wall_cache = None

    def get_wall_rects(self):
        if self._wall_cache is None:
            self._wall_cache = [pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                                for r in range(ROWS) for c in range(COLS) if self.grid[r][c] == 1]
        return self._wall_cache

    def get_door_rects(self):
        mid_col, mid_row = COLS // 2, ROWS // 2
        doors = {
            "up": pygame.Rect((mid_col - 1) * TILE_SIZE, 0, TILE_SIZE * 3, TILE_SIZE),
            "down": pygame.Rect((mid_col - 1) * TILE_SIZE, (ROWS - 1) * TILE_SIZE, TILE_SIZE * 3, TILE_SIZE),
            "left": pygame.Rect(0, (mid_row - 1) * TILE_SIZE, TILE_SIZE, TILE_SIZE * 3),
            "right": pygame.Rect((COLS - 1) * TILE_SIZE, (mid_row - 1) * TILE_SIZE, TILE_SIZE, TILE_SIZE * 3),
        }
        return {direction: rect for direction, rect in doors.items() if direction in self.active_doors}

    def fix_enemy_position(self, enemy):
        wall_rects = self.get_wall_rects() + list(self.get_door_rects().values())
        if not any(enemy.rect.colliderect(wall) for wall in wall_rects):
            return
        free_tiles = self._free_tiles()
        if free_tiles:
            enemy.rect.center = random.choice(free_tiles)

    def update(self, player):
        if self.portal:
            self.portal.update()
            if self.cleared and not self.portal.active:
                self.portal.active = True
        if self.cleared:
            return
        wall_rects = self.get_wall_rects() + list(self.get_door_rects().values())
        for enemy in self.enemies:
            if enemy.hp > 0:
                enemy.update(player, wall_rects)
                self.fix_enemy_position(enemy)
        if all(enemy.hp <= 0 for enemy in self.enemies):
            self._clear_room()

    def _clear_room(self):
        self.cleared = True
        if self.reward_spawned:
            return
        self.reward_spawned = True
        if len(self.enemies) == 0 or random.random() < 0.45:
            self.reward_chests.append(Chest(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, "reward"))
        else:
            self.items.append(Item(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                                   random.choice(["heart", "heart", "heart", "speed"])))

    def draw(self, screen, assets):
        self._draw_tiles(screen, assets)
        self._draw_decorations(screen)
        if self.chest: self.chest.draw(screen, assets)
        for chest in self.reward_chests: chest.draw(screen, assets)
        for item in self.items: item.draw(screen, assets)
        for enemy in self.enemies:
            if enemy.hp > 0: enemy.draw(screen, assets)
        if self.portal: self.portal.draw(screen)
        self._draw_room_label(screen)

    def _draw_room_label(self, screen):
        if self.is_boss_room and not self.cleared:
            text, color, size = "BOSS - survive et trouve son rythme", (255, 90, 90), 24
        elif self.is_exit and not self.cleared:
            text, color, size = "Tuez tous les ennemis pour ouvrir le portail", (255, 220, 80), 22
        else:
            return
        font = pygame.font.Font(None, size)
        label = font.render(text, True, color)
        screen.blit(label, (SCREEN_WIDTH // 2 - label.get_width() // 2, 8))

    def _draw_tiles(self, screen, assets):
        anim = pygame.time.get_ticks() // 220
        for r in range(ROWS):
            for c in range(COLS):
                tile = self.grid[r][c]
                x, y = c * TILE_SIZE, r * TILE_SIZE
                if tile == 1:
                    screen.blit(assets["wall"], (x, y))
                    if (r + c + anim) % 11 == 0:
                        pygame.draw.rect(screen, (80, 70, 90), (x + 4, y + 4, 8, 8), 1)
                elif tile == 2:
                    self._draw_door(screen, assets, x, y)
                else:
                    floor_key = f"floor_lv{self.level}" if f"floor_lv{self.level}" in assets else "floor"
                    screen.blit(assets[floor_key], (x, y))

    def _draw_door(self, screen, assets, x, y):
        screen.blit(assets["door"], (x, y))
        if self.cleared:
            pygame.draw.rect(screen, (120, 255, 150), (x + 3, y + 3, TILE_SIZE - 6, TILE_SIZE - 6), 2)
        else:
            pygame.draw.line(screen, (180, 40, 40), (x + 8, y + 8), (x + TILE_SIZE - 8, y + TILE_SIZE - 8), 3)
            pygame.draw.line(screen, (180, 40, 40), (x + TILE_SIZE - 8, y + 8), (x + 8, y + TILE_SIZE - 8), 3)

    def _draw_decorations(self, screen):
        tick = pygame.time.get_ticks()
        for x, y, deco in self.decorations:
            if deco == "stone":
                pygame.draw.circle(screen, (70, 70, 75), (x - 8, y + 5), 4)
                pygame.draw.circle(screen, (55, 55, 60), (x + 7, y - 4), 3)
            elif deco == "crack":
                pygame.draw.line(screen, (45, 45, 50), (x - 12, y - 4), (x - 2, y + 2), 2)
                pygame.draw.line(screen, (45, 45, 50), (x - 2, y + 2), (x + 10, y - 8), 2)
            elif deco == "rune":
                color = (120, 70 + (tick // 120) % 60, 180)
                pygame.draw.circle(screen, color, (x, y), 7, 1)
                pygame.draw.line(screen, color, (x - 5, y), (x + 5, y), 1)
            else:
                pygame.draw.circle(screen, (85, 75, 55), (x, y), 2)

