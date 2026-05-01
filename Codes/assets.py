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
    assets["enemy"]  = pygame.transform.scale(assets["enemy"],  (40, 40))
    assets["player"] = pygame.transform.scale(assets["player"], (40, 40))

    assets["heart"] = pygame.image.load(os.path.join(base, "assets", "heart.png")).convert_alpha()
    assets["speed"] = pygame.image.load(os.path.join(base, "assets", "speed.png")).convert_alpha()

    assets["heart"] = pygame.transform.scale(assets["heart"], (28, 28))
    assets["speed"] = pygame.transform.scale(assets["speed"], (28, 28))

    return assets