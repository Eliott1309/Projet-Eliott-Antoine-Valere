import random
import pygame
from entitees import Enemy

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 40
COLS = SCREEN_WIDTH // TILE_SIZE
ROWS = SCREEN_HEIGHT // TILE_SIZE
MINI_ROOM_SIZE = 12
MINI_ROOM_GAP  = 4

def make_empty():
    return [[0]*COLS for _ in range(ROWS)]

def make_piliers():
    g = make_empty()
    for px, py in [(5,4),(5,10),(14,4),(14,10)]:
        for dy in range(2):
            for dx in range(2):
                g[py+dy][px+dx] = 1
    return g

def make_croix():
    g = [[1]*COLS for _ in range(ROWS)]
    for row in range(5, 10):
        for col in range(COLS):
            g[row][col] = 0
    for row in range(ROWS):
        for col in range(8, 12):
            g[row][col] = 0
    return g

def make_chambres():
    g = make_empty()
    for row in range(ROWS):
        g[row][10] = 1
    for row in range(6, 9):
        g[row][10] = 0
    return g

def make_labyrinthe():
    """Quelques murs intérieurs disposés aléatoirement."""
    g = make_empty()
    for _ in range(12):
        col = random.randint(2, COLS - 3)
        row = random.randint(2, ROWS - 3)
        length = random.randint(2, 4)
        horizontal = random.choice([True, False])
        for i in range(length):
            r = row + (0 if horizontal else i)
            c = col + (i if horizontal else 0)
            if 1 < r < ROWS - 1 and 1 < c < COLS - 1:
                g[r][c] = 1
    return g

ROOM_TEMPLATES = [make_empty, make_piliers, make_croix, make_chambres, make_labyrinthe]


class Item:
    def __init__(self, x, y, item_type):
        self.rect = pygame.Rect(x - 14, y - 14, 28, 28)
        self.type = item_type

    def draw(self, screen, assets):
        key = self.type if self.type in assets else None
        if key:
            screen.blit(assets[key], self.rect)


class Chest:
    def __init__(self, x, y, chest_type="start"):
        self.rect = pygame.Rect(x - 18, y - 18, 36, 36)
        self.opened = False
        self.open_timer = 0
        self.chest_type = chest_type

    def draw(self, screen, assets):
        if not self.opened:
            screen.blit(assets["chest"], self.rect)

    def open(self):
        self.opened = True
        if self.chest_type == "start":
            return random.choice(["sword", "crossbow"])
        rewards = ["damage_boost","speed_boost","range_boost","sword","crossbow","bow","magic_wand"]
        return random.choice(rewards)


