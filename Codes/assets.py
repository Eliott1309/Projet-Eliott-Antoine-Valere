import pygame
import os

TILE_SIZE = 40

def load_assets():
    assets = {}
    
    base = os.path.dirname(os.path.abspath(__file__))

    def load_image(name, filename, alpha=True):
        path = os.path.join(base, "assets", filename)
        if alpha:
            assets[name] = pygame.image.load(path).convert_alpha()
        else:
            assets[name] = pygame.image.load(path).convert()

    def make_animation(name):
        image = assets[name]
        w, h = image.get_size()
        frame_1 = image
        frame_2 = pygame.transform.smoothscale(image, (w, max(1, h - 3)))
        frame_2 = pygame.transform.smoothscale(frame_2, (w, h))
        assets[name + "_anim"] = [frame_1, frame_2]
    
    load_image("floor", "floor.png", False)
    load_image("wall", "wall.png", True)
    load_image("door", "door.png", True)
    load_image("enemy", "enemy.png", True)
    load_image("player", "player.png", True)

    assets["floor"]  = pygame.transform.smoothscale(assets["floor"],  (TILE_SIZE, TILE_SIZE))
    assets["wall"]   = pygame.transform.smoothscale(assets["wall"],   (TILE_SIZE, TILE_SIZE))
    assets["door"]   = pygame.transform.smoothscale(assets["door"],   (TILE_SIZE, TILE_SIZE))
    assets["enemy"]  = pygame.transform.smoothscale(assets["enemy"],  (47, 47))
    assets["player"] = pygame.transform.smoothscale(assets["player"], (40, 40))

    load_image("player_armor", "player_armor.png", True)
    assets["player_armor"] = pygame.transform.smoothscale(assets["player_armor"], (58, 58))
    make_animation("player_armor")

    load_image("enemy_stalker", "enemy_stalker.png", True)
    load_image("enemy_shooter", "enemy_shooter.png", True)
    load_image("enemy_charger", "enemy_charger.png", True)
    load_image("enemy_bomber", "enemy_bomber.png", True)
    load_image("boss_warden", "boss_warden.png", True)
    load_image("boss_sorcerer", "boss_sorcerer.png", True)

    for key in ["enemy_stalker", "enemy_shooter", "enemy_charger", "enemy_bomber"]:
        assets[key] = pygame.transform.smoothscale(assets[key], (47, 47))
    assets["boss_warden"] = pygame.transform.smoothscale(assets["boss_warden"], (76, 76))
    assets["boss_sorcerer"] = pygame.transform.smoothscale(assets["boss_sorcerer"], (76, 76))

    assets["heart"] = pygame.image.load(os.path.join(base, "assets", "heart.png")).convert_alpha()
    assets["speed"] = pygame.image.load(os.path.join(base, "assets", "speed.png")).convert_alpha()

    assets["heart"] = pygame.transform.smoothscale(assets["heart"], (25, 25))
    assets["speed"] = pygame.transform.smoothscale(assets["speed"], (50, 50))

    load_image("chest", "chest.png", True)
    load_image("sword", "sword.png", True)
    load_image("crossbow", "crossbow.png", True)
    load_image("bow", "bow.png", True)
    load_image("magic_wand", "magic_wand.png", True)
    load_image("arrow", "arrow.png", True)

    assets["chest"] = pygame.transform.smoothscale(assets["chest"], (36, 36))
    assets["sword"] = pygame.transform.smoothscale(assets["sword"], (30, 30))
    assets["crossbow"] = pygame.transform.smoothscale(assets["crossbow"], (30, 30))
    assets["bow"] = pygame.transform.smoothscale(assets["bow"], (30, 30))
    assets["magic_wand"] = pygame.transform.smoothscale(assets["magic_wand"], (30, 30))
    assets["arrow"] = pygame.transform.smoothscale(assets["arrow"], (30, 15))

    for key in [
        "player", "enemy", "enemy_stalker", "enemy_shooter", "enemy_charger",
        "enemy_bomber", "boss_warden", "boss_sorcerer"
    ]:
        make_animation(key)

    assets["footstep"] = pygame.mixer.Sound(os.path.join(base, "assets", "footstep.wav"))
    assets["footstep"].set_volume(0.1)

    assets["typewriter"] = pygame.mixer.Sound(os.path.join(base, "assets", "typewriter.mp3"))
    assets["typewriter"].set_volume(0.25)
    '''for level in [2, 3]:
        for kind in ["stalker", "shooter", "charger", "bomber"]:
            filename = f"enemy_{kind}_{level}.png"
            path = os.path.join(base, "assets", filename)
            if os.path.exists(path):
                key = f"enemy_{kind}_lv{level}"
                assets[key] = pygame.image.load(path).convert_alpha()
                assets[key] = pygame.transform.smoothscale(assets[key], (47, 47))'''  

    # Avant le return dans load_assets()
    for level, filename in [(2, "bg2.png"), (3, "bg3.png")]:
        path = os.path.join(base, "assets", filename)
        if os.path.exists(path):
            assets[f"floor_lv{level}"] = pygame.image.load(path).convert()
            assets[f"floor_lv{level}"] = pygame.transform.smoothscale(assets[f"floor_lv{level}"], (TILE_SIZE, TILE_SIZE))
    
    return assets

