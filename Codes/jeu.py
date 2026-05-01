import pygame
import sys
from map import Map, SCREEN_HEIGHT, SCREEN_WIDTH

def lancer_jeu(keyboard_layout="azerty",assets=None):
    """Lance le jeu principal."""
    pygame.init()

    # Fenêtre
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mini Isaac")

    clock = pygame.time.Clock()
    font_game_over = pygame.font.Font(None, 80)
    font_restart = pygame.font.Font(None, 36)

    # Couleurs
    WHITE = (255, 255, 255)
    RED = (200, 50, 50)
    BLUE = (50, 100, 255)
    BLACK = (0, 0, 0)

    class Player:
        def __init__(self):
            self.rect = pygame.Rect(400, 300, 40, 40)
            self.speed = 5
            self.hp = 5
            self.max_hp = 5
            self.invincible_timer = 0  # frames d'invincibilité après un coup
            self.inventory = []
            self.weapon = None
            self.attack_rect = None
            self.attack_timer = 0
            self.attack_direction = None
            self.footstep_timer = 0
            self.footstep_channel = None




        def take_damage(self, amount=1):
            if self.invincible_timer == 0:
                self.hp -= amount
                self.invincible_timer = 60  # 1 seconde d'invincibilité

        def is_alive(self):
            return self.hp > 0

        # applique l'effet de l'objet ramassé par le joueur
        def apply_item(self, item_type):
            if item_type == "heart":
                if self.hp < self.max_hp:
                    self.hp = min(self.max_hp, self.hp + 1)
                    return True
                elif len(self.inventory) < 5:
                    self.inventory.append("heart")
                    return True
                return False

            elif item_type == "speed":
                self.speed += 0.5
                return True

        # utilise un objet de l'inventaire selon sa case
        def use_inventory_item(self, index):
            if index >= len(self.inventory):
                return

            item_type = self.inventory[index]

            if item_type == "heart" and self.hp < self.max_hp:
                self.hp = min(self.max_hp, self.hp + 1)
                self.inventory.pop(index)




        # affiche la barre de vie du joueur
        def draw_hp_bar(self, surface):
            """Dessine la barre de vie en haut à gauche."""
            BAR_X, BAR_Y = 10, 10
            BAR_W, BAR_H = 200, 20
            HEART_SIZE = 20
            PADDING = 4

            for i in range(self.max_hp):
                x = BAR_X + i * (HEART_SIZE + PADDING)
                color = (220, 50, 50) if i < self.hp else (80, 80, 80)
                pygame.draw.rect(surface, color, (x, BAR_Y, HEART_SIZE, HEART_SIZE), border_radius=4)
                pygame.draw.rect(surface, (255, 255, 255), (x, BAR_Y, HEART_SIZE, HEART_SIZE), 1, border_radius=4)

        # déplace le joueur et gère les collisions avec la salle
        def move(self, keys, game_map):
            if self.invincible_timer > 0:
                self.invincible_timer -= 1
            dx, dy = 0, 0

            if keyboard_layout == "azerty":
                left_key = pygame.K_q
                up_key = pygame.K_z
            else:
                left_key = pygame.K_a
                up_key = pygame.K_w

            if keys[left_key]: dx -= 1
            if keys[pygame.K_d]: dx += 1
            if keys[up_key]: dy -= 1
            if keys[pygame.K_s]: dy += 1


            #joue le son de pas seulement s'il n'est pas déjà lancé
            if dx != 0 or dy != 0:
                if self.footstep_channel is None or not self.footstep_channel.get_busy():
                    self.footstep_channel = assets["footstep"].play()
            else:
                if self.footstep_channel is not None:
                    self.footstep_channel.stop()
                    self.footstep_channel = None



            # Normalisation : si on bouge en diagonale, on réduit la vitesse
            if dx != 0 and dy != 0:
                dx *= 0.7071  
                dy *= 0.7071

            # Axe horizontal
            self.rect.x += dx * self.speed
            self._resolve_collisions(game_map, axis="x")

            # Axe vertical
            self.rect.y += dy * self.speed
            self._resolve_collisions(game_map, axis="y")

        def _resolve_collisions(self, game_map, axis):
            current_room = game_map.current_room

            for wall_rect in current_room.get_wall_rects():
                if self.rect.colliderect(wall_rect):
                    if axis == "x":
                        if self.rect.centerx < wall_rect.centerx:
                            self.rect.right = wall_rect.left
                        else:
                            self.rect.left = wall_rect.right
                    elif axis == "y":
                        if self.rect.centery < wall_rect.centery:
                            self.rect.bottom = wall_rect.top
                        else:
                            self.rect.top = wall_rect.bottom

            for direction, door_rect in current_room.get_door_rects().items():
                if self.rect.colliderect(door_rect):
                    if current_room.cleared:
                        dx, dy = current_room.door_directions[direction]
                        game_map.change_room(dx, dy, self)
                        return
                    else:
                        if axis == "x":
                            if self.rect.centerx < door_rect.centerx:
                                self.rect.right = door_rect.left
                            else:
                                self.rect.left = door_rect.right
                        elif axis == "y":
                            if self.rect.centery < door_rect.centery:
                                self.rect.bottom = door_rect.top
                            else:
                                self.rect.top = door_rect.bottom
        def draw(self):
            screen.blit(assets["player"], self.rect)
            if self.attack_timer > 0 and self.attack_rect is not None:
                #affiche un petit arc pour l'attaque de l'épée
                slash = pygame.Surface((70, 70), pygame.SRCALPHA)
                color = (240, 240, 255, 180)

                if self.attack_direction == (1, 0):
                    pygame.draw.arc(slash, color, (10, 10, 50, 50), -1.2, 1.2, 4)
                    screen.blit(slash, (self.rect.right - 20, self.rect.centery - 35))
                elif self.attack_direction == (-1, 0):
                    pygame.draw.arc(slash, color, (10, 10, 50, 50), 1.9, 4.4, 4)
                    screen.blit(slash, (self.rect.left - 50, self.rect.centery - 35))
                elif self.attack_direction == (0, -1):
                    pygame.draw.arc(slash, color, (10, 10, 50, 50), 0.3, 2.8, 4)
                    screen.blit(slash, (self.rect.centerx - 35, self.rect.top - 50))
                elif self.attack_direction == (0, 1):
                    pygame.draw.arc(slash, color, (10, 10, 50, 50), 3.4, 5.9, 4)
                    screen.blit(slash, (self.rect.centerx - 35, self.rect.bottom - 20))


        # affiche les cases de l'inventaire en bas de l'écran
        def draw_inventory(self, surface, assets):
            slot_size = 30
            spacing = 5
            slots = 5

            start_x = 10
            y = 562

            for i in range(slots):
                x = start_x + i * (slot_size + spacing)

                slot_rect = pygame.Rect(x, y, slot_size, slot_size)

                pygame.draw.rect(surface, (40, 40, 45), slot_rect, border_radius=6)
                pygame.draw.rect(surface, (220, 220, 220), slot_rect, 2, border_radius=6)
                if i == 0 and self.weapon is not None:
                    surface.blit(assets[self.weapon], slot_rect)

                item_index = i - 1

                if i > 0 and item_index < len(self.inventory):
                    if self.inventory[item_index] == "heart":
                        heart_rect = pygame.Rect(x + 8, y + 8, slot_size - 16, slot_size - 16)
                        pygame.draw.rect(surface, (220, 40, 70), heart_rect, border_radius=6)

        
        #crée une zone d'attaque courte pour l'épée
        def sword_attack(self, dx, dy, enemies):
            self.attack_direction = (dx, dy)
            attack_size = 45

            if dx == 1:
                self.attack_rect = pygame.Rect(self.rect.right, self.rect.centery - 15, attack_size, 30)
            elif dx == -1:
                self.attack_rect = pygame.Rect(self.rect.left - attack_size, self.rect.centery - 15, attack_size, 30)
            elif dy == 1:
                self.attack_rect = pygame.Rect(self.rect.centerx - 15, self.rect.bottom, 30, attack_size)
            elif dy == -1:
                self.attack_rect = pygame.Rect(self.rect.centerx - 15, self.rect.top - attack_size, 30, attack_size)

            self.attack_timer = 6

            for enemy in enemies:
                if enemy.hp > 0 and self.attack_rect.colliderect(enemy.rect):
                    enemy.hp -= 1



    class Bullet:
        def __init__(self, x, y, dx, dy, damage=1):
            """Initialise la balle avec une position et une direction."""
            self.rect = pygame.Rect(x, y, 10, 10)
            self.dx = dx
            self.dy = dy
            self.speed = 8
            self.damage = damage

        def update(self):
            """Met à jour la position de la balle."""
            self.rect.x += self.dx * self.speed
            self.rect.y += self.dy * self.speed

        def draw(self):
            """Dessine la balle sur l'écran."""
            pygame.draw.rect(screen, WHITE, self.rect)

    

    player = Player()
    bullets = []
    game_map = Map()

    shoot_cooldown = 0
    running = True

    while running:
        clock.tick(60)
        screen.fill(BLACK)

        keys = pygame.key.get_pressed()


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            #utilise un objet selon la touche 2 à 5
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_2:
                    player.use_inventory_item(0)
                elif event.key == pygame.K_3:
                    player.use_inventory_item(1)
                elif event.key == pygame.K_4:
                    player.use_inventory_item(2)
                elif event.key == pygame.K_5:
                    player.use_inventory_item(3)



        player.move(keys, game_map)
        
        if player.attack_timer > 0:
            player.attack_timer -= 1

        if shoot_cooldown > 0:
            shoot_cooldown -= 1

        if shoot_cooldown == 0:
            dx, dy = 0, 0

            if keys[pygame.K_i]:
                dx, dy = 0, -1
            elif keys[pygame.K_k]:
                dx, dy = 0, 1
            elif keys[pygame.K_j]:
                dx, dy = -1, 0
            elif keys[pygame.K_l]:
                dx, dy = 1, 0

            if dx != 0 or dy != 0:
                if player.weapon == "sword":
                    player.sword_attack(dx, dy, game_map.current_room.enemies)
                    shoot_cooldown = 15
                else:
                    damage = 1
                    cooldown = 10

                    #l'arbalète tire lentement mais tue instantanément
                    if player.weapon == "crossbow":
                        damage = 999
                        cooldown = 90

                    bullets.append(Bullet(player.rect.centerx, player.rect.centery, dx, dy, damage))
                    shoot_cooldown = cooldown


        
        for bullet in bullets[:]:
            bullet.update()

            if not screen.get_rect().colliderect(bullet.rect):
                bullets.remove(bullet)
                continue

            wall_rects = game_map.current_room.get_wall_rects()
            hit_wall = False
            for wall in wall_rects:
                if bullet.rect.colliderect(wall):
                    hit_wall = True
                    break
            if hit_wall:
                bullets.remove(bullet)
                continue

            for enemy in game_map.current_room.enemies:
                if enemy.hp > 0 and bullet.rect.colliderect(enemy.rect):
                    bullets.remove(bullet)
                    enemy.hp -= bullet.damage
                    break

        
        game_map.update(player)

        #ouvre le coffre si le joueur reste dessus 1 seconde
        chest = game_map.current_room.chest
        if chest is not None and not chest.opened:
            if player.rect.colliderect(chest.rect):
                chest.open_timer += 1

                if chest.open_timer >= 60:
                    player.weapon = chest.open()
            else:
                chest.open_timer = 0


        #vérifie si le joueur ramasse un objet au sol
        for item in game_map.current_room.items[:]:
            if player.rect.colliderect(item.rect):
                picked = player.apply_item(item.type)
                if picked:
                    game_map.current_room.items.remove(item)


        # Collision joueur / ennemis → dégâts
        for enemy in game_map.current_room.enemies:
            if enemy.hp > 0 and player.rect.colliderect(enemy.rect):
                player.take_damage(1)

        # Mort du joueur
        if not player.is_alive():
            screen.fill(BLACK)

            game_over_text = font_game_over.render("GAME OVER", True, RED)
            game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
            screen.blit(game_over_text, game_over_rect)

            restart_text = font_restart.render("Appuie sur ECHAP pour quitter", True, WHITE)
            restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
            screen.blit(restart_text, restart_rect)

            pygame.display.flip()

            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        waiting = False
                        running = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            waiting = False
                            running = False
            continue

        game_map.draw(screen, assets) 
        player.draw_hp_bar(screen)
        player.draw_inventory(screen, assets)
        
        player.draw()

        for bullet in bullets:
            bullet.draw()

        pygame.display.flip()
        

    
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    lancer_jeu()