class ExitPortal:
    def __init__(self):
        cx = SCREEN_WIDTH  // 2
        cy = SCREEN_HEIGHT // 2
        self.rect    = pygame.Rect(cx - 24, cy - 24, 48, 48)
        self.active  = False          # devient True quand la salle est cleared
        self.anim    = 0              # compteur d'animation

    def update(self):
        if self.active:
            self.anim = (self.anim + 1) % 60

    def draw(self, screen):
        if not self.active:
            return
        # Halo pulsant violet
        pulse = abs(30 - self.anim) / 30          # 0 → 1 → 0
        radius = int(28 + 10 * pulse)
        halo = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(halo, (160, 80, 255, 80), (radius, radius), radius)
        screen.blit(halo, (self.rect.centerx - radius, self.rect.centery - radius))

        # Cercle intérieur
        inner_color = (200, 130, 255)
        pygame.draw.circle(screen, inner_color, self.rect.center, 20)
        pygame.draw.circle(screen, (255, 255, 255), self.rect.center, 20, 2)

        # Texte indicatif
        try:
            font = pygame.font.Font(None, 20)
            label = font.render("SORTIE", True, (255, 255, 255))
            screen.blit(label, (self.rect.centerx - label.get_width()//2, self.rect.bottom + 6))
        except Exception:
            pass


class Room:
    def __init__(self, x, y, level=1, is_start=False, is_exit=False):
        self.x = x
        self.y = y
        self.level = level
        self.is_start = is_start
        self.is_exit  = is_exit
        self.active_doors = set()
        self.visited  = False
        self.cleared  = is_start        # la salle de départ est déjà cleared
        self.items    = []
        self.reward_spawned = False
        self.chest    = None
        self.reward_chests  = []
        self.portal   = None

        # Coffre de départ dans la salle initiale
        if is_start:
            self.chest = Chest(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80)

        # Portail dans la salle de sortie
        if is_exit:
            self.portal = ExitPortal()

        # Grille
        if is_start:
            self.grid = make_empty()
        else:
            self.grid = random.choice(ROOM_TEMPLATES)()

        self._apply_borders()

        # Ennemis (absents dans la salle de départ)
        self.enemies = []
        if not is_start:
            free_tiles = [
                (c * TILE_SIZE + TILE_SIZE//2, r * TILE_SIZE + TILE_SIZE//2)
                for r in range(2, ROWS-2) for c in range(2, COLS-2)
                if self.grid[r][c] == 0
            ]
            # Nombre et difficulté évoluent avec le niveau
            n_enemies = random.randint(1 + level, 3 + level)
            for _ in range(n_enemies):
                if free_tiles:
                    ex, ey = random.choice(free_tiles)
                    enemy = Enemy(ex, ey)
                    enemy.hp     = 2 + level
                    enemy.max_hp = enemy.hp
                    enemy.speed  = min(2 + level * 0.4, 4.5)
                    # Donner 2 points de patrouille aux ennemis de type patrol
                    if enemy.behavior == "patrol" and len(free_tiles) >= 2:
                        pts = random.sample(free_tiles, 2)
                        enemy.patrol_points = list(pts)
                        enemy.state = "patrol"
                    self.enemies.append(enemy)

        self.door_directions = {
            "up":    (0, -1),
            "down":  (0,  1),
            "left":  (-1, 0),
            "right": ( 1, 0),
        }

    # ── Grille ──────────────────────────────

    def _apply_borders(self):
        for col in range(COLS):
            self.grid[0][col] = 1
            self.grid[ROWS-1][col] = 1
        for row in range(ROWS):
            self.grid[row][0] = 1
            self.grid[row][COLS-1] = 1

    def _open_door(self, d):
        mc, mr = COLS//2, ROWS//2
        if d == "up":    [self.grid[0].__setitem__(c, 2) for c in range(mc-1, mc+2)]
        elif d == "down": [self.grid[ROWS-1].__setitem__(c, 2) for c in range(mc-1, mc+2)]
        elif d == "left": [self.grid[r].__setitem__(0, 2) for r in range(mr-1, mr+2)]
        elif d == "right":[self.grid[r].__setitem__(COLS-1, 2) for r in range(mr-1, mr+2)]

    def add_door(self, direction):
        self.active_doors.add(direction)
        self._open_door(direction)
        self._wall_cache = None   # invalide le cache quand une porte s'ouvre

    # ── Collisions ──────────────────────────

    def get_wall_rects(self):
        if not hasattr(self, "_wall_cache") or self._wall_cache is None:
            self._wall_cache = [
                pygame.Rect(c*TILE_SIZE, r*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                for r in range(ROWS) for c in range(COLS) if self.grid[r][c] == 1
            ]
        return self._wall_cache

    def get_door_rects(self):
        mid_col = COLS // 2
        mid_row = ROWS // 2
        all_doors = {
            "up":    pygame.Rect((mid_col-1)*TILE_SIZE, 0,              TILE_SIZE*3, TILE_SIZE),
            "down":  pygame.Rect((mid_col-1)*TILE_SIZE, (ROWS-1)*TILE_SIZE, TILE_SIZE*3, TILE_SIZE),
            "left":  pygame.Rect(0,              (mid_row-1)*TILE_SIZE, TILE_SIZE, TILE_SIZE*3),
            "right": pygame.Rect((COLS-1)*TILE_SIZE, (mid_row-1)*TILE_SIZE, TILE_SIZE, TILE_SIZE*3),
        }
        return {d: r for d, r in all_doors.items() if d in self.active_doors}

    # ── Update ──────────────────────────────

    def update(self, player):
        if self.portal:
            self.portal.update()
            if self.cleared and not self.portal.active:
                self.portal.active = True

        if self.cleared:
            return

        wall_rects = self.get_wall_rects()
        for enemy in self.enemies:
            if enemy.hp > 0:
                enemy.update(player, wall_rects)

        if all(e.hp <= 0 for e in self.enemies):
            self.cleared = True
            if not self.reward_spawned:
                self.reward_spawned = True
                if random.random() < 0.55:
                    self.reward_chests.append(Chest(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, "reward"))
                else:
                    self.items.append(Item(SCREEN_WIDTH//2, SCREEN_HEIGHT//2,
                                           random.choice(["heart", "speed"])))

    # ── Draw ────────────────────────────────

    def draw(self, screen, assets):
        self._draw_tiles(screen, assets)

        if self.chest:
            self.chest.draw(screen, assets)
        for rc in self.reward_chests:
            rc.draw(screen, assets)
        for item in self.items:
            item.draw(screen, assets)
        for enemy in self.enemies:
            if enemy.hp > 0:
                enemy.draw(screen, assets)
        if self.portal:
            self.portal.draw(screen)

        # Indicateur visuel sur la salle de sortie (avant cleared)
        if self.is_exit and not self.cleared:
            font = pygame.font.Font(None, 22)
            label = font.render("Tuez tous les ennemis pour ouvrir le portail", True, (255, 220, 80))
            screen.blit(label, (SCREEN_WIDTH//2 - label.get_width()//2, 8))

    def _draw_tiles(self, screen, assets):
        for r in range(ROWS):
            for c in range(COLS):
                tile = self.grid[r][c]
                x, y = c*TILE_SIZE, r*TILE_SIZE
                if tile == 1:
                    screen.blit(assets["wall"],  (x, y))
                elif tile == 2:
                    screen.blit(assets["door"],  (x, y))
                else:
                    screen.blit(assets["floor"], (x, y))


class Map:
    def __init__(self, level=1, num_rooms=None):
        self.level       = level
        self.rooms       = {}
        self.current_pos = (0, 0)

        # Nombre de salles qui augmente avec les niveaux
        if num_rooms is None:
            num_rooms = 8 + level * 2          # niveau 1 → 10, niveau 2 → 12, etc.
        num_rooms = max(num_rooms, 6)

        self._generate(num_rooms)
        self.current_room = self.rooms[self.current_pos]
        self.current_room.visited = True

        # Signal : le joueur entre dans le portail → changer de niveau
        self.next_level_triggered = False

    # ── Génération ──────────────────────────

    def _generate(self, num_rooms):
        dirs      = [(0,-1),(0,1),(-1,0),(1,0)]
        dir_names = {(0,-1):"up",(0,1):"down",(-1,0):"left",(1,0):"right"}
        visited, stack = {(0,0)}, [(0,0)]

        while len(visited) < num_rooms and stack:
            pos = stack[-1]
            random.shuffle(dirs)
            nxt = next(((pos[0]+dx, pos[1]+dy) for dx,dy in dirs
                        if (pos[0]+dx, pos[1]+dy) not in visited), None)
            if nxt:
                visited.add(nxt); stack.append(nxt)
            else:
                stack.pop()

        while len(visited) < num_rooms:            # compléter si bloqué
            base = random.choice(list(visited))
            random.shuffle(dirs)
            for dx, dy in dirs:
                npos = (base[0]+dx, base[1]+dy)
                if npos not in visited:
                    visited.add(npos); break

        exit_pos = max(visited, key=lambda p: abs(p[0]) + abs(p[1]))
        for coord in visited:
            self.rooms[coord] = Room(coord[0], coord[1], level=self.level,
                                     is_start=(coord==(0,0)), is_exit=(coord==exit_pos))
        for coord in visited:
            for dx, dy in dirs:
                nb = (coord[0]+dx, coord[1]+dy)
                if nb in self.rooms:
                    self.rooms[coord].add_door(dir_names[(dx,dy)])

    # ── Changement de salle ─────────────────

    def change_room(self, dx, dy, player=None):
        if not self.current_room.cleared:
            return False
        new_pos = (self.current_pos[0]+dx, self.current_pos[1]+dy)
        if new_pos not in self.rooms:
            return False
        self.current_pos  = new_pos
        self.current_room = self.rooms[new_pos]
        self.current_room.visited = True
        if player:
            # Repositionne le joueur loin de la porte qu'il vient de franchir
            # pour éviter qu'il la re-traverse immédiatement dans la nouvelle salle
            margin = TILE_SIZE * 2 + 5
            if dx ==  1: player.rect.left   = margin
            if dx == -1: player.rect.right  = COLS * TILE_SIZE - margin
            if dy ==  1: player.rect.top    = margin
            if dy == -1: player.rect.bottom = ROWS * TILE_SIZE - margin
            player.transition_lock = 20   # frames pendant lesquelles les portes sont ignorées
        return True

    # ── Update / Draw ───────────────────────

    def update(self, player):
        self.current_room.update(player)

        # Détecter si le joueur entre dans le portail
        portal = self.current_room.portal
        if portal and portal.active and portal.rect.colliderect(player.rect):
            self.next_level_triggered = True

    def draw(self, screen, assets):
        self.current_room.draw(screen, assets)
        self._draw_minimap(screen)

    # ── Minimap ─────────────────────────────

    def _draw_minimap(self, screen):
        step = MINI_ROOM_SIZE + MINI_ROOM_GAP

        # Calculer le centre de la minimap dynamiquement
        all_x = [x for x,y in self.rooms]
        all_y = [y for x,y in self.rooms]
        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)
        map_w = (max_x - min_x + 1) * step
        map_h = (max_y - min_y + 1) * step

        offset_x = SCREEN_WIDTH  - map_w - 10
        offset_y = 10

        for (x, y), room in self.rooms.items():
            if not room.visited:
                # Montrer les salles adjacentes comme inconnues
                adjacent = any((self.current_pos[0]+dx, self.current_pos[1]+dy) == (x,y)
                               for dx,dy in [(0,-1),(0,1),(-1,0),(1,0)])
                if not adjacent:
                    continue
                color = (60, 60, 60)
            elif (x, y) == self.current_pos:
                color = (255, 220, 50)
            elif room.is_exit:
                color = (180, 80, 255)   # violet = sortie
            elif room.cleared:
                color = (80, 180, 80)
            else:
                color = (180, 80, 80)

            draw_x = offset_x + (x - min_x) * step
            draw_y = offset_y + (y - min_y) * step
            pygame.draw.rect(screen, color, (draw_x, draw_y, MINI_ROOM_SIZE, MINI_ROOM_SIZE))
            if (x, y) == self.current_pos:
                pygame.draw.rect(screen, (255,255,255),
                                 (draw_x, draw_y, MINI_ROOM_SIZE, MINI_ROOM_SIZE), 1)