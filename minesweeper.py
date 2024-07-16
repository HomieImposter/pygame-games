import pygame
import random
import copy
pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1344, 768
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Minesweeper")
timer = pygame.time.Clock()
FPS = 60

textures = pygame.transform.scale(pygame.image.load("minesweeper-assets/textures.png"), (128, 128)).convert_alpha()
counter = [pygame.transform.scale(pygame.image.load(f"minesweeper-assets/counter/counter{x}.png"), (130/3.5, 250/3.5)).convert_alpha() for x in range(10)]
clickface = pygame.image.load("minesweeper-assets/faces/clickface.png").convert_alpha()
lostface = pygame.image.load("minesweeper-assets/faces/lostface.png").convert_alpha()
smileface = pygame.image.load("minesweeper-assets/faces/smileface.png").convert_alpha()
smilefacedown = pygame.image.load("minesweeper-assets/faces/smilefacedown.png").convert_alpha()
winface = pygame.image.load("minesweeper-assets/faces/winface.png").convert_alpha()
home_icon = pygame.image.load("misc/Home Icon.png").convert_alpha()
replay_icon = pygame.image.load("misc/Replay Icon.png").convert_alpha()


def fill(surface, color):  # From StackOverflow lol
    """Fill all pixels of the surface with color, preserve transparency."""
    w, h = surface.get_size()
    r, g, b = color
    for x in range(w):
        for y in range(h):
            a = surface.get_at((x, y))[3]
            surface.set_at((x, y), pygame.Color(r, g, b, a))


fill(home_icon, (70, 70, 70))
fill(replay_icon, (70, 70, 70))
home_icon = pygame.transform.smoothscale(home_icon, (64, 64))
replay_icon = pygame.transform.smoothscale(replay_icon, (64, 64))


def get_texture(grid_x, grid_y):
    texture = pygame.Surface((32, 32)).convert_alpha()
    texture.blit(textures, (0, 0), (grid_x * 32, grid_y * 32, 32, 32))
    return texture


blank_square = get_texture(0, 2)
one = get_texture(0, 0)
two = get_texture(1, 0)
three = get_texture(2, 0)
four = get_texture(3, 0)
five = get_texture(0, 1)
six = get_texture(1, 1)
seven = get_texture(2, 1)
eight = get_texture(3, 1)
numbers = [blank_square, one, two, three, four, five, six, seven, eight]
hidden = get_texture(1, 2)
flagged = get_texture(2, 2)
bomb = get_texture(2, 3)
bomb_red = get_texture(3, 3)
bomb_cross = get_texture(3, 2)


def reset():
    global board, won, lost, flags, time, timer_paused
    board = [[[0, "hidden"] for _ in range(42)] for _ in range(21)]
    populate_board()
    calculate_numbers()
    won = False
    lost = False
    flags = 0
    time = 0
    timer_paused = True


def draw_board():
    for y, j in enumerate(board):
        for x, i in enumerate(j):
            if i[1] == "hidden":
                screen.blit(hidden, (x * 32, y * 32 + 96))
            elif i[1] == "unhidden":
                if i[0] <= 8:
                    screen.blit(numbers[i[0]], (x * 32, y * 32 + 96))
                else:
                    screen.blit(bomb_red, (x * 32, y * 32 + 96))
            elif i[1] == "flagged":
                screen.blit(flagged, (x * 32, y * 32 + 96))

    if pygame.mouse.get_pressed()[0] and pygame.Rect(640, 16, 64, 64).collidepoint(pygame.mouse.get_pos()):
        screen.blit(pygame.transform.scale(smilefacedown, (64, 64)), (640, 16))
    elif won:
        screen.blit(pygame.transform.scale(winface, (64, 64)), (640, 16))
    elif lost:
        screen.blit(pygame.transform.scale(lostface, (64, 64)), (640, 16))
    elif pygame.mouse.get_pressed()[0]:
        screen.blit(pygame.transform.scale(clickface, (64, 64)), (640, 16))  # 640 = SCREEN_WIDTH / 2 - 32
    else:
        screen.blit(pygame.transform.scale(smileface, (64, 64)), (640, 16))


