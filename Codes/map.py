import random
import pygame
from entitees import Enemy

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
DOOR_SIZE = 60
WALL_THICKNESS = 30

MINI_ROOM_SIZE = 14
MINI_ROOM_GAP = 4
MINI_OFFSET_X = SCREEN_WIDTH - 90
MINI_OFFSET_Y = 30

class Room:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.enemies = [Enemy() for _ in range(random.randint(1, 3))]
        self.cleared = False
        self.visited = False
        self.active_doors = set()

        self.door_directions = {
            "up":    (0, -1),
            "down":  (0,  1),
            "left":  (-1, 0),
            "right": ( 1, 0),
        }

    def get_wall_rects(self):
        """
        Retourne la liste des rectangles de collision des murs.
        Chaque côté est découpé en segments autour de l'ouverture de porte.
        """
        rects = []
        door_start = (SCREEN_WIDTH - DOOR_SIZE) // 2
        door_end = door_start + DOOR_SIZE
        door_start_v = (SCREEN_HEIGHT - DOOR_SIZE) // 2
        door_end_v = door_start_v + DOOR_SIZE

        # Mur du haut
        if "up" in self.active_doors:
            rects.append(pygame.Rect(0, 0, door_start, WALL_THICKNESS))
            rects.append(pygame.Rect(door_end, 0, SCREEN_WIDTH - door_end, WALL_THICKNESS))
        else:
            rects.append(pygame.Rect(0, 0, SCREEN_WIDTH, WALL_THICKNESS))

        # Mur du bas
        if "down" in self.active_doors:
            rects.append(pygame.Rect(0, SCREEN_HEIGHT - WALL_THICKNESS, door_start, WALL_THICKNESS))
            rects.append(pygame.Rect(door_end, SCREEN_HEIGHT - WALL_THICKNESS, SCREEN_WIDTH - door_end, WALL_THICKNESS))
        else:
            rects.append(pygame.Rect(0, SCREEN_HEIGHT - WALL_THICKNESS, SCREEN_WIDTH, WALL_THICKNESS))

        # Mur gauche
        if "left" in self.active_doors:
            rects.append(pygame.Rect(0, 0, WALL_THICKNESS, door_start_v))
            rects.append(pygame.Rect(0, door_end_v, WALL_THICKNESS, SCREEN_HEIGHT - door_end_v))
        else:
            rects.append(pygame.Rect(0, 0, WALL_THICKNESS, SCREEN_HEIGHT))

        # Mur droit
        if "right" in self.active_doors:
            rects.append(pygame.Rect(SCREEN_WIDTH - WALL_THICKNESS, 0, WALL_THICKNESS, door_start_v))
            rects.append(pygame.Rect(SCREEN_WIDTH - WALL_THICKNESS, door_end_v, WALL_THICKNESS, SCREEN_HEIGHT - door_end_v))
        else:
            rects.append(pygame.Rect(SCREEN_WIDTH - WALL_THICKNESS, 0, WALL_THICKNESS, SCREEN_HEIGHT))

        return rects

    def get_door_rects(self):
        """Retourne les rects des portes actives avec leur direction."""
        door_start_h = (SCREEN_WIDTH - DOOR_SIZE) // 2
        door_start_v = (SCREEN_HEIGHT - DOOR_SIZE) // 2
        all_doors = {
            "up":    pygame.Rect(door_start_h, 0, DOOR_SIZE, WALL_THICKNESS),
            "down":  pygame.Rect(door_start_h, SCREEN_HEIGHT - WALL_THICKNESS, DOOR_SIZE, WALL_THICKNESS),
            "left":  pygame.Rect(0, door_start_v, WALL_THICKNESS, DOOR_SIZE),
            "right": pygame.Rect(SCREEN_WIDTH - WALL_THICKNESS, door_start_v, WALL_THICKNESS, DOOR_SIZE),
        }
        return {d: r for d, r in all_doors.items() if d in self.active_doors}

    def update(self, player):
        if not self.cleared:
            for enemy in self.enemies:
                if enemy.hp > 0:
                    enemy.update(player)
            if all(enemy.hp <= 0 for enemy in self.enemies):
                self.cleared = True

    def draw(self, screen):
        self._draw_walls(screen)
        for enemy in self.enemies:
            if enemy.hp > 0:
                enemy.draw(screen)

    def _draw_walls(self, screen):
        # Murs pleins
        for rect in self.get_wall_rects():
            pygame.draw.rect(screen, (80, 60, 40), rect)

        # Portes
        for direction, rect in self.get_door_rects().items():
            color = (0, 200, 80) if self.cleared else (120, 80, 80)
            pygame.draw.rect(screen, color, rect)


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
                if dx == 1:  player.rect.left = WALL_THICKNESS + 5
                if dx == -1: player.rect.right = SCREEN_WIDTH - WALL_THICKNESS - 5
                if dy == 1:  player.rect.top = WALL_THICKNESS + 5
                if dy == -1: player.rect.bottom = SCREEN_HEIGHT - WALL_THICKNESS - 5
            return True
        return False

    def update(self, player):
        self.current_room.update(player)

    def draw(self, screen):
        self.current_room.draw(screen)
        self._draw_minimap(screen)

    def _draw_minimap(self, screen):
        step = MINI_ROOM_SIZE + MINI_ROOM_GAP
        for (x, y), room in self.rooms.items():
            if not room.visited and (x, y) != self.current_pos:
                is_adjacent = any(
                    (self.current_pos[0] + dx, self.current_pos[1] + dy) == (x, y)
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