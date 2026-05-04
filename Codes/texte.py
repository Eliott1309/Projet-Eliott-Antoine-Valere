import os
import pygame

base = os.path.dirname(os.path.abspath(__file__))
MEDIEVAL_FONT_PATH = os.path.join(base, "assets", "medieval.ttf")


def get_medieval_font(size):
    try:
        return pygame.font.Font(MEDIEVAL_FONT_PATH, size)
    except Exception:
        return pygame.font.Font(None, size)


def draw_dialog_box(screen, text, width, height, text_index):
    box_width = 720
    box_height = 120
    x = (width - box_width) // 2
    y = height - box_height - 30
    pygame.draw.rect(screen, (110, 0, 0), (x-8, y-8, box_width+16, box_height+16))
    pygame.draw.rect(screen, (230, 70, 20), (x-3, y-3, box_width+6, box_height+6))
    pygame.draw.rect(screen, (245, 230, 190), (x, y, box_width, box_height))

    font = get_medieval_font(24)
    words = text[:text_index].split(" ")
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

