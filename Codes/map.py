import random
from entitees import Enemy

class Room:
    def __init__(self, x, y):
        """Initialise la salle avec une position et des ennemis."""
        self.x = x
        self.y = y
        self.enemies = [Enemy() for _ in range(random.randint(1,3))]
        self.cleared = False

    def update(self, player):
        """Met à jour les ennemis de la salle si elle n'est pas vidée."""
        if not self.cleared:
            for enemy in self.enemies:
                if enemy.hp > 0:
                    enemy.update(player)

            if all(enemy.hp <= 0 for enemy in self.enemies):
                self.cleared = True

    def draw(self, screen):
        """Dessine les ennemis de la salle sur l'écran."""
        for enemy in self.enemies:
            if enemy.hp > 0:
                enemy.draw(screen)


class Map:
    def __init__(self):
        """Initialise la carte avec des salles."""
        self.rooms = {}

        # Génération simple
        for x in range(-1,2):
            for y in range(-1,2):
                self.rooms[(x,y)] = Room(x,y)

        self.current_pos = (0,0)
        self.current_room = self.rooms[self.current_pos]

    def change_room(self, dx, dy):
        """Change vers une nouvelle salle si elle existe."""
        new_pos = (self.current_pos[0] + dx, self.current_pos[1] + dy)

        if new_pos in self.rooms:
            self.current_pos = new_pos
            self.current_room = self.rooms[new_pos]