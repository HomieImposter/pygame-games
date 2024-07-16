import pygame
import random
from pygame import gfxdraw
pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 920, 860
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris")
timer = pygame.time.Clock()
FPS = 60
font = pygame.font.Font("fonts/arcadeclassic.TTF", 50)

i_rotations = [
    [
        [' ', ' ', ' ', ' '],
        ['I', 'I', 'I', 'I'],
        [' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ']
    ],
    [
        [' ', ' ', 'I', ' '],
        [' ', ' ', 'I', ' '],
        [' ', ' ', 'I', ' '],
        [' ', ' ', 'I', ' ']
    ],
    [
        [' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' '],
        ['I', 'I', 'I', 'I'],
        [' ', ' ', ' ', ' ']
    ],
    [
        [' ', 'I', ' ', ' '],
        [' ', 'I', ' ', ' '],
        [' ', 'I', ' ', ' '],
        [' ', 'I', ' ', ' ']
    ]
]

j_rotations = [
    [
        ['J', ' ', ' '],
        ['J', 'J', 'J'],
        [' ', ' ', ' ']
    ],
    [
        [' ', 'J', 'J'],
        [' ', 'J', ' '],
        [' ', 'J', ' ']
    ],
    [
        [' ', ' ', ' '],
        ['J', 'J', 'J'],
        [' ', ' ', 'J']
    ],
    [
        [' ', 'J', ' '],
        [' ', 'J', ' '],
        ['J', 'J', ' ']
    ]
]

l_rotations = [
    [
        [' ', ' ', 'L'],
        ['L', 'L', 'L'],
        [' ', ' ', ' ']
    ],
    [
        [' ', 'L', ' '],
        [' ', 'L', ' '],
        [' ', 'L', 'L']
    ],
    [
        [' ', ' ', ' '],
        ['L', 'L', 'L'],
        ['L', ' ', ' ']
    ],
    [
        ['L', 'L', ' '],
        [' ', 'L', ' '],
        [' ', 'L', ' ']
    ]
]

o_rotations = [
    [
        ['O', 'O'],
        ['O', 'O']
    ]
]

z_rotations = [
    [
        [' ', 'Z', 'Z'],
        ['Z', 'Z', ' '],
        [' ', ' ', ' ']
    ],
    [
        [' ', 'Z', ' '],
        [' ', 'Z', 'Z'],
        [' ', ' ', 'Z']
    ],
    [
        [' ', ' ', ' '],
        [' ', 'Z', 'Z'],
        ['Z', 'Z', ' ']
    ],
    [
        ['Z', ' ', ' '],
        ['Z', 'Z', ' '],
        [' ', 'Z', ' ']
    ]
]

t_rotations = [
    [
        [' ', 'T', ' '],
        ['T', 'T', 'T'],
        [' ', ' ', ' ']
    ],
    [
        [' ', 'T', ' '],
        [' ', 'T', 'T'],
        [' ', 'T', ' ']
    ],
    [
        [' ', ' ', ' '],
        ['T', 'T', 'T'],
        [' ', 'T', ' ']
    ],
    [
        [' ', 'T', ' '],
        ['T', 'T', ' '],
        [' ', 'T', ' ']
    ]
]

s_rotations = [
    [
        ['S', 'S', ' '],
        [' ', 'S', 'S'],
        [' ', ' ', ' ']
    ],
    [
        [' ', ' ', 'S'],
        [' ', 'S', 'S'],
        [' ', 'S', ' ']
    ],
    [
        [' ', ' ', ' '],
        ['S', 'S', ' '],
        [' ', 'S', 'S']
    ],
    [
        [' ', 'S', ' '],
        ['S', 'S', ' '],
        ['S', ' ', ' ']
    ]
]

light_blue = pygame.image.load("tetris-assets/textures/Light Blue Block.png").convert_alpha()
dark_blue = pygame.image.load("tetris-assets/textures/Dark Blue Block.png").convert_alpha()
orange = pygame.image.load("tetris-assets/textures/Orange Block.png").convert_alpha()
yellow = pygame.image.load("tetris-assets/textures/Yellow Block.png").convert_alpha()
green = pygame.image.load("tetris-assets/textures/Green Block.png").convert_alpha()
purple = pygame.image.load("tetris-assets/textures/Purple Block.png").convert_alpha()
red = pygame.image.load("tetris-assets/textures/Red Block.png").convert_alpha()
ghost = pygame.image.load("tetris-assets/textures/Ghost Block.png").convert_alpha()
controls = pygame.image.load("tetris-assets/textures/Controls.png").convert_alpha()
controls = pygame.transform.scale_by(controls, 5)

theme_song = pygame.mixer.Sound("tetris-assets/audio/Tetris Theme.mp3")
piece_landed = pygame.mixer.Sound("tetris-assets/audio/tetris-piece-landed.mp3")
line_clear = pygame.mixer.Sound("tetris-assets/audio/tetris-line-clear.mp3")
level_up = pygame.mixer.Sound("tetris-assets/audio/tetris-level-up.mp3")
game_over_sound = pygame.mixer.Sound("tetris-assets/audio/tetris-game-over.mp3")
home_icon = pygame.image.load("misc/Home Icon.png").convert_alpha()
replay_icon = pygame.image.load("misc/Replay Icon.png").convert_alpha()

LIGHT_GREY = (112, 112, 128)
DEEP_BLUE = (24, 24, 38)
GRID_COLOUR = (68, 68, 83)
BACKGROUND = (24, 24, 38)

score = 0
level = 1
static_board = [[' ' for _ in range(10)] for _ in range(20)]
moving_board = [[' ' for _ in range(10)] for _ in range(20)]
next = random.choice(list("IJLOT"))
move_cooldown = FPS
speed = 0.8
game_over = False
right_key_down = False
left_key_down = False
down_key_down = False
shape_rotation = 0
current_shape = ' '
current_shape_origin = [0, 0]
held = ' '
used_hold = False
bag = list("IJLOZTS")
lines_since_level_up = 0
mute = True
theme_channel = pygame.mixer.Channel(0)
theme_channel.set_volume(0.5)
sfx_channel = pygame.mixer.Channel(1)
sfx_channel_2 = pygame.mixer.Channel(2)
with open("tetris-assets/highscore.txt") as file:
    highscore = int(file.readline())


def get_block(letter):
    if letter == 'I':
        return light_blue
    if letter == 'J':
        return dark_blue
    if letter == 'L':
        return orange
    if letter == 'O':
        return yellow
    if letter == 'Z':
        return green
    if letter == 'T':
        return purple
    if letter == 'S':
        return red


def get_rotations(letter):
    if letter == 'I':
        return i_rotations
    if letter == 'J':
        return j_rotations
    if letter == 'L':
        return l_rotations
    if letter == 'O':
        return o_rotations
    if letter == 'Z':
        return z_rotations
    if letter == 'T':
        return t_rotations
    if letter == 'S':
        return s_rotations


def draw_text(text, text_center):
    text = font.render(text, False, (222, 222, 222))
    text_rect = text.get_rect(center=text_center)
    screen.blit(text, text_rect)


def draw_game_area():
    pygame.draw.rect(screen, LIGHT_GREY, (255, 25, 410, 810))
    pygame.draw.rect(screen, DEEP_BLUE, (260, 30, 400, 800))

    # Draw grid
    for x in range(10):
        pygame.draw.rect(screen, GRID_COLOUR, (x * 40 + 260, 30, 1, 800))
    for y in range(20):
        pygame.draw.rect(screen, GRID_COLOUR, (260, y * 40 + 30, 400, 1))

    draw_ghost()

    # Draw (static) board
    for y, j in enumerate(static_board):
        for x, i in enumerate(j):
            if i != ' ':
                screen.blit(get_block(i), (x * 40 + 260, y * 40 + 30))
    # Draw (moving) board
    for y, j in enumerate(moving_board):
        for x, i in enumerate(j):
            if i != ' ':
                screen.blit(get_block(i), (x * 40 + 260, y * 40 + 30))


def draw_piece(piece, pos, surf=screen):
    if piece == 'I':
        piece_surface = pygame.Surface((40, 160))
        for y in range(4):
            piece_surface.blit(light_blue, (0, y * 40))
    elif piece == 'J' or piece == 'L':
        piece_surface = pygame.Surface((80, 120))
        ind = 3 if piece == 'J' else 1
        for y, j in enumerate(get_rotations(piece)[ind]):
            for x, i in enumerate(j):
                if i == 'J':
                    piece_surface.blit(dark_blue, (x * 40, y * 40))
                elif i == 'L':
                    piece_surface.blit(orange, (x * 40 - 40, y * 40))
    elif piece == 'O':
        piece_surface = pygame.Surface((80, 80))
        for y in range(2):
            for x in range(2):
                piece_surface.blit(yellow, (x * 40, y * 40))
    elif piece == 'Z' or piece == 'T' or piece == 'S':
        piece_surface = pygame.Surface((120, 80))
        for y, j in enumerate(get_rotations(piece)[0]):
            for x, i in enumerate(j):
                if i != ' ':
                    piece_surface.blit(get_block(i), (x * 40, y * 40))
    else:
        piece_surface = pygame.Surface((0, 0))
    piece_surface.set_colorkey((0, 0, 0))
    piece_surface_rect = piece_surface.get_rect(center=pos)
    surf.blit(piece_surface, piece_surface_rect)


icon = pygame.Surface((120, 120))
draw_piece(random.choice(list("IJLOZTS")), (60, 60), icon)
icon.set_colorkey((0, 0, 0))
pygame.display.set_icon(icon)


def draw_hold_area():
    pygame.draw.rect(screen, LIGHT_GREY, (25, 25, 210, 310))
    pygame.draw.rect(screen, DEEP_BLUE, (30, 30, 200, 300))
    draw_text("HOLD", (130, 50))

    draw_piece(held, (130, 200))


def draw_next_area():
    pygame.draw.rect(screen, LIGHT_GREY, (685, 25, 210, 310))
    pygame.draw.rect(screen, DEEP_BLUE, (690, 30, 200, 300))
    draw_text("NEXT", (790, 50))

    draw_piece(next, (790, 200))


def draw_score_area():
    pygame.draw.rect(screen, LIGHT_GREY, (685, 355, 210, 380))
    pygame.draw.rect(screen, DEEP_BLUE, (690, 360, 200, 370))
    draw_text("SCORE", (790, 405))
    draw_text(f"{score}", (790, 455))
    draw_text("LEVEL", (790, 520))
    draw_text(f"{level}", (790, 570))
    draw_text("HIGH", (790, 630))
    if score < highscore:
        draw_text(f"{highscore}", (790, 680))
    else:
        draw_text(f"{score}", (790, 680))


def draw_ghost():
    if moving_board == [[' ' for _ in range(10)] for _ in range(20)]:
        return
    distance = -1

    found = False
    while not found:  # Failsafe of 20
        distance += 1
        for y, j in enumerate(moving_board):
            for x, i in enumerate(j):
                if i != ' ':
                    if y + distance == 19 or (y + distance < 19 and static_board[y + distance + 1][x] != ' '):
                        found = True

    for y, j in enumerate(moving_board):
        for x, i in enumerate(j):
            if i != ' ':
                screen.blit(ghost, (x * 40 + 260, (y + distance) * 40 + 30))


def draw_game_over_screen():
    global score

    gfxdraw.filled_polygon(screen, ((0, 0), (SCREEN_WIDTH, 0), (SCREEN_WIDTH, SCREEN_HEIGHT), (0, SCREEN_HEIGHT)), (24, 24, 38, 100))

    game_over_text = font.render("GAME OVER", False, (222, 222, 222))
    game_over_text = pygame.transform.scale_by(game_over_text, 3)
    game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
    screen.blit(game_over_text, game_over_rect)

    score_text = font.render(f"SCORE          {score}", False, (222, 222, 222))
    score_text = pygame.transform.scale_by(score_text, 1.5)
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(score_text, score_rect)

    level_text = font.render(f"LEVEL          {level}", False, (222, 222, 222))
    level_text = pygame.transform.scale_by(level_text, 1.45)
    level_rect = level_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70))
    screen.blit(level_text, level_rect)

    if score > highscore:
        highscore_text = font.render(f"NEW   HIGH   SCORE!", False, (219, 33, 33))
        with open("tetris-assets/highscore.txt", 'w') as file:
            file.write(str(score))
    else:
        highscore_text = font.render(f"HIGH          {highscore}", False, (222, 222, 222))
    highscore_text = pygame.transform.scale_by(highscore_text, 1.45)
    highscore_rect = highscore_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 140))
    screen.blit(highscore_text, highscore_rect)

    screen.blit(home_icon, (SCREEN_WIDTH // 2 - 250, 650))
    screen.blit(replay_icon, (SCREEN_WIDTH // 2 + 150, 650))


def generate_next_piece():  # Doing it this fancier way makes it feel more random, even if less
    global bag
    if not bag:  # bag == []
        bag = list("IJLOZTS")
        random.shuffle(bag)
    return bag.pop(0)


def step_board():
    global move_cooldown, next, game_over, moving_board, shape_rotation, current_shape, current_shape_origin, used_hold, mute

    move_cooldown -= 1
    if move_cooldown <= 0:
        move_cooldown = FPS * speed
    else:
        return

    if game_over:
        return

    if moving_board == [[' ' for _ in range(10)] for _ in range(20)]:
        if static_board[0][3:7] == static_board[1][3:7] == [' ' for _ in range(4)]:
            moving_board[0][3:7] = get_rotations(next)[0][0]
            moving_board[1][3:7] = get_rotations(next)[0][1]
            current_shape = next
            next = generate_next_piece()
            shape_rotation = 0
            current_shape_origin = [3, 0]  # x, y
            used_hold = False
        else:
            if not mute:
                sfx_channel_2.play(game_over_sound)
            mute = True
            game_over = True
    else:
        next_moving_board = [[' ' for _ in range(10)] for _ in range(20)]
        for y, j in enumerate(moving_board):
            for x, i in enumerate(j):
                if i != ' ':
                    if y == 19 or static_board[y+1][x] != ' ':
                        stop_moving()
                        next_moving_board = [[' ' for _ in range(10)] for _ in range(20)]
                        return
                    else:
                        next_moving_board[y+1][x] = i
        current_shape_origin[1] += 1
        moving_board = next_moving_board


def stop_moving():
    global moving_board, static_board
    for y, j in enumerate(moving_board):
        for x, i in enumerate(j):
            if i != ' ':
                static_board[y][x] = i
    moving_board = [[' ' for _ in range(10)] for _ in range(20)]
    check_line_clear()
    if not mute:
        sfx_channel.play(piece_landed)


def move(dir):
    global moving_board, current_shape_origin
    next_moving_board = [[' ' for _ in range(10)] for _ in range(20)]
    can_move = True

    for y, j in enumerate(moving_board):
        for x, i in enumerate(j):
            if i != ' ' and (x + dir[0] == -1 or x + dir[0] == 10 or y + dir[1] == 20 or static_board[y + dir[1]][x + dir[0]] != ' '):
                can_move = False
    if can_move:
        for y, j in enumerate(moving_board):
            for x, i in enumerate(j):
                if i != ' ':
                    next_moving_board[y + dir[1]][x + dir[0]] = i
        current_shape_origin[0] += dir[0]
        current_shape_origin[1] += dir[1]
    else:
        next_moving_board = moving_board

    moving_board = next_moving_board


def rotate():
    global shape_rotation, moving_board
    shape_rotation += 1
    if len(get_rotations(current_shape)) == shape_rotation:
        shape_rotation = 0

    next_moving_board = [[' ' for _ in range(10)] for _ in range(20)]
    can_move = True
    for y, j in enumerate(get_rotations(current_shape)[shape_rotation]):
        for x, i in enumerate(j):
            if i != ' ':
                if 0 <= y + current_shape_origin[1] < 20 and 0 <= x + current_shape_origin[0] < 10:
                    next_moving_board[y + current_shape_origin[1]][x + current_shape_origin[0]] = i
                else:
                    can_move = False
    for y, j in enumerate(static_board):
        for x, i in enumerate(j):
            if i != ' ' and next_moving_board[y][x] != ' ':
                can_move = False
    if can_move:
        moving_board = next_moving_board


def drop():
    global moving_board
    if moving_board == [[' ' for _ in range(10)] for _ in range(20)]:
        return
    distance = -1

    found = False
    while not found:
        distance += 1
        for y, j in enumerate(moving_board):
            for x, i in enumerate(j):
                if i != ' ':
                    if y + distance == 19 or (y + distance < 19 and static_board[y + distance + 1][x] != ' '):
                        found = True

    next_moving_board = [[' ' for _ in range(10)] for _ in range(20)]
    for y, j in enumerate(moving_board):
        for x, i in enumerate(j):
            if i != ' ':
                next_moving_board[y + distance][x] = i
    moving_board = next_moving_board

    stop_moving()


def hold():
    global used_hold, held, current_shape, current_shape_origin, shape_rotation, moving_board
    if used_hold or moving_board == [[' ' for _ in range(10)] for _ in range(20)]:
        return

    next_held = current_shape
    if static_board[0][3:7] == static_board[1][3:7] == [' ' for _ in range(4)]:
        moving_board = [[' ' for _ in range(10)] for _ in range(20)]
        if held != ' ':
            moving_board[0][3:7] = get_rotations(held)[0][0]
            moving_board[1][3:7] = get_rotations(held)[0][1]
        current_shape = held
        shape_rotation = 0
        current_shape_origin = [3, 0]
        used_hold = True
    held = next_held


def check_line_clear():
    global static_board, score, level, lines_since_level_up, speed
    lines_cleared = 0
    for i, line in enumerate(static_board):
        if ' ' not in line:
            static_board[i] = [' ' for _ in range(10)]
            lines_cleared += 1
    if lines_cleared == 0:
        return

    lines_deleted = 0
    for line in reversed(range(20)):
        if lines_deleted == lines_cleared:
            break
        if static_board[line] == [' ' for _ in range(10)]:
            del static_board[line]
            lines_deleted += 1
    for _ in range(lines_deleted):
        static_board.insert(0, [' ' for _ in range(10)])

    scores = [800, 1200, 1800, 3200]
    score += scores[lines_cleared-1] * level

    lines_since_level_up += lines_cleared
    if lines_since_level_up >= 10:
        speed = (0.8 - level * 0.007) ** level
        lines_since_level_up -= 10
        level += 1
        speed = 0.1 if speed <= 0 else speed
        if not mute:
            sfx_channel_2.play(level_up)
    elif not mute:
        sfx_channel_2.play(line_clear)


def reset():
    global score, level, static_board, moving_board, next, move_cooldown, speed, game_over, right_key_down, left_key_down
    global down_key_down, shape_rotation, current_shape, current_shape_origin, held, used_hold, bag, lines_since_level_up, highscore

    score = 0
    level = 1
    static_board = [[' ' for _ in range(10)] for _ in range(20)]
    moving_board = [[' ' for _ in range(10)] for _ in range(20)]
    next = random.choice(list("IJLOT"))
    move_cooldown = FPS
    speed = 0.8
    game_over = False
    right_key_down = False
    left_key_down = False
    down_key_down = False
    shape_rotation = 0
    current_shape = ' '
    current_shape_origin = [0, 0]
    held = ' '
    used_hold = False
    bag = list("IJLOZTS")
    lines_since_level_up = 0

    icon = pygame.Surface((120, 120))
    draw_piece(random.choice(list("IJLOZTS")), (60, 60), icon)
    icon.set_colorkey((0, 0, 0))
    pygame.display.set_icon(icon)

    with open("tetris-assets/highscore.txt") as file:
        highscore = int(file.readline())


def tetris():
    global mute, left_key_down, right_key_down, down_key_down

    SCREEN_WIDTH, SCREEN_HEIGHT = 920, 860
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris")
    icon = pygame.Surface((120, 120))
    draw_piece(random.choice(list("IJLOZTS")), (60, 60), icon)
    icon.set_colorkey((0, 0, 0))
    pygame.display.set_icon(icon)

    theme_channel.play(theme_song, -1)

    running = True
    while running:
        timer.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and not game_over:
                if event.key == pygame.K_RIGHT:
                    right_key_down = True
                elif event.key == pygame.K_LEFT:
                    left_key_down = True
                elif event.key == pygame.K_DOWN:
                    down_key_down = True
                elif event.key == pygame.K_UP:
                    rotate()
                elif event.key == pygame.K_SPACE:
                    drop()
                elif event.key == pygame.K_h:
                    hold()
                elif event.key == pygame.K_m:
                    mute = not mute
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    right_key_down = False
                elif event.key == pygame.K_LEFT:
                    left_key_down = False
                elif event.key == pygame.K_DOWN:
                    down_key_down = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.Rect(SCREEN_WIDTH // 2 - 250, 650, 100, 100).collidepoint(pygame.mouse.get_pos()):
                    running = False
                elif pygame.Rect(SCREEN_WIDTH // 2 + 150, 650, 100, 100).collidepoint(pygame.mouse.get_pos()):
                    reset()

        if (0 <= move_cooldown % 5 < 1 and FPS * speed > 5) or (0 <= move_cooldown % 2 < 1 and FPS * speed <= 5):
            if left_key_down:
                move((-1, 0))
            if right_key_down:
                move((1, 0))
            if down_key_down:
                move((0, 1))

        screen.fill(BACKGROUND)
        draw_game_area()
        draw_hold_area()
        draw_next_area()
        draw_score_area()
        step_board()
        screen.blit(controls, (10, 355))
        if game_over:
            draw_game_over_screen()

        if mute:
            theme_channel.pause()
        else:
            theme_channel.unpause()

        pygame.display.update()

    if score > highscore:
        with open("tetris-assets/highscore.txt", 'w') as file:
            file.write(str(score))

    reset()


if __name__ == "__main__":
    tetris()
    pygame.quit()