def populate_board():
    global board
    for _ in range(bombs):
        while True:
            row = random.randint(0, 20)
            column = random.randint(0, 41)
            if board[row][column][0] == 0:
                board[row][column][0] = 9
                break


def calculate_numbers():
    global board
    for y, j in enumerate(board):
        for x, i in enumerate(j):
            if i[0] == 9:
                continue

            board[y][x][0] += 1 if y > 0 and board[y-1][x][0] == 9 else 0
            board[y][x][0] += 1 if y < 20 and board[y+1][x][0] == 9 else 0
            board[y][x][0] += 1 if x > 0 and board[y][x-1][0] == 9 else 0
            board[y][x][0] += 1 if x < 41 and board[y][x+1][0] == 9 else 0

            board[y][x][0] += 1 if y > 0 and x > 0 and board[y-1][x-1][0] == 9 else 0
            board[y][x][0] += 1 if y > 0 and x < 41 and board[y-1][x+1][0] == 9 else 0
            board[y][x][0] += 1 if y < 20 and x > 0 and board[y+1][x-1][0] == 9 else 0
            board[y][x][0] += 1 if y < 20 and x < 41 and board[y+1][x+1][0] == 9 else 0


def reveal_bombs():
    for y, j in enumerate(board):
        for x, i in enumerate(j):
            if i == [9, "hidden"]:
                screen.blit(bomb, (x * 32, y * 32 + 96))
            elif i[0] != 9 and i[1] == "flagged":
                screen.blit(bomb_cross, (x * 32, y * 32 + 96))


def zero_spread():
    global board
    while True:
        prev_board = copy.deepcopy(board)
        for y, j in enumerate(board):
            for x, i in enumerate(j):
                if i == [0, "unhidden"]:
                    if y > 0:
                        board[y-1][x][1] = "unhidden"
                    if y < 20:
                        board[y+1][x][1] = "unhidden"
                    if x > 0:
                        board[y][x-1][1] = "unhidden"
                    if x < 41:
                        board[y][x+1][1] = "unhidden"

                    if y > 0 and x > 0:
                        board[y-1][x-1][1] = "unhidden"
                    if y > 0 and x < 41:
                        board[y-1][x+1][1] = "unhidden"
                    if y < 20 and x > 0:
                        board[y+1][x-1][1] = "unhidden"
                    if y < 20 and x < 41:
                        board[y+1][x+1][1] = "unhidden"

        if board == prev_board:
            break


def chord(pos):
    global board, lost

    flagged = 0

    # Count how many flags are surrounding
    for y in range(-1, 2):
        for x in range(-1, 2):
            if not (x == y == 0) and 0 <= pos[0] + x < 42 and 0 <= pos[1] + y < 21:
                flagged += 1 if board[pos[1] + y][pos[0] + x][1] == "flagged" else 0

    # If equal to the number, reveal all (non-flagged) neighbours
    if flagged == board[pos[1]][pos[0]][0]:
        for y in range(-1, 2):
            for x in range(-1, 2):
                if not (x == y == 0) and 0 <= pos[0] + x < 42 and 0 <= pos[1] + y < 21 and board[pos[1] + y][pos[0] + x][1] != "flagged":
                    board[pos[1] + y][pos[0] + x][1] = "unhidden"
                    if board[pos[1] + y][pos[0] + x][0] == 9:
                        lost = True
                    elif board[pos[1] + y][pos[0] + x][0] == 0:
                        zero_spread()


