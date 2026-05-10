import random
import pygame
from config_carte import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, COLS, ROWS, MINI_ROOM_SIZE, MINI_ROOM_GAP
from salle import Room


class Map:
    #initialise une map pour un niveau, avec ses salles et la position de depart
    def __init__(self, level=1, num_rooms=None):
        self.level = level
        self.rooms = {}
        self.current_pos = (0, 0)
        if num_rooms is None:
            num_rooms = 8 + level * 2
        self._creer_salles(max(num_rooms, 6))
        self.current_room = self.rooms[self.current_pos]
        self.current_room.visited = True
        self.next_level_triggered = False

    #ca prend le nombre de salles, ca cree le chemin de la map et ca remplit self.rooms
    def _creer_salles(self, num_rooms):
        dirs = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        dir_names = {(0, -1): "up", (0, 1): "down", (-1, 0): "left", (1, 0): "right"}
        visited, stack = {(0, 0)}, [(0, 0)]
        while len(visited) < num_rooms and stack:
            pos = stack[-1]
            random.shuffle(dirs)
            nxt = next(((pos[0] + dx, pos[1] + dy) for dx, dy in dirs
                        if (pos[0] + dx, pos[1] + dy) not in visited), None)
            if nxt:
                visited.add(nxt)
                stack.append(nxt)
            else:
                stack.pop()
        while len(visited) < num_rooms:
            base = random.choice(list(visited))
            random.shuffle(dirs)
            for dx, dy in dirs:
                npos = (base[0] + dx, base[1] + dy)
                if npos not in visited:
                    visited.add(npos)
                    break
        exit_pos = max(visited, key=lambda p: abs(p[0]) + abs(p[1]))
        for coord in visited:
            self.rooms[coord] = Room(coord[0], coord[1], level=self.level,
                                     is_start=coord == (0, 0), is_exit=coord == exit_pos)
        for coord in visited:
            for dx, dy in dirs:
                if (coord[0] + dx, coord[1] + dy) in self.rooms:
                    self.rooms[coord].add_door(dir_names[(dx, dy)])

    #prend une direction, change la salle si elle existe et replace le joueur si besoin
    def change_room(self, dx, dy, player=None):
        if not self.current_room.cleared:
            return False
        new_pos = (self.current_pos[0] + dx, self.current_pos[1] + dy)
        if new_pos not in self.rooms:
            return False
        self.current_pos = new_pos
        self.current_room = self.rooms[new_pos]
        self.current_room.visited = True
        if player:
            margin = TILE_SIZE * 2 + 5
            if dx == 1: player.rect.left = margin
            if dx == -1: player.rect.right = COLS * TILE_SIZE - margin
            if dy == 1: player.rect.top = margin
            if dy == -1: player.rect.bottom = ROWS * TILE_SIZE - margin
            player.transition_lock = 20
        return True

    #met a jour la salle actuelle et regarde si le joueur touche le portail de fin
    def update(self, player):
        self.current_room.update(player)
        portal = self.current_room.portal
        if portal and portal.active and portal.rect.colliderect(player.rect):
            self.next_level_triggered = True

    #dessine la salle actuelle puis la mini carte par dessus
    def draw(self, screen, assets):
        self.current_room.draw(screen, assets)
        self._dessiner_mini_carte(screen)

    #ca prend l'ecran, ca dessine les salles deja vues et ca ne renvoie rien
    def _dessiner_mini_carte(self, screen):
        step = MINI_ROOM_SIZE + MINI_ROOM_GAP
        all_x = [x for x, _y in self.rooms]
        all_y = [y for _x, y in self.rooms]
        offset_x = SCREEN_WIDTH - (max(all_x) - min(all_x) + 1) * step - 10
        offset_y = 10
        for (x, y), room in self.rooms.items():
            if not room.visited and not self._est_a_cote(x, y):
                continue
            rx = offset_x + (x - min(all_x)) * step
            ry = offset_y + (y - min(all_y)) * step
            color = self._couleur_salle(room, (x, y))
            pygame.draw.rect(screen, color, (rx, ry, MINI_ROOM_SIZE, MINI_ROOM_SIZE), border_radius=2)
            if room.is_exit:
                pygame.draw.rect(screen, (200, 130, 255), (rx - 1, ry - 1, MINI_ROOM_SIZE + 2, MINI_ROOM_SIZE + 2), 1)

    #ca prend les coordonnees d'une salle et ca dit si elle touche la salle actuelle
    def _est_a_cote(self, x, y):
        return any((self.current_pos[0] + dx, self.current_pos[1] + dy) == (x, y)
                   for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)])

    #ca prend une salle et ses coordonnees, puis ca renvoie la couleur pour la mini carte
    def _couleur_salle(self, room, coord):
        if coord == self.current_pos:
            return (255, 255, 120)
        if not room.visited:
            return (70, 70, 85)
        if room.is_exit:
            return (160, 80, 255)
        if room.cleared:
            return (80, 180, 110)
        return (180, 80, 80)

