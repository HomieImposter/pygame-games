import pygame
from pygame import gfxdraw
pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1344, 768
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Connect 4")
timer = pygame.time.Clock()
FPS = 60

RED = (200, 20, 20)
YELLOW = (245, 201, 7)
BLUE = (26, 44, 163)
DARK_GREEN = (14, 130, 18)
LIGHT_GREEN = (20, 200, 20)
BACKGROUND = (24, 24, 38)

home_icon = pygame.image.load("misc/Home Icon.png").convert_alpha()
replay_icon = pygame.image.load("misc/Replay Icon.png").convert_alpha()

board = [[BACKGROUND for _ in range(7)] for _ in range(6)]
red_turn = True
game_over = False
to_place = (-1, 0)

icon = pygame.Surface((80, 80)).convert_alpha()
gfxdraw.aacircle(icon, 40, 40, 40, RED)
gfxdraw.filled_circle(icon, 40, 40, 40, RED)
gfxdraw.aacircle(icon, 40, 40, 30, (138, 30, 30))
icon.set_colorkey((0, 0, 0))
pygame.display.set_icon(icon)


def draw_counter(x, y, colour):
    gfxdraw.aacircle(screen, x, y, 40, colour)
    gfxdraw.filled_circle(screen, x, y, 40, colour)
    if colour[:3] == RED:
        gfxdraw.aacircle(screen, x, y, 30, (138, 30, 30))
    elif colour[:3] == YELLOW:
        gfxdraw.aacircle(screen, x, y, 30, (171, 145, 29))


def draw_board():
    pygame.draw.rect(screen, BLUE, (323, 100, 720, 620))
    for y, j in enumerate(board):
        for x, colour in enumerate(j):
            draw_counter(x * 100 + 60 + 323, y * 100 + 60 + 100, colour)


def draw_arrows():
    global to_place
    for x, colour in enumerate(board[0]):
        if colour == BACKGROUND:
            if pygame.Rect(x * 100 + 343, 30, 80, 40).collidepoint(pygame.mouse.get_pos()):
                # Draw ghost
                for y in range(5, -1, -1):  # Goes backwards through the y, bottom to top
                    if board[y][x] == BACKGROUND:
                        to_place = y, x
                        if red_turn:
                            draw_counter(x * 100 + 60 + 323, y * 100 + 60 + 100, (200, 20, 20, 100))
                        else:
                            draw_counter(x * 100 + 60 + 323, y * 100 + 60 + 100, (245, 201, 7, 100))
                        break
                fill = LIGHT_GREEN
            else:
                fill = DARK_GREEN
            gfxdraw.aatrigon(screen, x * 100 + 343, 30, x * 100 + 423, 30, x * 100 + 383, 70, fill)
            gfxdraw.filled_trigon(screen, x * 100 + 343, 30, x * 100 + 423, 30, x * 100 + 383, 70, fill)


def check_win():
    global game_over
    game_over_line = ((0, 0), (0, 0))
    for y, j in enumerate(board):
        for check in range(4):  # Checks straight along x
            if j[check] == j[check+1] == j[check+2] == j[check+3] != BACKGROUND:
                game_over_line = ((y, check), (y, check+3))

        for x, i in enumerate(j):
            for check in range(3):  # Checks straight along y
                if board[check][x] == board[check+1][x] == board[check+2][x] == board[check+3][x] != BACKGROUND:
                    game_over_line = ((check, x), (check + 3, x))

            for check_y in range(3):  # Checks diagonals
                for check_x in range(4):
                    if board[check_y][check_x] == board[check_y+1][check_x+1] == board[check_y+2][check_x+2] == board[check_y+3][check_x+3] != BACKGROUND:
                        game_over_line = ((check_y, check_x), (check_y+3, check_x+3))
                    elif board[check_y][check_x+3] == board[check_y+1][check_x+2] == board[check_y+2][check_x+1] == board[check_y+3][check_x] != BACKGROUND:
                        game_over_line = ((check_y, check_x+3), (check_y+3, check_x))

    if game_over_line != ((0, 0), (0, 0)):
        game_over = True
        pygame.draw.line(screen, (240, 240, 240),
                         (game_over_line[0][1] * 100 + 383, game_over_line[0][0] * 100 + 60 + 100),
                         (game_over_line[1][1] * 100 + 383, game_over_line[1][0] * 100 + 60 + 100), 5)


def draw_game_over_screen():
    gfxdraw.filled_polygon(screen, ((0, 0), (0, SCREEN_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT), (SCREEN_WIDTH, 0)), (0, 0, 0, 100))
    screen.blit(home_icon, (SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//2 - 50))
    screen.blit(replay_icon, (SCREEN_WIDTH//2 + 150, SCREEN_HEIGHT//2 - 50))


def reset():
    global board, red_turn, game_over, to_place
    board = [[BACKGROUND for _ in range(7)] for _ in range(6)]
    red_turn = True
    game_over = False
    to_place = (-1, 0)


def connect4():
    global red_turn, to_place, game_over

    SCREEN_WIDTH, SCREEN_HEIGHT = 1344, 768
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Connect 4")
    icon = pygame.Surface((80, 80)).convert_alpha()
    gfxdraw.aacircle(icon, 40, 40, 40, RED)
    gfxdraw.filled_circle(icon, 40, 40, 40, RED)
    gfxdraw.aacircle(icon, 40, 40, 30, (138, 30, 30))
    icon.set_colorkey((0, 0, 0))
    pygame.display.set_icon(icon)

    running = True
    while running:
        timer.tick(FPS)

        to_place = (-1, 0)

        screen.fill(BACKGROUND)
        draw_board()
        check_win()
        if not game_over:
            draw_arrows()
        else:
            draw_game_over_screen()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
                if to_place != (-1, 0):
                    if red_turn:
                        board[to_place[0]][to_place[1]] = RED
                    else:
                        board[to_place[0]][to_place[1]] = YELLOW
                    red_turn = not red_turn
                if game_over:
                    if pygame.Rect(SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//2 - 50, 100, 100).collidepoint(pygame.mouse.get_pos()):
                        running = False  # Clicked the Home button
                    if pygame.Rect(SCREEN_WIDTH//2 + 150, SCREEN_HEIGHT//2 - 50, 100, 100).collidepoint(pygame.mouse.get_pos()):
                        reset()  # Clicked the Replay button

        pygame.display.update()

    reset()


if __name__ == "__main__":
    connect4()
    pygame.quit()
