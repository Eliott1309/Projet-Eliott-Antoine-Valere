import pygame
import os

TILE_SIZE = 40

def load_assets():
    assets = {}
    
    base = os.path.dirname(os.path.abspath(__file__))
    
    assets["floor"] = pygame.image.load(os.path.join(base, "assets", "floor2.png")).convert()
    assets["wall"]  = pygame.image.load(os.path.join(base, "assets", "wall.png")).convert()
    assets["door"]  = pygame.image.load(os.path.join(base, "assets", "door.png")).convert()
    assets["enemy"] = pygame.image.load(os.path.join(base, "assets", "enemy.png")).convert_alpha()
    assets["player"]= pygame.image.load(os.path.join(base, "assets", "player.png")).convert_alpha()

    assets["floor"]  = pygame.transform.smoothscale(assets["floor"],  (TILE_SIZE, TILE_SIZE))
    assets["wall"]   = pygame.transform.smoothscale(assets["wall"],   (TILE_SIZE, TILE_SIZE))
    assets["door"]   = pygame.transform.smoothscale(assets["door"],   (TILE_SIZE, TILE_SIZE))
    assets["enemy"]  = pygame.transform.smoothscale(assets["enemy"],  (47, 47))
    assets["player"] = pygame.transform.smoothscale(assets["player"], (40, 40))

    assets["heart"] = pygame.image.load(os.path.join(base, "assets", "heart.png")).convert_alpha()
    assets["speed"] = pygame.image.load(os.path.join(base, "assets", "speed.png")).convert_alpha()

    assets["heart"] = pygame.transform.smoothscale(assets["heart"], (25, 25))
    assets["speed"] = pygame.transform.smoothscale(assets["speed"], (25, 25))

    assets["chest"] = pygame.image.load(os.path.join(base, "assets", "chest.png")).convert_alpha()
    assets["sword"] = pygame.image.load(os.path.join(base, "assets", "sword.png")).convert_alpha()
    assets["crossbow"] = pygame.image.load(os.path.join(base, "assets", "crossbow.png")).convert_alpha()

    assets["chest"] = pygame.transform.smoothscale(assets["chest"], (36, 36))
    assets["sword"] = pygame.transform.smoothscale(assets["sword"], (30, 30))
    assets["crossbow"] = pygame.transform.smoothscale(assets["crossbow"], (30, 30))

    assets["footstep"] = pygame.mixer.Sound(os.path.join(base, "assets", "footstep.wav"))
    assets["footstep"].set_volume(0.1)

    assets["typewriter"] = pygame.mixer.Sound(os.path.join(base, "assets", "typewriter.mp3"))
    assets["typewriter"].set_volume(0.25)
    return assets