def draw_counters():
    global time_delay, time, timer_paused
    # Bombs left counter
    bombs_left = bombs - flags if bombs - flags >= 0 else 0
    bombs_left = str(f"{bombs_left:03}")
    screen.blit(counter[int(bombs_left[0])], (30, 17))
    screen.blit(counter[int(bombs_left[1])], (70, 17))
    screen.blit(counter[int(bombs_left[2])], (110, 17))

    # Timer
    if won or lost:
        timer_paused = True
    time_delay -= 1 if not timer_paused else 0
    if time_delay <= 0:
        time_delay = FPS
        time += 1 if time < 999 else 0

    display_time = str(f"{time:03}")
    screen.blit(counter[int(display_time[0])], (1200, 17))
    screen.blit(counter[int(display_time[1])], (1240, 17))
    screen.blit(counter[int(display_time[2])], (1280, 17))


def check_win():
    global won
    unhiddens = 0
    for y in board:
        for x in y:
            if x[1] == "unhidden":
                unhiddens += 1
    if unhiddens == 42 * 21 - bombs:
        won = True


def draw_gave_over_screen():  # For the sake of consistency
    screen.blit(home_icon, home_icon.get_rect(center=(SCREEN_WIDTH // 2 - 200, 52)))
    screen.blit(replay_icon, replay_icon.get_rect(center=(SCREEN_WIDTH // 2 + 200, 52)))


pygame.display.set_icon(flagged)
board = [[[0, "hidden"] for _ in range(42)] for _ in range(21)]
bombs = 100
populate_board()
calculate_numbers()
won = False
lost = False
flags = 0
time = 0
time_delay = FPS
timer_paused = True


def minesweeper():
    global flags, timer_paused, lost

    SCREEN_WIDTH, SCREEN_HEIGHT = 1344, 768
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Minesweeper")
    pygame.display.set_icon(flagged)

    running = True
    while running:
        timer.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not (lost or won):
                    pos = (pygame.mouse.get_pos()[0] // 32, (pygame.mouse.get_pos()[1] - 96) // 32)
                    if pygame.mouse.get_pressed()[0]:
                        if 0 <= pos[0] < 42 and 0 <= pos[1] < 21:
                            if board[pos[1]][pos[0]][1] == "hidden":
                                if timer_paused:
                                    while board[pos[1]][pos[0]][0] != 0:  # Bit scuffed but should make first click on zero
                                        reset()
                                board[pos[1]][pos[0]][1] = "unhidden"
                                if board[pos[1]][pos[0]][0] == 9:
                                    lost = True
                                elif board[pos[1]][pos[0]][0] == 0:
                                    zero_spread()
                            elif board[pos[1]][pos[0]][1] == "unhidden":
                                chord(pos)
                        timer_paused = False
                    elif pygame.mouse.get_pressed()[2]:
                        if 0 <= pos[0] < 42 and 0 <= pos[1] < 21:
                            if board[pos[1]][pos[0]][1] == "hidden":
                                board[pos[1]][pos[0]][1] = "flagged"
                                flags += 1
                            elif board[pos[1]][pos[0]][1] == "flagged":
                                board[pos[1]][pos[0]][1] = "hidden"
                                flags -= 1
                else:
                    if pygame.Rect(SCREEN_WIDTH // 2 - 232, 20, 64, 64).collidepoint(pygame.mouse.get_pos()):
                        running = False  # Clicked on the Home button
                    if pygame.Rect(SCREEN_WIDTH // 2 + 168, 20, 64, 64).collidepoint(pygame.mouse.get_pos()):
                        reset()  # Clicked on the Replay button
            elif event.type == pygame.MOUSEBUTTONUP:
                if pygame.Rect(640, 16, 64, 64).collidepoint(pygame.mouse.get_pos()):  # Face clicked
                    reset()

        screen.fill((200, 200, 200))
        draw_board()
        draw_counters()
        check_win()
        if lost:
            reveal_bombs()
        if won or lost:
            draw_gave_over_screen()

        pygame.display.update()

    reset()


if __name__ == "__main__":
    minesweeper()
    pygame.quit()
