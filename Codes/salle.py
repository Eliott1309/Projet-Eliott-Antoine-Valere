import random
import pygame
from entitees import Enemy, Boss
from config_carte import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, COLS, ROWS, ROOM_TEMPLATES, make_empty
from objets_salle import Item, Chest, ExitPortal


class Room:
    #prepare une salle avec sa position, son niveau, ses murs, objets et ennemis
    def __init__(self, x, y, level=1, is_start=False, is_exit=False):
        self.x = x
        self.y = y
        self.level = level
        self.is_start = is_start
        self.is_exit = is_exit
        self.is_boss_room = is_exit and level in (3,6,9)
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
        self._mettre_bords()
        self._ajouter_decos()
        self.enemies = []
        self._ajouter_ennemis()

    #ca prend juste la salle, ca met des murs sur les bords et ca change la grille directement
    def _mettre_bords(self):
        for col in range(COLS):
            self.grid[0][col] = 1
            self.grid[ROWS - 1][col] = 1
        for row in range(ROWS):
            self.grid[row][0] = 1
            self.grid[row][COLS - 1] = 1

    #ca prend la salle, ca cherche des cases libres et ca pose des petites decos au hasard
    def _ajouter_decos(self):
        free_tiles = self._cases_libres()
        random.shuffle(free_tiles)
        for x, y in free_tiles[:random.randint(8, 16)]:
            self.decorations.append((x, y, random.choice(["stone", "crack", "rune", "dust"])))

    #ca regarde la grille et ca renvoie les positions ou on peut poser un truc sans mur
    def _cases_libres(self):
        return [(c * TILE_SIZE + TILE_SIZE // 2, r * TILE_SIZE + TILE_SIZE // 2)
                for r in range(2, ROWS - 2) for c in range(2, COLS - 2)
                if self.grid[r][c] == 0]

    #ca prend la salle et son niveau, ca ajoute les ennemis ou le boss dans la liste enemies
    def _ajouter_ennemis(self):
        if self.is_boss_room:
            if self.level == 3:
                boss_kind = "warden"
            elif self.level == 6:
                boss_kind = "sorcerer"
            else:
                 boss_kind = "berserker"
            self.enemies.append(Boss(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, boss_kind, self.level))
            return
        if self.is_start:
            return
        free_tiles = self._cases_libres()
        for _ in range(random.randint(1 + self.level // 2, 2 + self.level)):
            if not free_tiles:
                return
            wall_rects = self.get_wall_rects()
            valid_tiles = [(ex, ey) for ex, ey in free_tiles
                if not any(pygame.Rect(ex-20, ey-20, 40, 40).colliderect(w) for w in wall_rects)]
            if not valid_tiles:
                return
            ex, ey = random.choice(valid_tiles)
            enemy = Enemy(ex, ey)
            enemy.level = self.level
            enemy.hp = 2 + self.level
            enemy.max_hp = enemy.hp
            enemy.speed = min(1.8 + self.level * 0.28, 4.0)
            if enemy.behavior == "patrol" and len(free_tiles) >= 2:
                enemy.patrol_points = list(random.sample(free_tiles, 2))
                enemy.state = "patrol"
            self.enemies.append(enemy)

    #ca prend une direction, ca remplace les murs par une porte dans la grille
    def _ouvrir_porte(self, direction):
        mid_col, mid_row = COLS // 2, ROWS // 2
        if direction == "up":
            for c in range(mid_col - 1, mid_col + 2): self.grid[0][c] = 2
        elif direction == "down":
            for c in range(mid_col - 1, mid_col + 2): self.grid[ROWS - 1][c] = 2
        elif direction == "left":
            for r in range(mid_row - 1, mid_row + 2): self.grid[r][0] = 2
        elif direction == "right":
            for r in range(mid_row - 1, mid_row + 2): self.grid[r][COLS - 1] = 2

    #ajoute une porte dans une direction et remet le cache des murs a zero
    def add_door(self, direction):
        self.active_doors.add(direction)
        self._ouvrir_porte(direction)
        self._wall_cache = None

    #renvoie les rectangles des murs, avec un cache pour eviter de tout refaire
    def get_wall_rects(self):
        if self._wall_cache is None:
            self._wall_cache = [pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                                for r in range(ROWS) for c in range(COLS) if self.grid[r][c] == 1]
        return self._wall_cache

    #renvoie les rectangles des portes actives pour les collisions et passages
    def get_door_rects(self):
        mid_col, mid_row = COLS // 2, ROWS // 2
        doors = {
            "up": pygame.Rect((mid_col - 1) * TILE_SIZE, 0, TILE_SIZE * 3, TILE_SIZE),
            "down": pygame.Rect((mid_col - 1) * TILE_SIZE, (ROWS - 1) * TILE_SIZE, TILE_SIZE * 3, TILE_SIZE),
            "left": pygame.Rect(0, (mid_row - 1) * TILE_SIZE, TILE_SIZE, TILE_SIZE * 3),
            "right": pygame.Rect((COLS - 1) * TILE_SIZE, (mid_row - 1) * TILE_SIZE, TILE_SIZE, TILE_SIZE * 3),
        }
        return {direction: rect for direction, rect in doors.items() if direction in self.active_doors}

    #si un ennemi spawn dans un mur, on le decale un peu pour le sortir
    def fix_enemy_position(self, enemy):
        wall_rects = self.get_wall_rects()
        for wall in wall_rects:
             if enemy.rect.colliderect(wall):
                dx = enemy.rect.centerx - wall.centerx
                dy = enemy.rect.centery - wall.centery
                if abs(dx) >= abs(dy):
                    enemy.rect.x += 3 if dx >= 0 else -3
                else:
                    enemy.rect.y += 3 if dy >= 0 else -3

    #met a jour portail et ennemis, puis verifie si la salle est terminee
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
            self._finir_salle()

    #ca prend la salle, ca la marque comme finie et ca met une recompense si besoin
    def _finir_salle(self):
        self.cleared = True
        if self.reward_spawned:
            return
        self.reward_spawned = True
        if len(self.enemies) == 0 or random.random() < 0.45:
            self.reward_chests.append(Chest(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, "reward"))
        else:
            self.items.append(Item(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, random.choice(["heart", "heart", "heart", "speed"])))

    #affiche la salle complete avec le sol, les objets, les ennemis et le portail
    def draw(self, screen, assets):
        self._dessiner_cases(screen, assets)
        self._dessiner_decos(screen)
        if self.chest: self.chest.draw(screen, assets)
        for chest in self.reward_chests: chest.draw(screen, assets)
        for item in self.items: item.draw(screen, assets)
        for enemy in self.enemies:
            if enemy.hp > 0: enemy.draw(screen, assets)
        if self.portal: self.portal.draw(screen)
        self._dessiner_texte_salle(screen)

    #ca prend l'ecran et ca affiche le texte special d'une salle boss ou sortie
    def _dessiner_texte_salle(self, screen):
        if self.is_boss_room and not self.cleared:
            text, color, size = "BOSS - survive et trouve son rythme", (255, 90, 90), 24
        elif self.is_exit and not self.cleared:
            text, color, size = "Tuez tous les ennemis pour ouvrir le portail", (255, 220, 80), 22
        else:
            return
        font = pygame.font.Font(None, size)
        label = font.render(text, True, color)
        screen.blit(label, (SCREEN_WIDTH // 2 - label.get_width() // 2, 8))

    #ca prend l'ecran et les images, ca dessine tout le sol, les murs et les portes
    def _dessiner_cases(self, screen, assets):
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
                    self._dessiner_porte(screen, assets, x, y)
                else:
                    floor_key = f"floor_lv{self.level}" if f"floor_lv{self.level}" in assets else "floor"
                    screen.blit(assets[floor_key], (x, y))

    #ca prend la position d'une porte et ca affiche son image, il n'y a rien a renvoyer
    def _dessiner_porte(self, screen, assets, x, y):
        screen.blit(assets["door"], (x, y))
        
    #ca prend l'ecran, ca dessine les cailloux/runes de deco et ca modifie pas la salle
    def _dessiner_decos(self, screen):
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

