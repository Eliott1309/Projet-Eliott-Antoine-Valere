import random
import pygame
from entitees import Enemy

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WALL_THICKNESS = 30
DOOR_SIZE = 60

TILE_SIZE = 40  # taille d'une tuile en pixels
COLS = SCREEN_WIDTH // TILE_SIZE   # 20 colonnes
ROWS = SCREEN_HEIGHT // TILE_SIZE  # 15 lignes

MINI_ROOM_SIZE = 14
MINI_ROOM_GAP = 4
MINI_OFFSET_X = SCREEN_WIDTH - 90
MINI_OFFSET_Y = 30


def make_empty():
    """Salle vide classique."""
    grid = [[0]*COLS for _ in range(ROWS)]
    return grid

def make_piliers():
    """Salle avec 4 piliers."""
    grid = make_empty()
    for px, py in [(5,4),(5,10),(14,4),(14,10)]:
        for dy in range(2):
            for dx in range(2):
                grid[py+dy][px+dx] = 1
    return grid

def make_couloir_h():
    """Couloir horizontal avec murs épais en haut et en bas."""
    grid = [[1]*COLS for _ in range(ROWS)]
    for row in range(5, 10):
        for col in range(COLS):
            grid[row][col] = 0
    return grid

def make_couloir_v():
    """Couloir vertical."""
    grid = [[1]*COLS for _ in range(ROWS)]
    for row in range(ROWS):
        for col in range(8, 12):
            grid[row][col] = 0
    return grid

def make_croix():
    """Salle en forme de croix."""
    grid = [[1]*COLS for _ in range(ROWS)]
    for row in range(5, 10):
        for col in range(COLS):
            grid[row][col] = 0
    for row in range(ROWS):
        for col in range(8, 12):
            grid[row][col] = 0
    return grid

def make_chambres():
    """Deux chambres reliées par un passage."""
    grid = make_empty()
    # mur de séparation vertical au milieu
    for row in range(ROWS):
        grid[row][10] = 1
    # passage au centre
    for row in range(6, 9):
        grid[row][10] = 0
    return grid

ROOM_TEMPLATES = [
    make_empty,
    make_piliers,
    make_chambres,
    # make_couloir_h,   # à corriger plus tard
    # make_couloir_v,   # à corriger plus tard
    make_croix,       
]

class Item:
    def __init__(self, x, y, item_type):
        self.rect = pygame.Rect(x - 14, y - 14, 28, 28)
        self.type = item_type

    def draw(self, screen, assets):
        if self.type == "heart":
            screen.blit(assets["heart"], self.rect)
        elif self.type == "speed":
            screen.blit(assets["speed"], self.rect)

#represente un coffre qui peut donner une arme ou un bonus
class Chest:
    def __init__(self, x, y, chest_type="start"):
        self.rect = pygame.Rect(x - 18, y - 18, 36, 36)
        self.opened = False
        self.open_timer = 0
        self.chest_type = chest_type

    #affiche le coffre tant qu'il n'est pas ouvert
    def draw(self, screen, assets):
        if not self.opened:
            screen.blit(assets["chest"], self.rect)

    #donne une recompense au hasard
    def open(self):
        self.opened = True

        if self.chest_type == "start":
            return random.choice(["sword", "crossbow"])

        rewards = [
            "damage_boost",
            "speed_boost",
            "range_boost",
            "sword",
            "crossbow",
            "bow",
            "magic_wand"
        ]

        return random.choice(rewards)




