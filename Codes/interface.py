from texte import draw_dialog_box, get_medieval_font


def draw_extra_hud(surface, player, game_map, score, pickup_message,
                   pickup_message_timer, font_hud, font_message, width):
    enemies_left = sum(1 for e in game_map.current_room.enemies if e.hp > 0)
    weapon_names = {None: "Aucune", "sword": "Epee", "crossbow": "Arbalete",
                    "bow": "Arc", "magic_wand": "Baguette"}
    surface.blit(font_hud.render("Score : " + str(score), True, (255, 255, 255)), (10, 38))
    surface.blit(font_hud.render("Arme : " + weapon_names[player.weapon], True, (255, 255, 255)), (10, 66))
    surface.blit(font_hud.render("Ennemis restants : " + str(enemies_left), True, (255, 255, 255)), (10, 94))
    surface.blit(font_hud.render("Niveau : " + str(game_map.level), True, (200, 130, 255)), (10, 122))
    surface.blit(font_hud.render("Armes : touche 1", True, (210, 210, 210)), (10, 150))
    if pickup_message_timer > 0:
        msg_surf = font_message.render(pickup_message, True, (255, 230, 120))
        surface.blit(msg_surf, (width // 2 - msg_surf.get_width() // 2, 45))

