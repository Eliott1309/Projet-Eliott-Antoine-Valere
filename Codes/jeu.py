import os
import json
import random
import sys
import pygame
from carte import Map, SCREEN_HEIGHT, SCREEN_WIDTH
from effets import DynamicLighting, FadeTransition, ParticleSystem, ScreenShake
from texte import draw_dialog_box, get_medieval_font
from interface import draw_extra_hud
from joueur import Player
from projectiles import Bullet, EnemyBullet, Explosion
from actions_jeu import (add_score_for_dead_enemies, collect_enemy_attacks,
                         collect_items, create_magic_explosion, draw_frame,
                         load_bg, open_chests, player_touch_enemies,
                         show_game_over, show_level_transition)

base = os.path.dirname(os.path.abspath(__file__))

def sauvegarder_partie(player, current_level, score):
    data = {
        "level": current_level,
        "score": score,
        "hp": player.hp,
        "armor_hp": player.armor_hp,
        "has_armor": player.has_armor,
        "weapons": player.weapons,
        "weapon": player.weapon,
        "damage_boost": player.damage_boost,
        "speed": player.speed,
        "range_boost": player.range_boost,
        "inventory": player.inventory,
    }
    with open("sauvegarde.json", "w") as f:
        json.dump(data, f)

def charger_partie():
    try:
        with open("sauvegarde.json", "r") as f:
            return json.load(f)
    except:
        return None

