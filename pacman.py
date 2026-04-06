import os
import pygame
from pygame.locals import *
import random

pygame.init()
WIDTH, HEIGHT = 512, 512

clock = pygame.time.Clock()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pacman 1.0")

font = pygame.font.Font(None, 36)

MAP = [
    '################',
    '#..............#',
    '#...########...#',
    '#.....G........#',
    '#..............#',
    '#..##########..#',
    '#..............#',
    '#.##.#....#.##.#',
    '#....#.G..#....#',
    '#.#..######..#.#',
    '#.#..........#.#',
    '#.###.####.###.#',    
    '#.G............#',
    '#....#.##.#..P.#',
    '#....#.G..#....#',
    '################',
]

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
DARKGRAY = (110, 110, 110)
RED = (255, 0, 0)
YELLOW = (255, 230, 0)

script_dir = os.path.dirname(os.path.abspath(__file__))

pacman_path = os.path.join(script_dir, "PacMan.png")
ghost_path = os.path.join(script_dir, "ghost.png")

try:
    pacman_img = pygame.image.load(pacman_path)
    pacman_img.convert()
    pacman_img = pygame.transform.scale(pacman_img, (32, 32))
except pygame.error:
    pacman_img = None

try:
    ghost_img = pygame.image.load(ghost_path)
    ghost_img.convert()
    ghost_img = pygame.transform.scale(ghost_img, (32, 32))
except pygame.error:
    ghost_img = None

background = BLACK

walls = []
apples = []
ghosts = []

class Tile:

    def __init__(self, is_a_wall, left, top):
        if is_a_wall == "#":
            wall = Rect(left, top, 32, 32)
            walls.append(wall)
            
        elif is_a_wall == ".":
            apple_rect = pygame.Rect(left+12, top+12, 8, 8)
            apples.append(apple_rect)            

def init_game():
    global player, direction, v

    player = None
    direction = 0  # 0: right, 90: down, 180: left, 270: up

    v = [0, 0]

    walls.clear()
    apples.clear()
    ghosts.clear()

    def init_gh_pos(left, top):
        ghost = Rect(left, top, 32, 32)
        ghosts.append(ghost)

    def init_pl_pos(left, top):
        global player
        player = Rect(left, top, 32, 32)

    for y, row in enumerate(MAP):
        for x, box in enumerate(row):
            if box == "P":
                init_pl_pos(x*32, y*32)
            elif box == "G":
                init_gh_pos(x*32, y*32)
            do = Tile(box, x*32, y*32)

# Initialize the game
init_game()

game_state = 'start'

lrkey_dict = {K_d:32, K_a:-32}
udkey_dict = {K_s:32, K_w:-32}

def rand_v():
    g_v = [0, 0]
    num = random.randrange(4)
    if num == 0:
        g_v = [32, 0]
    if num == 1:
        g_v = [-32, 0]
    if num == 2:
        g_v = [0, 32]
    if num == 3:
        g_v = [0, -32]
    return g_v

def gh_ai():
    for g in ghosts:
        g_v = rand_v()
        next_gh_x = (g.x + g_v[0])
        next_gh_y = (g.y + g_v[1])
        tile_gh_x = next_gh_x // 32
        tile_gh_y = next_gh_y // 32
        if MAP[tile_gh_y][tile_gh_x] == "#":
            continue
        else:
            g.x = next_gh_x
            g.y = next_gh_y

moving = False
running = True
while running:
    clock.tick(3)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == KEYDOWN:
            if game_state == 'start':
                if event.key == K_SPACE:
                    game_state = 'playing'
            elif game_state == 'playing':
                if event.key in lrkey_dict:
                    v[1] = 0
                    v [0] = lrkey_dict[event.key]
                    moving = True
                    if event.key == K_d:
                        direction = 180
                    elif event.key == K_a:
                        direction = 0
                elif event.key in udkey_dict:
                    v[0] = 0
                    v[1] = udkey_dict[event.key]
                    moving = True
                    if event.key == K_s:
                        direction = 90
                    elif event.key == K_w:
                        direction = 270
            elif game_state in ['lose', 'win']:
                if event.key == K_r:
                    init_game()
                    game_state = 'playing'
                    moving = False
                elif event.key == K_q:
                    running = False

    screen.fill(background)

    if game_state == 'start':
        start_text = font.render("Pacman - Press SPACE to start", True, YELLOW)
        screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, HEIGHT//2 - start_text.get_height()//2))
    elif game_state == 'playing':
        # --- Player Movement    
        next_x = (player.x + v[0])
        next_y = (player.y + v[1])

        tile_x = next_x // 32
        tile_y = next_y // 32

        if moving:
            if MAP[tile_y][tile_x] == "#":
                pass
            else:
                player.x = next_x
                player.y = next_y

        apples = [a for a in apples if not player.colliderect(a)]

        for wall in walls:
            pygame.draw.rect(screen, BLUE, wall)
        for a in apples:
            pygame.draw.circle(screen, YELLOW, a.center, 3)

        for g in ghosts:
            if ghost_img:
                screen.blit(ghost_img, g.topleft)
            else:
                pygame.draw.rect(screen, WHITE, g)

        for g in ghosts:
            if player.colliderect(g):
                game_state = 'lose'

        if apples == []:  
            game_state = 'win'

        gh_ai()

        if pacman_img:
            rotated_img = pygame.transform.rotate(pacman_img, direction)
            img_rect = rotated_img.get_rect(center=player.center)
            screen.blit(rotated_img, img_rect)
        else:
            pygame.draw.circle(screen, YELLOW, player.center, 14)
            pygame.draw.circle(screen, BLACK, player.center, 8)
    elif game_state == 'lose':
        lose_text = font.render("Game Over - Press R to restart or Q to quit", True, RED)
        screen.blit(lose_text, (WIDTH//2 - lose_text.get_width()//2, HEIGHT//2 - lose_text.get_height()//2))
    elif game_state == 'win':
        win_text = font.render("You Win! - Press R to restart or Q to quit", True, YELLOW)
        screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2 - win_text.get_height()//2))

    pygame.display.update()

pygame.quit()