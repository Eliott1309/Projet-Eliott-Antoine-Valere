import os
import pygame
from projectiles import EnemyBullet


def load_bg(level, base, width, height):
    if level <= 3:
        name = "bg.jpeg"      
    elif level <= 6:
        name = "bg2.png"      
    else:
        name = "bg3.png"
    img = pygame.image.load(os.path.join(base, "assets", name))
    return pygame.transform.scale(img, (width, height))


#ca prend la map, les ennemis deja comptes et le score, puis ca ajoute les points quand un ennemi meurt et ca renvoie le nouveau score
def ajouter_score_ennemis_morts(game_map, counted_dead_enemies, particles, shake, score):
    for enemy in game_map.current_room.enemies:
        if enemy.hp <= 0 and id(enemy) not in counted_dead_enemies:
            counted_dead_enemies.add(id(enemy))
            score += 100
            particles.emit_blood(enemy.rect.centerx, enemy.rect.centery, count=15)
            particles.emit_sparks(enemy.rect.centerx, enemy.rect.centery, count=6)
            shake.trigger(intensity=5, duration=8)
    return score


#ca prend une position et les listes d'effets, ca cree une explosion magique et ca retire de la vie aux ennemis autour
def faire_explosion_magique(x, y, explosions, game_map, player, particles,
                            shake, extra_lights, extra_lights_timer, Explosion):
    explosions.append(Explosion(x, y))
    explosion_rect = pygame.Rect(x - 55, y - 55, 110, 110)
    particles.emit_explosion(x, y)
    shake.trigger(intensity=8, duration=14)
    extra_lights.append([x, y, 120, (160, 90, 255)])
    extra_lights_timer.append(12)
    for enemy in game_map.current_room.enemies:
        if enemy.hp > 0 and explosion_rect.colliderect(enemy.rect):
            enemy.hp -= 2 + player.damage_boost


#ca prend la position d'un ennemi et le joueur, ca affiche un cercle dangereux et ca blesse si le joueur est dedans
def faire_attaque_zone_ennemi(x, y, player, warning_circles, radius=70, damage=8):
    warning_circles.append([x, y, radius, 14])
    burst_rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
    if burst_rect.colliderect(player.rect):
        player.take_damage(damage)


#ca prend les ennemis de la salle, ca recupere leurs tirs en attente et ca les met dans les listes du jeu
def recuperer_attaques_ennemis(game_map, enemy_bullets, player, warning_circles):
    for enemy in game_map.current_room.enemies:
        if enemy.hp <= 0:
            continue
        shot = getattr(enemy, "pending_shot", None)
        if shot:
            x, y, dx, dy, damage, color, size = shot
            enemy_bullets.append(EnemyBullet(x, y, dx, dy, damage, color, size))
            enemy.pending_shot = None
        for ring_shot in getattr(enemy, "pending_ring", []):
            x, y, dx, dy, damage, color, size = ring_shot
            enemy_bullets.append(EnemyBullet(x, y, dx, dy, damage, color, size, speed=3.6))
        if getattr(enemy, "pending_burst", False):
            faire_attaque_zone_ennemi(enemy.rect.centerx, enemy.rect.centery, player, warning_circles, 80, 8)
            enemy.pending_burst = False


#ca prend le niveau et l'ecran, ca affiche le petit ecran avant de commencer et ca ne renvoie rien
def afficher_entree_niveau(level, screen, width, height, get_medieval_font):
    overlay = pygame.Surface((width, height))
    overlay.fill((10, 5, 20))
    title = get_medieval_font(64).render(f"Niveau {level}", True, (200, 130, 255))
    subtitle = get_medieval_font(28).render("Prepare-toi...", True, (180, 180, 180))
    for alpha in range(0, 256, 8):
        dessiner_fondu_niveau(screen, overlay, title, subtitle, width, height, alpha)
    pygame.time.delay(1200)
    for alpha in range(255, -1, -8):
        dessiner_fondu_niveau(screen, overlay, title, subtitle, width, height, alpha)


