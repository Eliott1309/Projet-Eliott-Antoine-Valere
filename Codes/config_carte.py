import random

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 40
COLS = SCREEN_WIDTH // TILE_SIZE
ROWS = SCREEN_HEIGHT // TILE_SIZE
MINI_ROOM_SIZE = 12
MINI_ROOM_GAP = 4


#ici on cree une salle vide, ca prend rien et ca renvoie une grille sans obstacle
def make_empty():
    return [[0] * COLS for _ in range(ROWS)]


#on part d'une grille vide puis on met 4 gros piliers, ca renvoie la grille finie
def make_piliers():
    grid = make_empty()
    for px, py in [(5, 4), (5, 10), (14, 4), (14, 10)]:
        for dy in range(2):
            for dx in range(2):
                grid[py + dy][px + dx] = 1
    return grid


#sert a faire une salle en forme de croix, ca ne prend rien et renvoie la grille
def make_croix():
    grid = [[1] * COLS for _ in range(ROWS)]
    for row in range(5, 10):
        for col in range(COLS):
            grid[row][col] = 0
    for row in range(ROWS):
        for col in range(8, 12):
            grid[row][col] = 0
    return grid


#ici ca coupe la salle en deux avec un passage au milieu, puis ca renvoie la grille
def make_chambres():
    grid = make_empty()
    for row in range(ROWS):
        grid[row][10] = 1
    for row in range(6, 9):
        grid[row][10] = 0
    return grid


#on ajoute des petits murs au hasard pour faire labyrinthe, ca renvoie la salle cree
def make_labyrinthe():
    grid = make_empty()
    for _ in range(12):
        col = random.randint(2, COLS - 3)
        row = random.randint(2, ROWS - 3)
        length = random.randint(2, 4)
        horizontal = random.choice([True, False])
        for i in range(length):
            r = row + (0 if horizontal else i)
            c = col + (i if horizontal else 0)
            if 1 < r < ROWS - 1 and 1 < c < COLS - 1:
                grid[r][c] = 1
    return grid


ROOM_TEMPLATES = [make_empty, make_piliers, make_croix, make_chambres, make_labyrinthe]