def lancer_jeu(keyboard_layout="azerty", assets=None, charger = False):

    pygame.init()

    WIDTH, HEIGHT = 800, 600
    game_surface = pygame.Surface((WIDTH, HEIGHT))
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mini Isaac")

    try:
        pygame.mixer.music.load(os.path.join(base, "assets", "music.mp3"))
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
    except:
        pass

    clock = pygame.time.Clock()

    font_game_over = get_medieval_font(80)
    font_restart   = get_medieval_font(32)
    font_hud       = get_medieval_font(24)
    font_message   = get_medieval_font(30)

    WHITE = (255, 255, 255)
    RED   = (200,  50,  50)
    BLACK = (0,    0,    0)
    CONTACT_DAMAGE = 6
    BOW_KNOCKBACK = 100

    shake        = ScreenShake()
    particles    = ParticleSystem()
    lighting     = DynamicLighting(WIDTH, HEIGHT)
    fade         = FadeTransition(WIDTH, HEIGHT)




    player = Player(keyboard_layout, assets, game_surface, font_hud, particles, shake, fade)
    data = None
    if charger:
        data = charger_partie()
    if data:
        player.hp = data["hp"]
        player.armor_hp = data["armor_hp"]
        player.has_armor = data["has_armor"]
        player.weapons = data["weapons"]
        player.weapon = data["weapon"]
        player.damage_boost = data["damage_boost"]
        player.speed = data["speed"]
        player.range_boost = data["range_boost"]
        player.inventory = data.get("inventory", [])
        current_level = data["level"]
        score = data["score"]
        game_map = Map(level=current_level)
        current_bg = load_bg(current_level, base, WIDTH, HEIGHT)
    else:
        current_level = 1
        game_map = Map(level=current_level)
        current_bg = load_bg(1, base, WIDTH, HEIGHT)
        score = 0
    bullets, explosions = [], []
    enemy_bullets = []
    warning_circles = []

    game_finished = False
    ending_transition = False
    ending_text_index = 0
    ending_message = "Vous avez sauve la princesse. Le royaume est enfin libere."
    princess_rect = pygame.Rect(WIDTH//2 - 25, HEIGHT//2 - 35, 50, 70)


    counted_dead_enemies = set()
    pickup_message = ""
    pickup_message_timer = 0

    quest_transition = False
    quest_text_index = 0
    quest_message = ("Vous devez sauver la princesse. Tuez d'abord les ennemis "
                     "dans les salles environnantes avant de pouvoir la retrouver.")
    typewriter_channel = None
    shoot_cooldown = 0
    running = True

    extra_lights = []
    extra_lights_timer = []

    while running:
        clock.tick(60)
        game_surface.fill(BLACK)
        game_surface.blit(current_bg, (0, 0))
        keys = pygame.key.get_pressed()

        if pickup_message_timer > 0:
            pickup_message_timer -= 1

        for i in range(len(extra_lights_timer) - 1, -1, -1):
            extra_lights_timer[i] -= 1
            if extra_lights_timer[i] <= 0:
                extra_lights.pop(i)
                extra_lights_timer.pop(i)

        portal = game_map.current_room.portal
        portal_light = []
        if portal and portal.active:
            portal_light = [(portal.rect.centerx, portal.rect.centery, 80, (180, 100, 255))]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if quest_transition and event.key == pygame.K_SPACE:
                    if quest_text_index < len(quest_message):
                        quest_text_index = len(quest_message)
                        if typewriter_channel: typewriter_channel.stop(); typewriter_channel = None
                    else:
                        quest_transition = False

                if ending_transition and event.key == pygame.K_SPACE:
                    if ending_text_index < len(ending_message):
                        ending_text_index = len(ending_message)
                    else:
                        running = False
                if event.key == pygame.K_F5:
                    sauvegarder_partie(player, current_level, score)
                    pickup_message = "Partie sauvegardee !"
                    pickup_message_timer = 120
                if event.key == pygame.K_1: player.switch_weapon()
                elif event.key == pygame.K_2: player.use_inventory_item(0)
                elif event.key == pygame.K_3: player.use_inventory_item(1)
                elif event.key == pygame.K_4: player.use_inventory_item(2)
                elif event.key == pygame.K_5: player.use_inventory_item(3)

        if game_finished:
            if not ending_transition:
                player.move(keys, game_map)
                player.keep_inside_screen()

            game_surface.fill((30, 20, 45))
            pygame.draw.rect(game_surface, (80, 60, 100), (0, 0, WIDTH, HEIGHT), 12)
            pygame.draw.rect(game_surface, (245, 190, 220), princess_rect, border_radius=10)
            pygame.draw.circle(game_surface, (255, 225, 190), (princess_rect.centerx, princess_rect.y + 15), 16)
            pygame.draw.rect(game_surface, (255, 220, 80), (princess_rect.x + 8, princess_rect.y - 8, 34, 10), border_radius=3)
            label = font_message.render("Princesse", True, WHITE)
            game_surface.blit(label, label.get_rect(center=(WIDTH//2, HEIGHT//2 + 55)))

            if player.rect.colliderect(princess_rect):
                ending_transition = True

            if ending_transition:
                if ending_text_index < len(ending_message):
                    ending_text_index += 1
                draw_dialog_box(game_surface, ending_message, WIDTH, HEIGHT, ending_text_index)

            player.draw()
            # Rendu final avec screenshake
            offset = shake.get_offset()
            screen.fill(BLACK)
            screen.blit(game_surface, offset)
            fade.update(); fade.draw(screen)
            pygame.display.flip()
            continue

        if quest_transition:
            if quest_text_index < len(quest_message):
                quest_text_index += 1
                if typewriter_channel is None or not typewriter_channel.get_busy():
                    typewriter_channel = assets["typewriter"].play()
            else:
                if typewriter_channel: typewriter_channel.stop(); typewriter_channel = None
            draw_dialog_box(game_surface, quest_message, WIDTH, HEIGHT, quest_text_index)
            screen.fill(BLACK)
            screen.blit(game_surface, (0, 0))
            pygame.display.flip()
            continue

        if not fade.is_active:
            old_pos = game_map.current_pos
            player.move(keys, game_map)
            if current_level == 1 and old_pos == (0, 0) and game_map.current_pos != (0, 0):
                quest_transition = True
                quest_text_index = 0

        if player.attack_timer > 0:
            player.attack_timer -= 1
        if shoot_cooldown > 0:
            shoot_cooldown -= 1

        if shoot_cooldown == 0 and not fade.is_active:
            dx, dy = 0, 0
            if keys[pygame.K_i]: dx, dy = 0, -1
            elif keys[pygame.K_k]: dx, dy = 0,  1
            elif keys[pygame.K_j]: dx, dy = -1, 0
            elif keys[pygame.K_l]: dx, dy =  1, 0

            if player.weapon and (dx != 0 or dy != 0):
                player.last_direction = (dx, dy)
                if player.weapon == "sword":
                    player.sword_attack(dx, dy, game_map.current_room.enemies)
                    shoot_cooldown = 15

                elif player.weapon == "crossbow":
                    bullets.append(Bullet(player.rect.centerx, player.rect.centery, dx, dy,
                                          3+player.damage_boost, 800+player.range_boost,
                                          (230,230,230), 10, pierce=3, image=assets["arrow"]))
                    particles.emit_sparks(player.rect.centerx, player.rect.centery, count=4, color=(200,200,220))
                    shoot_cooldown = 75

                elif player.weapon == "bow":
                    bullets.append(Bullet(player.rect.centerx, player.rect.centery, dx, dy,
                                          1+player.damage_boost, 520+player.range_boost,
                                          (120,220,120), 8, image=assets["arrow"]))
                    player.rect.x -= dx * BOW_KNOCKBACK; player._resolve_collisions(game_map, "x")
                    player.rect.y -= dy * BOW_KNOCKBACK; player._resolve_collisions(game_map, "y")
                    shoot_cooldown = 15

                elif player.weapon == "magic_wand":
                    bullets.append(Bullet(player.rect.centerx, player.rect.centery, dx, dy,
                                          1+player.damage_boost, 650+player.range_boost,
                                          (160,90,255), 14, pierce=1, magic=True))
                    particles.emit_magic(player.rect.centerx, player.rect.centery, count=6)
                    shoot_cooldown = 45

        wall_rects = game_map.current_room.get_wall_rects()
        for bullet in bullets[:]:
            bullet.update()
            if not game_surface.get_rect().colliderect(bullet.rect):
                bullets.remove(bullet); continue
            if bullet.distance_travelled >= bullet.max_distance:
                bullets.remove(bullet); continue
            hit_wall = any(bullet.rect.colliderect(w) for w in wall_rects)
            if hit_wall:
                if bullet.magic: create_magic_explosion(bullet.rect.centerx, bullet.rect.centery, explosions, game_map, player, particles, shake, extra_lights, extra_lights_timer, Explosion)
                else: particles.emit_sparks(bullet.rect.centerx, bullet.rect.centery, count=4, color=bullet.color)
                bullets.remove(bullet); continue
            for enemy in game_map.current_room.enemies:
                if enemy.hp > 0 and bullet.rect.colliderect(enemy.rect) and id(enemy) not in bullet.hit_enemies:
                    enemy.hp -= bullet.damage
                    bullet.hit_enemies.add(id(enemy))
                    particles.emit_blood(bullet.rect.centerx, bullet.rect.centery, count=8)
                    shake.trigger(intensity=3, duration=5)
                    if bullet.magic:
                        create_magic_explosion(bullet.rect.centerx, bullet.rect.centery, explosions, game_map, player, particles, shake, extra_lights, extra_lights_timer, Explosion)
                        if bullet in bullets: bullets.remove(bullet)
                        break
                    bullet.pierce -= 1
                    if bullet.pierce <= 0:
                        if bullet in bullets: bullets.remove(bullet)
                        break

        score = add_score_for_dead_enemies(game_map, counted_dead_enemies, particles, shake, score)

        game_map.update(player)
        collect_enemy_attacks(game_map, enemy_bullets, player, warning_circles)

        for enemy_bullet in enemy_bullets[:]:
            enemy_bullet.update()
            if not game_surface.get_rect().colliderect(enemy_bullet.rect):
                enemy_bullets.remove(enemy_bullet)
                continue
            if enemy_bullet.rect.colliderect(player.rect):
                player.take_damage(enemy_bullet.damage)
                particles.emit_sparks(player.rect.centerx, player.rect.centery, count=6, color=(255, 80, 80))
                enemy_bullets.remove(enemy_bullet)
                continue


            if any(enemy_bullet.rect.colliderect(w) for w in wall_rects):
                particles.emit_sparks(enemy_bullet.rect.centerx, enemy_bullet.rect.centery,
                                      count=3, color=enemy_bullet.color)
                enemy_bullets.remove(enemy_bullet)
                continue

        # Passage au niveau suivant
        if game_map.next_level_triggered:
            if current_level >= 10:
                game_finished = True
                game_map.next_level_triggered = False
                bullets.clear(); explosions.clear()
                enemy_bullets.clear(); warning_circles.clear()
                player.rect.center = (WIDTH//2, HEIGHT - 80)
            else:
                current_level += 1
                current_bg = load_bg(current_level, base, WIDTH, HEIGHT)
                show_level_transition(current_level, screen, WIDTH, HEIGHT, get_medieval_font)
                game_map = Map(level=current_level)
                bullets.clear(); explosions.clear()
                enemy_bullets.clear(); warning_circles.clear()
                particles.particles.clear()
                extra_lights.clear(); extra_lights_timer.clear()
                player.rect.center = (WIDTH//2, HEIGHT//2)
                player.transition_lock = 0
                score += current_level * 500
                pickup_message = f"Niveau {current_level} â€” Bonne chance !"
                pickup_message_timer = 180

        message, timer = open_chests(player, game_map.current_room, particles)
        if timer:
            pickup_message, pickup_message_timer = message, timer

        message, timer = collect_items(player, game_map.current_room, particles)
        if timer:
            pickup_message, pickup_message_timer = message, timer

        player_touch_enemies(player, game_map.current_room, CONTACT_DAMAGE)

        if not player.is_alive():
            running = show_game_over(
                screen, game_surface, current_bg,
                (font_game_over, font_restart), (RED, WHITE, BLACK),
                score, WIDTH, HEIGHT
            )
            continue

        hud_data = (draw_extra_hud, score, pickup_message, pickup_message_timer,
                    font_hud, font_message, WIDTH)
        draw_frame(game_surface, screen, game_map, assets, particles, player,
                   hud_data, bullets, enemy_bullets, explosions, warning_circles,
                   lighting, extra_lights, portal_light, shake, fade, BLACK)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    lancer_jeu()

