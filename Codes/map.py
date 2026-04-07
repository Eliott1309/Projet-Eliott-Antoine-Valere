import random
import pygame
from entitees import Enemy

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
DOOR_SIZE = 60
DOOR_THICKNESS = 20

# Minimap
MINI_ROOM_SIZE = 14
MINI_ROOM_GAP = 4
MINI_OFFSET_X = SCREEN_WIDTH - 90
MINI_OFFSET_Y = 10

class Room:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.enemies = [Enemy() for _ in range(random.randint(1, 3))]
        self.cleared = False
        self.visited = False

        self.doors = {
            "up":    pygame.Rect((SCREEN_WIDTH - DOOR_SIZE) // 2, 0, DOOR_SIZE, DOOR_THICKNESS),
            "down":  pygame.Rect((SCREEN_WIDTH - DOOR_SIZE) // 2, SCREEN_HEIGHT - DOOR_THICKNESS, DOOR_SIZE, DOOR_THICKNESS),
            "left":  pygame.Rect(0, (SCREEN_HEIGHT - DOOR_SIZE) // 2, DOOR_THICKNESS, DOOR_SIZE),
            "right": pygame.Rect(SCREEN_WIDTH - DOOR_THICKNESS, (SCREEN_HEIGHT - DOOR_SIZE) // 2, DOOR_THICKNESS, DOOR_SIZE),
        }

        self.door_directions = {
            "up":    (0, -1),
            "down":  (0,  1),
            "left":  (-1, 0),
            "right": ( 1, 0),
        }

        # Portes actives (celles qui mènent à une vraie salle) — remplies par Map
        self.active_doors = set()

    def check_door_collision(self, player_rect):
        if not self.cleared:
            return None
        for direction, door_rect in self.doors.items():
            if direction in self.active_doors and player_rect.colliderect(door_rect):
                return self.door_directions[direction]
        return None

    def update(self, player):
        if not self.cleared:
            for enemy in self.enemies:
                if enemy.hp > 0:
                    enemy.update(player)
            if all(enemy.hp <= 0 for enemy in self.enemies):
                self.cleared = True

    def draw(self, screen):
        self._draw_doors(screen)
        for enemy in self.enemies:
            if enemy.hp > 0:
                enemy.draw(screen)

    def _draw_doors(self, screen):
        for direction, door_rect in self.doors.items():
            if direction not in self.active_doors:
                continue  # Pas de porte ici
            color = (0, 200, 80) if self.cleared else (120, 120, 120)
            pygame.draw.rect(screen, color, door_rect)


class Map:
    def __init__(self):
        self.rooms = {}

        for x in range(-1, 2):
            for y in range(-1, 2):
                self.rooms[(x, y)] = Room(x, y)

        self.current_pos = (0, 0)
        self.current_room = self.rooms[self.current_pos]
        self.current_room.visited = True

        # Calcule les portes actives pour chaque salle
        self._init_active_doors()

    def _init_active_doors(self):
        """Pour chaque salle, active uniquement les portes qui mènent à une salle existante."""
        neighbors = {
            "up":    (0, -1),
            "down":  (0,  1),
            "left":  (-1, 0),
            "right": ( 1, 0),
        }
        for (x, y), room in self.rooms.items():
            for direction, (dx, dy) in neighbors.items():
                if (x + dx, y + dy) in self.rooms:
                    room.active_doors.add(direction)

    def change_room(self, dx, dy, player=None):
        if not self.current_room.cleared:
            return False

        new_pos = (self.current_pos[0] + dx, self.current_pos[1] + dy)
        if new_pos in self.rooms:
            self.current_pos = new_pos
            self.current_room = self.rooms[new_pos]
            self.current_room.visited = True

            if player:
                if dx == 1:  player.rect.left = DOOR_THICKNESS + 5
                if dx == -1: player.rect.right = SCREEN_WIDTH - DOOR_THICKNESS - 5
                if dy == 1:  player.rect.top = DOOR_THICKNESS + 5
                if dy == -1: player.rect.bottom = SCREEN_HEIGHT - DOOR_THICKNESS - 5
            return True
        return False

    def update(self, player):
        self.current_room.update(player)
        direction = self.current_room.check_door_collision(player.rect)
        if direction:
            self.change_room(*direction, player=player)

    def draw(self, screen):
        self.current_room.draw(screen)
        self._draw_minimap(screen)

    def _draw_minimap(self, screen):
        """Dessine la minimap en haut à droite."""
        step = MINI_ROOM_SIZE + MINI_ROOM_GAP

        for (x, y), room in self.rooms.items():
            if not room.visited and (x, y) != self.current_pos:
                # Salle adjacente non visitée : afficher en gris très sombre si une porte y mène
                is_adjacent = any(
                    (self.current_pos[0] + dx, self.current_pos[1] + dy) == (x, y)
                    for dx, dy in [(0,-1),(0,1),(-1,0),(1,0)]
                )
                if not is_adjacent:
                    continue
                color = (60, 60, 60)  # salle accessible non visitée
            elif not room.visited:
                continue
            elif (x, y) == self.current_pos:
                color = (255, 220, 50)   # salle actuelle : jaune
            elif room.cleared:
                color = (80, 180, 80)    # salle vidée : vert
            else:
                color = (180, 80, 80)    # salle visitée non vidée : rouge

            draw_x = MINI_OFFSET_X + x * step
            draw_y = MINI_OFFSET_Y + y * step
            pygame.draw.rect(screen, color, (draw_x, draw_y, MINI_ROOM_SIZE, MINI_ROOM_SIZE))

            # Bordure blanche pour la salle actuelle
            if (x, y) == self.current_pos:
                pygame.draw.rect(screen, (255, 255, 255), (draw_x, draw_y, MINI_ROOM_SIZE, MINI_ROOM_SIZE), 1)