#ca prend les textes du niveau et l'alpha, ca dessine juste une image du fondu sur l'ecran
def dessiner_fondu_niveau(screen, overlay, title, subtitle, width, height, alpha):
    overlay.set_alpha(alpha)
    screen.blit(overlay, (0, 0))
    screen.blit(title, (width // 2 - title.get_width() // 2, height // 2 - 60))
    screen.blit(subtitle, (width // 2 - subtitle.get_width() // 2, height // 2 + 20))
    pygame.display.flip()
    pygame.time.delay(16)


WEAPON_LABELS = {"sword": "Epee : attaque courte", "crossbow": "Arbalete : tir penetrant",
                 "bow": "Arc : tire et propulse", "magic_wand": "Baguette : explosif de zone",
                 "damage_boost": "Degats augmentes", "speed_boost": "Vitesse augmentee",
                 "range_boost": "Portee augmentee", "heart": "Soin recupere",
                 "armor": "Armure : +50 HP"}
ITEM_LABELS = {"heart": "Coeur recupere", "speed": "Vitesse augmentee"}


def random_boost_reward(player):
    weapons = ["sword", "crossbow", "bow", "magic_wand"]
    missing_weapons = [w for w in weapons if w not in player.weapons]
    if missing_weapons and len(player.weapons) < 2:
        return missing_weapons[0]
    return random_choice_boost()


def random_choice_boost():
    import random
    return random.choice(["heart", "heart", "damage_boost", "speed_boost", "range_boost"])


def open_chests(player, room, particles):
    message, timer = "", 0
    chests = []
    if room.chest:
        chests.append(room.chest)
    chests += room.reward_chests
    for chest in chests:
        if chest.opened:
            continue
        if player.rect.colliderect(chest.rect):
            chest.open_timer += 1
            if chest.open_timer >= 15:
                reward = chest.open()
                if reward in player.weapons:
                    reward = random_boost_reward(player)
                player.apply_item(reward)
                message, timer = WEAPON_LABELS.get(reward, reward), 180
                particles.emit_sparks(chest.rect.centerx, chest.rect.centery, count=14, color=(255, 220, 80))
                particles.emit_magic(chest.rect.centerx, chest.rect.centery, count=8, color=(200, 160, 60))
        else:
            chest.open_timer = 0
    return message, timer


def collect_items(player, room, particles):
    for item in room.items[:]:
        if player.rect.colliderect(item.rect) and player.apply_item(item.type):
            room.items.remove(item)
            particles.emit_magic(item.rect.centerx, item.rect.centery, count=10, color=(120, 220, 120))
            return ITEM_LABELS.get(item.type, item.type), 120
    return "", 0


def player_touch_enemies(player, room, contact_damage):
    for enemy in room.enemies:
        if enemy.hp > 0 and player.rect.colliderect(enemy.rect):
            player.take_damage(getattr(enemy, "touch_damage", contact_damage))


def show_game_over(screen, game_surface, current_bg, fonts, colors, score, width, height):
    font_game_over, font_restart = fonts
    red, white, black = colors
    for alpha in range(0, 256, 12):
        game_surface.set_alpha(255 - alpha)
        screen.fill(black)
        screen.blit(game_surface, (0, 0))
        pygame.display.flip()
        pygame.time.delay(16)
    game_surface.set_alpha(255)
    game_surface.fill(black)
    game_surface.blit(current_bg, (0, 0))
    go_surf = font_game_over.render("GAME OVER", True, red)
    rs_surf = font_restart.render("Appuie sur ECHAP pour quitter", True, white)
    sc_surf = font_restart.render(f"Score final : {score}", True, (255, 230, 120))
    game_surface.blit(go_surf, go_surf.get_rect(center=(width // 2, height // 2 - 60)))
    game_surface.blit(sc_surf, sc_surf.get_rect(center=(width // 2, height // 2 + 10)))
    game_surface.blit(rs_surf, rs_surf.get_rect(center=(width // 2, height // 2 + 50)))
    screen.blit(game_surface, (0, 0))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False
    return False


def draw_frame(game_surface, screen, game_map, assets, particles, player, hud_data,
               bullets, enemy_bullets, explosions, warning_circles, lighting,
               extra_lights, portal_light, shake, fade, black):
    draw_extra_hud = hud_data[0]
    score, pickup_message, pickup_timer, font_hud, font_message, width = hud_data[1:]
    game_map.draw(game_surface, assets, show_minimap=False)
    particles.update()
    particles.draw(game_surface)
    player.draw_hp_bar(game_surface)
    player.draw_inventory(game_surface, assets)
    draw_extra_hud(game_surface, player, game_map, score, pickup_message,
                   pickup_timer, font_hud, font_message, width)
    player.draw()
    for bullet in bullets:
        bullet.draw(game_surface)
    for enemy_bullet in enemy_bullets:
        enemy_bullet.draw(game_surface)
    for explosion in explosions[:]:
        explosion.update()
        explosion.draw(game_surface)
        if explosion.timer <= 0:
            explosions.remove(explosion)
    for warning in warning_circles[:]:
        x, y, radius, timer = warning
        pygame.draw.circle(game_surface, (255, 80, 80), (x, y), radius, 2)
        warning[3] -= 1
        if warning[3] <= 0:
            warning_circles.remove(warning)
    all_extra = extra_lights + portal_light
    lighting.draw(game_surface, player, all_extra if all_extra else None)
    game_map.dessiner_mini_carte(game_surface)
    screen.fill(black)
    sw, sh = screen.get_size()
    scale = min(sw / 800, sh / 600)
    scaled_w, scaled_h = int(800 * scale), int(600 * scale)
    scaled = pygame.transform.scale(game_surface, (scaled_w, scaled_h))
    shake_x, shake_y = shake.decalage_ecran()
    ox = (sw - scaled_w) // 2 + shake_x
    oy = (sh - scaled_h) // 2 + shake_y
    screen.blit(scaled, (ox, oy))
    fade.update()
    fade.draw(screen)
    pygame.display.flip()

