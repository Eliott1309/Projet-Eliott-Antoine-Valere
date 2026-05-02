import pygame
import sys
import os
from map import Map, SCREEN_HEIGHT, SCREEN_WIDTH

base = os.path.dirname(os.path.abspath(__file__))
MEDIEVAL_FONT_PATH = os.path.join(base, "assets", "medieval.ttf")

def get_medieval_font(size):
    try:
        return pygame.font.Font(MEDIEVAL_FONT_PATH, size)
    except:
        return pygame.font.Font(None, size)


def draw_dialog_box(screen, text, width, height, text_index):
    box_width = 720
    box_height = 120
    x = (width - box_width) // 2
    y = height - box_height - 30

    pygame.draw.rect(screen, (110, 0, 0),    (x-8, y-8, box_width+16, box_height+16))
    pygame.draw.rect(screen, (230, 70, 20),  (x-3, y-3, box_width+6,  box_height+6))
    pygame.draw.rect(screen, (245, 230, 190),(x,   y,   box_width,    box_height))

    font = get_medieval_font(24)
    visible_text = text[:text_index]
    words = visible_text.split(" ")
    lines, current_line = [], ""

    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] < box_width - 50:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)

    for i, line in enumerate(lines[:3]):
        text_surface = font.render(line, True, (120, 20, 20))
        screen.blit(text_surface, (x + 30, y + 30 + i * 28))

    small_font = get_medieval_font(18)
    continue_text = small_font.render("Appuyer sur espace pour continuer", True, (120, 20, 20))
    continue_rect = continue_text.get_rect(center=(width//2, y + box_height - 18))
    screen.blit(continue_text, continue_rect)


def lancer_jeu(keyboard_layout="azerty", assets=None):
    pygame.init()

    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mini Isaac")

    clock = pygame.time.Clock()

    font_game_over = get_medieval_font(80)
    font_restart   = get_medieval_font(32)
    font_hud       = get_medieval_font(24)
    font_message   = get_medieval_font(30)

    WHITE = (255, 255, 255)
    RED   = (200,  50,  50)
    BLACK = (0,    0,    0)

    # ──────────────────────────────────────────────────────────────
    def draw_extra_hud(surface, player, game_map, score, pickup_message, pickup_message_timer):
        enemies_left = sum(1 for e in game_map.current_room.enemies if e.hp > 0)
        weapon_names = {None:"Aucune","sword":"Epee","crossbow":"Arbalete",
                        "bow":"Arc","magic_wand":"Baguette"}

        surface.blit(font_hud.render("Score : " + str(score), True, WHITE), (10, 38))
        surface.blit(font_hud.render("Arme : " + weapon_names[player.weapon], True, WHITE), (10, 66))
        surface.blit(font_hud.render("Ennemis restants : " + str(enemies_left), True, WHITE), (10, 94))
        surface.blit(font_hud.render("Niveau : " + str(game_map.level), True, (200, 130, 255)), (10, 122))

        if pickup_message_timer > 0:
            msg_surf = font_message.render(pickup_message, True, (255, 230, 120))
            surface.blit(msg_surf, (WIDTH//2 - msg_surf.get_width()//2, 45))

    # ──────────────────────────────────────────────────────────────
    class Player:
        def __init__(self):
            self.rect = pygame.Rect(400, 300, 40, 40)
            self.speed = 5
            self.hp = 5
            self.max_hp = 5
            self.invincible_timer = 0
            self.inventory = []
            self.weapon = None
            self.weapons = []
            self.selected_weapon_index = 0
            self.damage_boost = 0
            self.range_boost  = 0
            self.attack_rect  = None
            self.attack_timer = 0
            self.attack_direction = None
            self.footstep_timer   = 0
            self.footstep_channel = None

        def take_damage(self, amount=1):
            if self.invincible_timer == 0:
                self.hp -= amount
                self.invincible_timer = 60

        def is_alive(self):
            return self.hp > 0

        def add_weapon(self, weapon_type):
            if weapon_type not in self.weapons:
                self.weapons.append(weapon_type)
            self.weapon = weapon_type
            self.selected_weapon_index = self.weapons.index(weapon_type)

        def switch_weapon(self):
            if not self.weapons:
                return
            self.selected_weapon_index = (self.selected_weapon_index + 1) % len(self.weapons)
            self.weapon = self.weapons[self.selected_weapon_index]

        def apply_item(self, item_type):
            if item_type == "heart":
                if self.hp < self.max_hp:   self.hp = min(self.max_hp, self.hp+1); return True
                elif len(self.inventory)<5: self.inventory.append("heart");        return True
                return False
            boosts = {"speed":("speed",0.5),"damage_boost":("damage_boost",1),
                      "speed_boost":("speed",0.75),"range_boost":("range_boost",80)}
            if item_type in boosts:
                attr, val = boosts[item_type]; setattr(self, attr, getattr(self, attr)+val); return True
            if item_type in ["sword","crossbow","bow","magic_wand"]:
                self.add_weapon(item_type); return True

        def use_inventory_item(self, index):
            if index < len(self.inventory) and self.inventory[index]=="heart" and self.hp < self.max_hp:
                self.hp = min(self.max_hp, self.hp+1); self.inventory.pop(index)

        def draw_hp_bar(self, surface):
            for i in range(self.max_hp):
                x = 10 + i * 24
                color = (220,50,50) if i < self.hp else (80,80,80)
                pygame.draw.rect(surface, color,        (x, 10, 20, 20), border_radius=4)
                pygame.draw.rect(surface, (255,255,255),(x, 10, 20, 20), 1, border_radius=4)

        def move(self, keys, game_map):
            if self.invincible_timer > 0:
                self.invincible_timer -= 1
            dx, dy = 0, 0

            left_key = pygame.K_q if keyboard_layout == "azerty" else pygame.K_a
            up_key   = pygame.K_z if keyboard_layout == "azerty" else pygame.K_w

            if keys[left_key]:       dx -= 1
            if keys[pygame.K_d]:     dx += 1
            if keys[up_key]:         dy -= 1
            if keys[pygame.K_s]:     dy += 1

            if dx != 0 or dy != 0:
                if self.footstep_channel is None or not self.footstep_channel.get_busy():
                    self.footstep_channel = assets["footstep"].play()
            else:
                if self.footstep_channel is not None:
                    self.footstep_channel.stop()
                    self.footstep_channel = None

            if dx != 0 and dy != 0:
                dx *= 0.7071; dy *= 0.7071

            self.rect.x += dx * self.speed
            self._resolve_collisions(game_map, "x")
            self.rect.y += dy * self.speed
            self._resolve_collisions(game_map, "y")

        def _resolve_collisions(self, game_map, axis):
            current_room = game_map.current_room
            for wall_rect in current_room.get_wall_rects():
                if self.rect.colliderect(wall_rect):
                    if axis == "x":
                        if self.rect.centerx < wall_rect.centerx: self.rect.right = wall_rect.left
                        else:                                       self.rect.left  = wall_rect.right
                    else:
                        if self.rect.centery < wall_rect.centery: self.rect.bottom = wall_rect.top
                        else:                                      self.rect.top    = wall_rect.bottom

            for direction, door_rect in current_room.get_door_rects().items():
                if self.rect.colliderect(door_rect):
                    if current_room.cleared:
                        dx, dy = current_room.door_directions[direction]
                        game_map.change_room(dx, dy, self)
                        return
                    else:
                        if axis == "x":
                            if self.rect.centerx < door_rect.centerx: self.rect.right = door_rect.left
                            else:                                       self.rect.left  = door_rect.right
                        else:
                            if self.rect.centery < door_rect.centery: self.rect.bottom = door_rect.top
                            else:                                      self.rect.top    = door_rect.bottom

        def draw(self):
            screen.blit(assets["player"], self.rect)
            if self.attack_timer > 0 and self.attack_rect is not None:
                slash = pygame.Surface((70, 70), pygame.SRCALPHA)
                color = (240, 240, 255, 180)
                if self.attack_direction == (1,  0): pygame.draw.arc(slash, color, (10,10,50,50), -1.2, 1.2, 4); screen.blit(slash, (self.rect.right-20, self.rect.centery-35))
                elif self.attack_direction == (-1, 0): pygame.draw.arc(slash, color, (10,10,50,50), 1.9, 4.4, 4); screen.blit(slash, (self.rect.left-50,  self.rect.centery-35))
                elif self.attack_direction == (0, -1): pygame.draw.arc(slash, color, (10,10,50,50), 0.3, 2.8, 4); screen.blit(slash, (self.rect.centerx-35, self.rect.top-50))
                elif self.attack_direction == (0,  1): pygame.draw.arc(slash, color, (10,10,50,50), 3.4, 5.9, 4); screen.blit(slash, (self.rect.centerx-35, self.rect.bottom-20))

        def draw_inventory(self, surface, assets):
            slot_size, spacing, slots = 30, 5, 5
            start_x, y = 10, 562
            for i in range(slots):
                x = start_x + i * (slot_size + spacing)
                slot_rect = pygame.Rect(x, y, slot_size, slot_size)
                pygame.draw.rect(surface, (40,40,45),      slot_rect, border_radius=6)
                pygame.draw.rect(surface, (220,220,220),   slot_rect, 2, border_radius=6)
                if i == 0 and self.weapon is not None:
                    if self.weapon in assets:
                        surface.blit(assets[self.weapon], slot_rect)
                    else:
                        ltr = pygame.font.Font(None, 22).render(self.weapon[0].upper(), True, (255,255,255))
                        surface.blit(ltr, ltr.get_rect(center=slot_rect.center))
                item_index = i - 1
                if i > 0 and item_index < len(self.inventory):
                    if self.inventory[item_index] == "heart":
                        pygame.draw.rect(surface, (220,40,70),
                                         pygame.Rect(x+8, y+8, slot_size-16, slot_size-16), border_radius=6)

        def sword_attack(self, dx, dy, enemies):
            self.attack_direction = (dx, dy)
            attack_size = 45 + self.range_boost // 4
            if dx == 1:   self.attack_rect = pygame.Rect(self.rect.right,          self.rect.centery-15, attack_size, 30)
            elif dx == -1: self.attack_rect = pygame.Rect(self.rect.left-attack_size, self.rect.centery-15, attack_size, 30)
            elif dy == 1:  self.attack_rect = pygame.Rect(self.rect.centerx-15, self.rect.bottom,          30, attack_size)
            elif dy == -1: self.attack_rect = pygame.Rect(self.rect.centerx-15, self.rect.top-attack_size, 30, attack_size)
            self.attack_timer = 6
            for enemy in enemies:
                if enemy.hp > 0 and self.attack_rect.colliderect(enemy.rect):
                    enemy.hp -= 1 + self.damage_boost
                    enemy.rect.x += dx * 25
                    enemy.rect.y += dy * 25

    # ──────────────────────────────────────────────────────────────
    class Bullet:
        def __init__(self, x, y, dx, dy, damage=1, max_distance=800,
                     color=WHITE, size=10, pierce=1, magic=False):
            self.rect = pygame.Rect(x, y, size, size)
            self.dx, self.dy = dx, dy
            self.speed = 8
            self.damage = damage
            self.max_distance = max_distance
            self.distance_travelled = 0
            self.color = color
            self.pierce = pierce
            self.magic  = magic
            self.hit_enemies = set()

        def update(self):
            self.rect.x += self.dx * self.speed
            self.rect.y += self.dy * self.speed
            self.distance_travelled += self.speed

        def draw(self):
            pygame.draw.rect(screen, self.color, self.rect)

    class Explosion:
        def __init__(self, x, y):
            self.x, self.y = x, y
            self.radius = 55
            self.timer  = 12

        def update(self): self.timer -= 1

        def draw(self):
            pygame.draw.circle(screen, (170, 90, 255), (self.x, self.y), self.radius, 3)

    # ──────────────────────────────────────────────────────────────
    #  State
    # ──────────────────────────────────────────────────────────────
    player = Player()
    bullets, explosions = [], []

    current_level = 1
    game_map = Map(level=current_level)

    score = 0
    counted_dead_enemies = set()
    pickup_message       = ""
    pickup_message_timer = 0

    quest_transition  = False
    quest_text_index  = 0
    quest_message     = ("Vous devez sauver la princesse. Tuez d'abord les ennemis "
                         "dans les salles environnantes avant de pouvoir la retrouver.")
    typewriter_channel = None
    shoot_cooldown = 0
    running = True

    # ──────────────────────────────────────────────────────────────
    def add_score_for_dead_enemies():
        nonlocal score
        for enemy in game_map.current_room.enemies:
            if enemy.hp <= 0 and id(enemy) not in counted_dead_enemies:
                counted_dead_enemies.add(id(enemy))
                score += 100

    def create_magic_explosion(x, y):
        explosions.append(Explosion(x, y))
        explosion_rect = pygame.Rect(x-55, y-55, 110, 110)
        for enemy in game_map.current_room.enemies:
            if enemy.hp > 0 and explosion_rect.colliderect(enemy.rect):
                enemy.hp -= 2 + player.damage_boost

    def show_level_transition(level):
        screen.fill((10, 5, 20))
        t = get_medieval_font(64).render(f"Niveau  {level}", True, (200, 130, 255))
        s = get_medieval_font(28).render("Prépare-toi...", True, (180, 180, 180))
        screen.blit(t, (WIDTH//2 - t.get_width()//2, HEIGHT//2 - 60))
        screen.blit(s, (WIDTH//2 - s.get_width()//2, HEIGHT//2 + 20))
        pygame.display.flip()
        pygame.time.delay(2000)

    # ──────────────────────────────────────────────────────────────
    #  Boucle principale
    # ──────────────────────────────────────────────────────────────
    while running:
        clock.tick(60)
        screen.fill(BLACK)
        keys = pygame.key.get_pressed()

        if pickup_message_timer > 0:
            pickup_message_timer -= 1

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

                if event.key == pygame.K_1: player.switch_weapon()
                elif event.key == pygame.K_2: player.use_inventory_item(0)
                elif event.key == pygame.K_3: player.use_inventory_item(1)
                elif event.key == pygame.K_4: player.use_inventory_item(2)
                elif event.key == pygame.K_5: player.use_inventory_item(3)

        # ── Boîte de dialogue intro ──────────────────────────────
        if quest_transition:
            if quest_text_index < len(quest_message):
                quest_text_index += 1
                if typewriter_channel is None or not typewriter_channel.get_busy():
                    typewriter_channel = assets["typewriter"].play()
            else:
                if typewriter_channel: typewriter_channel.stop(); typewriter_channel = None
            draw_dialog_box(screen, quest_message, WIDTH, HEIGHT, quest_text_index)
            pygame.display.flip()
            continue

        # ── Mouvement joueur ─────────────────────────────────────
        old_pos = game_map.current_pos
        player.move(keys, game_map)
        if current_level == 1 and old_pos == (0, 0) and game_map.current_pos != (0, 0):
            quest_transition = True
            quest_text_index = 0

        # ── Attaque ──────────────────────────────────────────────
        if player.attack_timer > 0:
            player.attack_timer -= 1
        if shoot_cooldown > 0:
            shoot_cooldown -= 1

        if shoot_cooldown == 0:
            dx, dy = 0, 0
            if keys[pygame.K_i]: dx, dy = 0, -1
            elif keys[pygame.K_k]: dx, dy = 0,  1
            elif keys[pygame.K_j]: dx, dy = -1, 0
            elif keys[pygame.K_l]: dx, dy =  1, 0

            if player.weapon and (dx != 0 or dy != 0):
                if player.weapon == "sword":
                    player.sword_attack(dx, dy, game_map.current_room.enemies)
                    shoot_cooldown = 15

                elif player.weapon == "crossbow":
                    bullets.append(Bullet(player.rect.centerx, player.rect.centery, dx, dy,
                                          3+player.damage_boost, 800+player.range_boost,
                                          (230,230,230), 10, pierce=3))
                    shoot_cooldown = 75

                elif player.weapon == "bow":
                    bullets.append(Bullet(player.rect.centerx, player.rect.centery, dx, dy,
                                          1+player.damage_boost, 500+player.range_boost,
                                          (120,220,120), 8))
                    player.rect.x -= dx * 35; player._resolve_collisions(game_map, "x")
                    player.rect.y -= dy * 35; player._resolve_collisions(game_map, "y")
                    shoot_cooldown = 18

                elif player.weapon == "magic_wand":
                    bullets.append(Bullet(player.rect.centerx, player.rect.centery, dx, dy,
                                          1+player.damage_boost, 650+player.range_boost,
                                          (160,90,255), 14, pierce=1, magic=True))
                    shoot_cooldown = 45

        # ── Balles ───────────────────────────────────────────────
        wall_rects = game_map.current_room.get_wall_rects()
        for bullet in bullets[:]:
            bullet.update()
            if not screen.get_rect().colliderect(bullet.rect):
                bullets.remove(bullet); continue
            if bullet.distance_travelled >= bullet.max_distance:
                bullets.remove(bullet); continue
            hit_wall = any(bullet.rect.colliderect(w) for w in wall_rects)
            if hit_wall:
                if bullet.magic: create_magic_explosion(bullet.rect.centerx, bullet.rect.centery)
                bullets.remove(bullet); continue
            for enemy in game_map.current_room.enemies:
                if enemy.hp > 0 and bullet.rect.colliderect(enemy.rect) and id(enemy) not in bullet.hit_enemies:
                    enemy.hp -= bullet.damage
                    bullet.hit_enemies.add(id(enemy))
                    if bullet.magic:
                        create_magic_explosion(bullet.rect.centerx, bullet.rect.centery)
                        if bullet in bullets: bullets.remove(bullet)
                        break
                    bullet.pierce -= 1
                    if bullet.pierce <= 0:
                        if bullet in bullets: bullets.remove(bullet)
                        break

        add_score_for_dead_enemies()

        # ── Update map (ennemis, portail) ─────────────────────────
        game_map.update(player)

        # ── Passage au niveau suivant ─────────────────────────────
        if game_map.next_level_triggered:
            current_level += 1
            show_level_transition(current_level)
            game_map = Map(level=current_level)
            bullets.clear()
            explosions.clear()
            player.rect.center = (WIDTH//2, HEIGHT//2)
            score += current_level * 500
            pickup_message       = f"Niveau {current_level} — Bonne chance !"
            pickup_message_timer = 180

        # ── Coffres ───────────────────────────────────────────────
        WEAPON_LABELS = {"sword":"Epee : attaque courte","crossbow":"Arbalete : tir pénétrant",
                         "bow":"Arc : tire et propulse","magic_wand":"Baguette : explosif de zone",
                         "damage_boost":"Dégâts augmentés","speed_boost":"Vitesse augmentée",
                         "range_boost":"Portée augmentée"}

        def try_open_chest(chest):
            nonlocal pickup_message, pickup_message_timer
            if chest.opened: return
            if player.rect.colliderect(chest.rect):
                chest.open_timer += 1
                if chest.open_timer >= 15:
                    reward = chest.open()
                    player.apply_item(reward)
                    pickup_message, pickup_message_timer = WEAPON_LABELS.get(reward, reward), 180
            else:
                chest.open_timer = 0

        if game_map.current_room.chest:
            try_open_chest(game_map.current_room.chest)
        for rc in game_map.current_room.reward_chests:
            try_open_chest(rc)

        # ── Items au sol ──────────────────────────────────────────
        ITEM_LABELS = {"heart":"Coeur récupéré","speed":"Vitesse augmentée"}
        for item in game_map.current_room.items[:]:
            if player.rect.colliderect(item.rect) and player.apply_item(item.type):
                game_map.current_room.items.remove(item)
                pickup_message, pickup_message_timer = ITEM_LABELS.get(item.type, item.type), 120

        # ── Collisions joueur / ennemis ───────────────────────────
        for enemy in game_map.current_room.enemies:
            if enemy.hp > 0 and player.rect.colliderect(enemy.rect):
                player.take_damage(1)

        # ── Game Over ─────────────────────────────────────────────
        if not player.is_alive():
            screen.fill(BLACK)
            go_surf = font_game_over.render("GAME OVER", True, RED)
            rs_surf = font_restart.render("Appuie sur ECHAP pour quitter", True, WHITE)
            sc_surf = font_restart.render(f"Score final : {score}", True, (255, 230, 120))
            screen.blit(go_surf, go_surf.get_rect(center=(WIDTH//2, HEIGHT//2 - 60)))
            screen.blit(go_surf, go_surf.get_rect(center=(WIDTH//2, HEIGHT//2 - 60)))
            screen.blit(sc_surf, sc_surf.get_rect(center=(WIDTH//2, HEIGHT//2 + 10)))
            screen.blit(rs_surf, rs_surf.get_rect(center=(WIDTH//2, HEIGHT//2 + 50)))
            pygame.display.flip()
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:              waiting = running = False
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        waiting = running = False
            continue

        # ── Rendu ─────────────────────────────────────────────────
        game_map.draw(screen, assets)
        player.draw_hp_bar(screen)
        player.draw_inventory(screen, assets)
        draw_extra_hud(screen, player, game_map, score, pickup_message, pickup_message_timer)
        player.draw()
        for bullet in bullets: bullet.draw()
        for explosion in explosions[:]:
            explosion.update(); explosion.draw()
            if explosion.timer <= 0: explosions.remove(explosion)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    lancer_jeu()