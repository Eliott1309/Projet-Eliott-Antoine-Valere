import random
import pygame
from entitees import Enemy

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
DOOR_SIZE = 60
DOOR_THICKNESS = 20

class Room:
    def __init__(self, x, y):
        """Initialise la salle avec une position, des ennemis et des portes."""
        self.x = x
        self.y = y
        self.enemies = [Enemy() for _ in range(random.randint(1, 3))]
        self.cleared = False

        # Portes : centre de chaque côté (rect de collision)
        self.doors = {
            "up":    pygame.Rect((SCREEN_WIDTH - DOOR_SIZE) // 2, 0, DOOR_SIZE, DOOR_THICKNESS),
            "down":  pygame.Rect((SCREEN_WIDTH - DOOR_SIZE) // 2, SCREEN_HEIGHT - DOOR_THICKNESS, DOOR_SIZE, DOOR_THICKNESS),
            "left":  pygame.Rect(0, (SCREEN_HEIGHT - DOOR_SIZE) // 2, DOOR_THICKNESS, DOOR_SIZE),
            "right": pygame.Rect(SCREEN_WIDTH - DOOR_THICKNESS, (SCREEN_HEIGHT - DOOR_SIZE) // 2, DOOR_THICKNESS, DOOR_SIZE),
        }

        # Direction → (dx, dy) pour changer de salle
        self.door_directions = {
            "up":    (0, -1),
            "down":  (0,  1),
            "left":  (-1, 0),
            "right": ( 1, 0),
        }

    def check_door_collision(self, player_rect):
        """
        Retourne (dx, dy) si le joueur touche une porte ET que la salle est vidée.
        Retourne None sinon.
        """
        if not self.cleared:
            return None
        for direction, door_rect in self.doors.items():
            if player_rect.colliderect(door_rect):
                return self.door_directions[direction]
        return None

    def update(self, player):
        """Met à jour les ennemis de la salle si elle n'est pas vidée."""
        if not self.cleared:
            for enemy in self.enemies:
                if enemy.hp > 0:
                    enemy.update(player)
            if all(enemy.hp <= 0 for enemy in self.enemies):
                self.cleared = True

    def draw(self, screen):
        """Dessine les portes et les ennemis de la salle."""
        self._draw_doors(screen)
        for enemy in self.enemies:
            if enemy.hp > 0:
                enemy.draw(screen)

    def _draw_doors(self, screen):
        """Dessine les portes : grises si bloquées, vertes si ouvertes."""
        color = (0, 200, 80) if self.cleared else (120, 120, 120)
        for door_rect in self.doors.values():
            pygame.draw.rect(screen, color, door_rect)


class Map:
    def __init__(self):
        """Initialise la carte avec des salles."""
        self.rooms = {}

        for x in range(-1, 2):
            for y in range(-1, 2):
                self.rooms[(x, y)] = Room(x, y)

        self.current_pos = (0, 0)
        self.current_room = self.rooms[self.current_pos]

    def change_room(self, dx, dy, player=None):
        if not self.current_room.cleared:
            return False

        new_pos = (self.current_pos[0] + dx, self.current_pos[1] + dy)
        if new_pos in self.rooms:
            self.current_pos = new_pos
            self.current_room = self.rooms[new_pos]

            # Repositionne le joueur de l'autre côté de la porte
            if player:
                if dx == 1:  player.rect.left = 20
                if dx == -1: player.rect.right = 780
                if dy == 1:  player.rect.top = 20
                if dy == -1: player.rect.bottom = 580
            return True
        return False

    def update(self, player):
        self.current_room.update(player)
        direction = self.current_room.check_door_collision(player.rect)
        if direction:
            self.change_room(*direction, player=player)  # passer player ici
    
    def draw(self, screen):
        """Dessine la salle actuelle."""
        self.current_room.draw(screen)