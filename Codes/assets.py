import pygame
import os

TILE_SIZE = 40

def load_assets():
    assets = {}
    
    base = os.path.dirname(os.path.abspath(__file__))
    
    assets["floor"] = pygame.image.load(os.path.join(base, "assets", "floor.png")).convert()
    assets["wall"]  = pygame.image.load(os.path.join(base, "assets", "wall.png")).convert()
    assets["door"]  = pygame.image.load(os.path.join(base, "assets", "door.png")).convert()
    assets["enemy"] = pygame.image.load(os.path.join(base, "assets", "enemy.png")).convert_alpha()
    assets["player"]= pygame.image.load(os.path.join(base, "assets", "player.png")).convert_alpha()

    assets["floor"]  = pygame.transform.scale(assets["floor"],  (TILE_SIZE, TILE_SIZE))
    assets["wall"]   = pygame.transform.scale(assets["wall"],   (TILE_SIZE, TILE_SIZE))
    assets["door"]   = pygame.transform.scale(assets["door"],   (TILE_SIZE, TILE_SIZE))
    assets["enemy"]  = pygame.transform.scale(assets["enemy"],  (47, 47))
    assets["player"] = pygame.transform.scale(assets["player"], (40, 40))

    assets["heart"] = pygame.image.load(os.path.join(base, "assets", "heart.png")).convert_alpha()
    assets["speed"] = pygame.image.load(os.path.join(base, "assets", "speed.png")).convert_alpha()

    assets["heart"] = pygame.transform.scale(assets["heart"], (25, 25))
    assets["speed"] = pygame.transform.scale(assets["speed"], (25, 25))

    assets["chest"] = pygame.image.load(os.path.join(base, "assets", "chest.png")).convert_alpha()
    assets["sword"] = pygame.image.load(os.path.join(base, "assets", "sword.png")).convert_alpha()
    assets["crossbow"] = pygame.image.load(os.path.join(base, "assets", "crossbow.png")).convert_alpha()

    assets["chest"] = pygame.transform.scale(assets["chest"], (36, 36))
    assets["sword"] = pygame.transform.scale(assets["sword"], (30, 30))
    assets["crossbow"] = pygame.transform.scale(assets["crossbow"], (30, 30))

    assets["footstep"] = pygame.mixer.Sound(os.path.join(base, "assets", "footstep.wav"))
    assets["footstep"].set_volume(0.1)

    return assets