class Room:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.active_doors = set()
        self.visited = False
        self.cleared = False
        if self.x == 0 and self.y == 0:
            self.cleared = True
        self.items = []
        self.reward_spawned = False
        self.chest = None
        # Coffres de recompense qui peuvent apparaitre apres une salle terminee
        self.reward_chests = []


        if self.x == 0 and self.y == 0:
            self.chest = Chest(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80)




        #la salle de départ est vide
        if self.x == 0 and self.y == 0:
            self.grid = make_empty()
        else:
            self.grid = random.choice(ROOM_TEMPLATES)()

        self._apply_borders()



        free_tiles = [
            (col * TILE_SIZE + TILE_SIZE // 2, row * TILE_SIZE + TILE_SIZE // 2)
            for row in range(1, ROWS - 1)
            for col in range(1, COLS - 1)
            if self.grid[row][col] == 0
        ]
        self.enemies = []

        #la salle de départ contient seulement le coffre
        if not (self.x == 0 and self.y == 0):
            for _ in range(random.randint(1, 3)):
                if free_tiles:
                    x, y = random.choice(free_tiles)
                    self.enemies.append(Enemy(x, y))

        self.door_directions = {
            "up":    (0, -1),
            "down":  (0,  1),
            "left":  (-1, 0),
            "right": ( 1, 0),
        }

    def _apply_borders(self):
        """Force les bords de la grille en murs."""
        for col in range(COLS):
            self.grid[0][col] = 1
            self.grid[ROWS-1][col] = 1
        for row in range(ROWS):
            self.grid[row][0] = 1
            self.grid[row][COLS-1] = 1

    def _open_door(self, direction):
        mid_col = COLS // 2
        mid_row = ROWS // 2
        if direction == "up":
            for col in range(mid_col - 1, mid_col + 2):
                self.grid[0][col] = 2
        elif direction == "down":
            for col in range(mid_col - 1, mid_col + 2):
                self.grid[ROWS-1][col] = 2
        elif direction == "left":
            for row in range(mid_row - 1, mid_row + 2):
                self.grid[row][0] = 2
        elif direction == "right":
            for row in range(mid_row - 1, mid_row + 2):
                self.grid[row][COLS-1] = 2

    def add_door(self, direction):
        self.active_doors.add(direction)
        self._open_door(direction)

    def get_wall_rects(self):
        """Retourne les rects de collision de toutes les tuiles mur."""
        rects = []
        for row in range(ROWS):
            for col in range(COLS):
                if self.grid[row][col] == 1:
                    rects.append(pygame.Rect(col*TILE_SIZE, row*TILE_SIZE, TILE_SIZE, TILE_SIZE))
        return rects

    def get_door_rects(self):
        """Retourne les rects des ouvertures de portes (pour le passage)."""
        mid_col = COLS // 2
        mid_row = ROWS // 2
        all_doors = {
            "up":    pygame.Rect((mid_col-1)*TILE_SIZE, 0, TILE_SIZE*3, TILE_SIZE),
            "down":  pygame.Rect((mid_col-1)*TILE_SIZE, (ROWS-1)*TILE_SIZE, TILE_SIZE*3, TILE_SIZE),
            "left":  pygame.Rect(0, (mid_row-1)*TILE_SIZE, TILE_SIZE, TILE_SIZE*3),
            "right": pygame.Rect((COLS-1)*TILE_SIZE, (mid_row-1)*TILE_SIZE, TILE_SIZE, TILE_SIZE*3),
        }
        return {d: r for d, r in all_doors.items() if d in self.active_doors}

    def update(self, player):
        if not self.cleared:
            wall_rects = self.get_wall_rects()
            for enemy in self.enemies:
                if enemy.hp > 0:
                    enemy.update(player, wall_rects)
            if all(e.hp <= 0 for e in self.enemies):
                self.cleared = True
                if not self.reward_spawned:
                    self.reward_spawned = True

                # Une salle terminee a une chance de faire apparaitre un coffre
                if random.random() < 0.55:
                    self.reward_chests.append(Chest(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, "reward"))
                else:
                     item_type = random.choice(["heart", "speed"])
                     self.items.append(Item(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, item_type))



    def draw(self, screen, assets):
        self._draw_tiles(screen, assets)
         
        if self.chest is not None:
            self.chest.draw(screen, assets)
        
        for reward_chest in self.reward_chests:
            reward_chest.draw(screen, assets)

             
        for item in self.items:
            item.draw(screen, assets)

        for enemy in self.enemies:
            if enemy.hp > 0:
                enemy.draw(screen, assets)

    def _draw_tiles(self, screen, assets):
        for row in range(ROWS):
             for col in range(COLS):
                 tile = self.grid[row][col]
                 x = col * TILE_SIZE
                 y = row * TILE_SIZE

                 if tile == 1:
                     screen.blit(assets["wall"], (x, y))
                 elif tile == 2:
                     screen.blit(assets["door"], (x, y))
                 else:
                     screen.blit(assets["floor"], (x, y))



class Map:
    def __init__(self):
        self.rooms = {}
        for x in range(-1, 2):
            for y in range(-1, 2):
                self.rooms[(x, y)] = Room(x, y)

        self.current_pos = (0, 0)
        self.current_room = self.rooms[self.current_pos]
        self.current_room.visited = True
        self._init_active_doors()

    def _init_active_doors(self):
        neighbors = {"up": (0,-1), "down": (0,1), "left": (-1,0), "right": (1,0)}

        for (x, y), room in self.rooms.items():
            #la salle de départ a une seule porte vers la droite
            if (x, y) == (0, 0):
                room.add_door("right")
            else:
                for direction, (dx, dy) in neighbors.items():
                    if (x+dx, y+dy) in self.rooms and (x+dx, y+dy) != (0, 0):
                        room.add_door(direction)



    def change_room(self, dx, dy, player=None):
        if not self.current_room.cleared:
            return False
        new_pos = (self.current_pos[0]+dx, self.current_pos[1]+dy)
        if new_pos in self.rooms:
            self.current_pos = new_pos
            self.current_room = self.rooms[new_pos]
            self.current_room.visited = True
            if player:
                mid_col = COLS // 2
                mid_row = ROWS // 2
                if dx == 1:  player.rect.left = TILE_SIZE + 5
                if dx == -1: player.rect.right = (COLS-1)*TILE_SIZE - 5
                if dy == 1:  player.rect.top = TILE_SIZE + 5
                if dy == -1: player.rect.bottom = (ROWS-1)*TILE_SIZE - 5
            return True
        return False

    def update(self, player):
        self.current_room.update(player)

    def draw(self, screen, assets):
        self.current_room.draw(screen, assets)
        self._draw_minimap(screen)

    def _draw_minimap(self, screen):
        step = MINI_ROOM_SIZE + MINI_ROOM_GAP
        for (x, y), room in self.rooms.items():
            if not room.visited and (x, y) != self.current_pos:
                is_adjacent = any(
                    (self.current_pos[0]+dx, self.current_pos[1]+dy) == (x, y)
                    for dx, dy in [(0,-1),(0,1),(-1,0),(1,0)]
                )
                if not is_adjacent:
                    continue
                color = (60, 60, 60)
            elif not room.visited:
                continue
            elif (x, y) == self.current_pos:
                color = (255, 220, 50)
            elif room.cleared:
                color = (80, 180, 80)
            else:
                color = (180, 80, 80)

            draw_x = MINI_OFFSET_X + x * step
            draw_y = MINI_OFFSET_Y + y * step
            pygame.draw.rect(screen, color, (draw_x, draw_y, MINI_ROOM_SIZE, MINI_ROOM_SIZE))
            if (x, y) == self.current_pos:
                pygame.draw.rect(screen, (255,255,255), (draw_x, draw_y, MINI_ROOM_SIZE, MINI_ROOM_SIZE), 1)