import random
import pygame

WIDTH = 800
HEIGHT = 600
PLAYER_MAX_HP = 100
HEART_HEAL = 30


class Player:
    def __init__(self, keyboard_layout, assets, game_surface, font_hud, particles, shake, fade):
        self.rect = pygame.Rect(400, 300, 40, 40)
        self.speed = 5
        self.hp = PLAYER_MAX_HP
        self.max_hp = PLAYER_MAX_HP
        self.invincible_timer  = 0
        self.transition_lock   = 0
        self.inventory = []
        self.weapon = None
        self.weapons = []
        self.selected_weapon_index = 0
        self.damage_boost = 0
        self.armor_hp = 0
        self.max_armor_hp = 50
        self.has_armor = False
        self.range_boost  = 0
        self.attack_rect  = None
        self.last_direction = (1, 0)
        self.attack_timer = 0
        self.attack_direction = None
        self.footstep_timer   = 0
        self.footstep_channel = None
        self._prev_hp = PLAYER_MAX_HP
        self.keyboard_layout = keyboard_layout
        self.assets = assets
        self.game_surface = game_surface
        self.font_hud = font_hud
        self.particles = particles
        self.shake = shake
        self.fade = fade

    def take_damage(self, amount=1):
        if self.invincible_timer == 0:
            if self.has_armor and self.armor_hp > 0:
                self.armor_hp -= amount
                if self.armor_hp <= 0:
                    self.armor_hp = 0
                self.particles.emit_sparks(
                    self.rect.centerx, self.rect.centery,
                    count=6, color=(80, 160, 255)
                )
            else:
                self.hp = max(0, self.hp - amount)
                self.shake.trigger(intensity=7, duration=12)
                self.particles.emit_sparks(
                    self.rect.centerx, self.rect.centery,
                    count=8, color=(220, 40, 40)
                )
            self.invincible_timer = 45

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
            if self.hp < self.max_hp:   self.hp = min(self.max_hp, self.hp+HEART_HEAL); return True
            elif len(self.inventory)<5: self.inventory.append("heart");        return True
            return False
        boosts = {"speed":("speed",0.5),"damage_boost":("damage_boost",1),
            "speed_boost":("speed",0.75),"range_boost":("range_boost",150)}
        if item_type in boosts:
            attr, val = boosts[item_type]
            setattr(self, attr, getattr(self, attr) + val)
            if attr == "speed":
                self.speed = min(self.speed, 7)
            return True
        if item_type in ["sword","crossbow","bow","magic_wand"]:
            self.add_weapon(item_type); return True
        if item_type == "armor":
            if not self.has_armor:
                self.has_armor = True
                self.armor_hp = self.max_armor_hp
            else:
                self.armor_hp = min(self.max_armor_hp, self.armor_hp + 25)
            return True
    def use_inventory_item(self, index):
        if index < len(self.inventory) and self.inventory[index]=="heart" and self.hp < self.max_hp:
            self.hp = min(self.max_hp, self.hp+HEART_HEAL); self.inventory.pop(index)

    def draw_hp_bar(self, surface):
        bar_x, bar_y = 10, 10
        bar_w, bar_h = 210, 20
        ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surface, (55, 20, 25), (bar_x, bar_y, bar_w, bar_h), border_radius=6)
        pygame.draw.rect(surface, (220, 45, 55), (bar_x, bar_y, int(bar_w * ratio), bar_h), border_radius=6)
        pygame.draw.rect(surface, (255,255,255), (bar_x, bar_y, bar_w, bar_h), 2, border_radius=6)
        hp_text = self.font_hud.render(str(int(self.hp)) + " / " + str(self.max_hp), True, (255, 255, 255))
        surface.blit(hp_text, (bar_x + bar_w + 8, bar_y - 2))
        #barre armure
        if self.has_armor:
            armor_y = bar_y + bar_h + 4
            armor_ratio = max(0, self.armor_hp / self.max_armor_hp)
            pygame.draw.rect(surface, (20, 40, 80), (bar_x, armor_y, bar_w, bar_h), border_radius=6)
            pygame.draw.rect(surface, (60, 140, 255), (bar_x, armor_y, int(bar_w * armor_ratio), bar_h), border_radius=6)
            pygame.draw.rect(surface, (180, 210, 255), (bar_x, armor_y, bar_w, bar_h), 2, border_radius=6)
            armor_text = self.font_hud.render(str(int(self.armor_hp)) + " / " + str(self.max_armor_hp), True, (180, 210, 255))
            surface.blit(armor_text, (bar_x + bar_w + 8, armor_y - 2))

    def move(self, keys, game_map):
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        if self.transition_lock > 0:
            self.transition_lock -= 1
        dx, dy = 0, 0

        left_key = pygame.K_q if self.keyboard_layout == "azerty" else pygame.K_a
        up_key   = pygame.K_z if self.keyboard_layout == "azerty" else pygame.K_w

        if keys[left_key]:       dx -= 1
        if keys[pygame.K_d]:     dx += 1
        if keys[up_key]:         dy -= 1
        if keys[pygame.K_s]:     dy += 1

        moving = (dx != 0 or dy != 0)
        
        if moving:
            if abs(dx) > abs(dy):
                self.last_direction = (1, 0) if dx > 0 else (-1, 0)
            else:
                self.last_direction = (0, 1) if dy > 0 else (0, -1)

        if moving:
            if self.footstep_channel is None or not self.footstep_channel.get_busy():
                self.footstep_channel = self.assets["footstep"].play()
            if random.random() < 0.25:
                self.particles.emit_dust(
                    self.rect.centerx + random.randint(-8, 8),
                    self.rect.bottom
                )
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
        self.keep_inside_screen()

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

        if self.transition_lock > 0:
            return

        for direction, door_rect in current_room.get_door_rects().items():
            if self.rect.colliderect(door_rect):
                if current_room.cleared:
                    dx, dy = current_room.door_directions[direction]
                    _dx, _dy = dx, dy
                    def do_change():
                        game_map.change_room(_dx, _dy, self)
                    self.fade.start(callback=do_change)
                    return
                else:
                    if axis == "x":
                        if self.rect.centerx < door_rect.centerx: self.rect.right = door_rect.left
                        else:                                       self.rect.left  = door_rect.right
                    else:
                        if self.rect.centery < door_rect.centery: self.rect.bottom = door_rect.top
                        else:                                      self.rect.top    = door_rect.bottom

    def keep_inside_screen(self):
        if self.rect.left < 0:   self.rect.left = 0
        if self.rect.right > WIDTH:  self.rect.right = WIDTH
        if self.rect.top < 0:    self.rect.top = 0
        if self.rect.bottom > HEIGHT: self.rect.bottom = HEIGHT

    #dessine l'arme equipee dans la main du joueur
    def draw_weapon_in_hand(self):
        if self.weapon is None:
            return
        if self.weapon not in self.assets:
            return

        weapon_image = self.assets[self.weapon]
        direction = self.attack_direction if self.attack_timer > 0 else self.last_direction

        weapon_sizes = {
            "sword": 28,
            "crossbow": 24,
            "bow": 26,
            "magic_wand": 24
        }

        size = weapon_sizes.get(self.weapon, 24)


        weapon_image = pygame.transform.smoothscale(weapon_image, (size, size))

        if self.weapon == "sword":
            pos = (self.rect.right - 5, self.rect.centery - size//2)
            weapon_rect = weapon_image.get_rect(center=(pos[0] + size//2, pos[1] + size//2))
            self.game_surface.blit(weapon_image, weapon_rect)
            return


        dx, dy = direction

        if dx == 1:
            angle = 0
            pos = (self.rect.right - 5, self.rect.centery - size//2)
        elif dx == -1:
            angle = 180
            pos = (self.rect.left - size + 5, self.rect.centery - size//2)
        elif dy == -1:
            angle = 90
            pos = (self.rect.centerx - size//2, self.rect.top - size + 8)
        else:
            angle = -90
            pos = (self.rect.centerx - size//2, self.rect.bottom - 8)

        if self.weapon == "crossbow":
            angle += 180

        if self.weapon == "magic_wand":
            if dx == 1:
                angle = -90
            elif dx == -1:
                angle = 90
            elif dy == -1:
                angle = 0
            else:
                angle = 180


        weapon_image = pygame.transform.rotate(weapon_image, angle)
        weapon_rect = weapon_image.get_rect(center=(pos[0] + size//2, pos[1] + size//2))
        self.game_surface.blit(weapon_image, weapon_rect)


    def draw(self):
        pulse = 2 if pygame.time.get_ticks() // 220 % 2 == 0 else 0
        draw_rect = self.rect.inflate(pulse, pulse)
        anim_key = "player_armor_anim" if self.has_armor and self.armor_hp > 0 and "player_armor_anim" in self.assets else "player_anim"
        frames = self.assets.get(anim_key, [self.assets["player"]])
        frame = frames[pygame.time.get_ticks() // 180 % len(frames)]

        # Clignotement rouge quand invincible
        if self.invincible_timer > 0 and (self.invincible_timer // 4) % 2 == 0:
            tinted = frame.copy()
            tinted.fill((255, 80, 80, 160), special_flags=pygame.BLEND_RGBA_MULT)
            self.game_surface.blit(tinted, draw_rect)
        else:
            self.game_surface.blit(frame, draw_rect)
        self.draw_weapon_in_hand()


        if self.attack_timer > 0 and self.attack_rect is not None:
            slash = pygame.Surface((70, 70), pygame.SRCALPHA)
            color = (240, 240, 255, 180)
            if self.attack_direction == (1,  0): pygame.draw.arc(slash, color, (10,10,50,50), -1.2, 1.2, 4); self.game_surface.blit(slash, (self.rect.right-20, self.rect.centery-35))
            elif self.attack_direction == (-1, 0): pygame.draw.arc(slash, color, (10,10,50,50), 1.9, 4.4, 4); self.game_surface.blit(slash, (self.rect.left-50,  self.rect.centery-35))
            elif self.attack_direction == (0, -1): pygame.draw.arc(slash, color, (10,10,50,50), 0.3, 2.8, 4); self.game_surface.blit(slash, (self.rect.centerx-35, self.rect.top-50))
            elif self.attack_direction == (0,  1): pygame.draw.arc(slash, color, (10,10,50,50), 3.4, 5.9, 4); self.game_surface.blit(slash, (self.rect.centerx-35, self.rect.bottom-20))

    def draw_inventory(self, surface, assets):
        slot_size, spacing = 30, 5
        bottom_y = HEIGHT - 10  # ancrage bas de l'écran

        #colonne armes 
        weapon_x = 10
        for i, weapon in enumerate(self.weapons):
            y = bottom_y - (i + 1) * (slot_size + spacing)
            slot_rect = pygame.Rect(weapon_x, y, slot_size, slot_size)

            pygame.draw.rect(surface, (40, 40, 45), slot_rect, border_radius=6)
            border_color = (255, 230, 120) if weapon == self.weapon else (220, 220, 220)
            pygame.draw.rect(surface, border_color, slot_rect, 2, border_radius=6)

            if weapon in self.assets:
                surface.blit(self.assets[weapon], slot_rect)
            else:
                ltr = pygame.font.Font(None, 22).render(weapon[0].upper(), True, (255, 255, 255))
                surface.blit(ltr, ltr.get_rect(center=slot_rect.center))

        #colonne soins 
        heal_x = WIDTH - slot_size - 10
        heal_items = [item for item in self.inventory if item == "heart"]
        for i, item in enumerate(heal_items):
            y = bottom_y - (i + 1) * (slot_size + spacing)
            slot_rect = pygame.Rect(heal_x, y, slot_size, slot_size)

            pygame.draw.rect(surface, (40, 40, 45), slot_rect, border_radius=6)
            pygame.draw.rect(surface, (220, 220, 220), slot_rect, 2, border_radius=6)
            pygame.draw.rect(surface, (220, 40, 70),
                            pygame.Rect(heal_x + 8, y + 8, slot_size - 16, slot_size - 16),
                            border_radius=6)

    def sword_attack(self, dx, dy, enemies):
        self.attack_direction = (dx, dy)
        attack_size = 55 + self.range_boost // 3
        if dx == 1:   self.attack_rect = pygame.Rect(self.rect.right,          self.rect.centery-15, attack_size, 30)
        elif dx == -1: self.attack_rect = pygame.Rect(self.rect.left-attack_size, self.rect.centery-15, attack_size, 30)
        elif dy == 1:  self.attack_rect = pygame.Rect(self.rect.centerx-15, self.rect.bottom,          30, attack_size)
        elif dy == -1: self.attack_rect = pygame.Rect(self.rect.centerx-15, self.rect.top-attack_size, 30, attack_size)
        self.attack_timer = 6

        #effet de slash
        self.particles.emit_sparks(
            self.rect.centerx + dx * 30,
            self.rect.centery + dy * 30,
            count=5, color=(255, 240, 180)
        )

        for enemy in enemies:
            if enemy.hp > 0 and self.attack_rect.colliderect(enemy.rect):
                enemy.hp -= 2 + self.damage_boost
                enemy.rect.x = max(40, min(800 - 40, enemy.rect.x + dx * 32))
                enemy.rect.y = max(40, min(600 - 40, enemy.rect.y + dy * 32))
                self.shake.trigger(intensity=4, duration=7)
                self.particles.emit_blood(enemy.rect.centerx, enemy.rect.centery, count=10)

