import pygame
import random
import copy
pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1366, 768
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake")
font100 = pygame.font.SysFont("franklingothic", 100)
font40 = pygame.font.SysFont("franklingothic", 40)
timer = pygame.time.Clock()
FPS = 60

display_board = pygame.Surface((17 * 46, 15 * 46))  # Each square is 46x46
home_icon = pygame.image.load("misc/Home Icon.png").convert_alpha()
replay_icon = pygame.image.load("misc/Replay Icon.png").convert_alpha()

with open("snake-assets/highscore.txt") as file:
    highscore = int(file.readline())

board = [[[0, 0] for x in range(17)] for y in range(15)]
board[7][12] = [1, 0]
board[7][4] = [2, 0]
board[7][3] = [2, 1]
board[7][2] = [2, 2]
direction = 'E'
next_dir = ['', 0]
move_counter = 0
length = 3
paused = True
game_over = False
speed = 0.1
score = 0

snake_colour = (44, 128, 29)  # Green, by default
RED = (199, 26, 26)
BLACK = (9, 10, 15)
WHITE = (225, 226, 235)


def set_icon():
    icon = pygame.Surface((32, 32))
    icon.fill((44, 44, 71))
    pygame.draw.rect(icon, snake_colour, (2, 2, 28, 12))
    pygame.draw.rect(icon, snake_colour, (2, 2, 12, 28))
    pygame.draw.rect(icon, snake_colour, (2, 18, 28, 12))
    pygame.draw.circle(icon, BLACK, (26, 21), 2)
    pygame.draw.circle(icon, BLACK, (26, 26), 2)
    pygame.display.set_icon(icon)


def reset():
    global board, direction, next_dir, move_counter, length, paused, game_over, score
    board = [[[0, 0] for _ in range(17)] for _ in range(15)]
    board[7][12] = [1, 0]
    board[7][4] = [2, 0]
    board[7][3] = [2, 1]
    board[7][2] = [2, 2]
    direction = 'E'
    next_dir = ['', 0]
    move_counter = 0
    length = 3
    paused = True
    game_over = False
    score = 0


def draw_board():
    display_board.fill((44, 44, 71))
    for i in range(0, 17, 2):
        for j in range(0, 15):
            pygame.draw.rect(display_board, (32, 32, 54), (46 * i + 46 * (j % 2), 46 * j, 46, 46))

    for grid_y, row in enumerate(board):
        for grid_x, square in enumerate(row):
            x = grid_x * 46
            y = grid_y * 46

            if square[0] == 1:  # Apple
                pygame.draw.circle(display_board, RED, (x + 23, y + 23), 18)
            elif square[0] == 2:  # Snake
                pygame.draw.rect(display_board, snake_colour, (x + 3, y + 3, 40, 40))
                if square[1] == 0:  # Head - Draws the eyes in the right direction
                    eyes = []
                    eyes = [1, 2] if direction == 'N' else eyes
                    eyes = [2, 3] if direction == 'E' else eyes
                    eyes = [3, 4] if direction == 'S' else eyes
                    eyes = [4, 1] if direction == 'W' else eyes

                    pygame.draw.circle(display_board, BLACK, (x + 14, y + 14), 5) if 1 in eyes else None
                    pygame.draw.circle(display_board, BLACK, (x + 32, y + 14), 5) if 2 in eyes else None
                    pygame.draw.circle(display_board, BLACK, (x + 32, y + 32), 5) if 3 in eyes else None
                    pygame.draw.circle(display_board, BLACK, (x + 14, y + 32), 5) if 4 in eyes else None
                else:  # Body - Fills in the gaps
                    if grid_x > 0 and board[grid_y][grid_x-1] == [2, square[1]-1]:
                        pygame.draw.rect(display_board, snake_colour, (x - 3, y + 3, 6, 40))
                    elif grid_x < 16 and board[grid_y][grid_x+1] == [2, square[1]-1]:
                        pygame.draw.rect(display_board, snake_colour, (x + 43, y + 3, 6, 40))
                    elif grid_y > 0 and board[grid_y-1][grid_x] == [2, square[1]-1]:
                        pygame.draw.rect(display_board, snake_colour, (x + 3, y - 3, 40, 6))
                    elif grid_y < 14 and board[grid_y+1][grid_x] == [2, square[1]-1]:
                        pygame.draw.rect(display_board, snake_colour, (x + 3, y + 43, 40, 6))

    screen.blit(display_board, (292, 39))


def draw_displays():
    if paused:
        text = "Press any key to play"
    elif game_over:
        text = "Game over!"
        screen.blit(home_icon, (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 + 100))
        screen.blit(replay_icon, (SCREEN_WIDTH // 2 + 150, SCREEN_HEIGHT // 2 + 100))
    else:
        text = ''
    display_text = font100.render(text, True, WHITE)
    display_rect = display_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
    screen.blit(display_text, display_rect)


def move():
    global move_counter, board, direction, next_dir, length, game_over, score

    if paused or game_over:
        return

    move_counter -= 1
    if move_counter > 0:
        return
    move_counter = FPS * speed  # Move every 0.3 secs

    if next_dir[0] != '':
        direction = next_dir[0]

    next_board = copy.deepcopy(board)
    fruit_eaten = False

    for y, j in enumerate(board):
        for x, i in enumerate(j):
            if i[0] == 2:
                if i[1] == 0:  # Head
                    if (y == 0 and direction == 'N') or (y == 14 and direction == 'S') or (x == 0 and direction == 'W') or (x == 16 and direction == 'E'):
                        game_over = True  # Hit edge of map
                        return

                    if y > 0 and direction == 'N':
                        if board[y-1][x] == [1, 0]:  # Hit fruit
                            length += 1
                            fruit_eaten = True
                        elif board[y-1][x] != [0, 0]:  # Hit self
                            game_over = True
                            return
                        next_board[y - 1][x] = [2, 0]

                    elif x < 16 and direction == 'E':
                        next_board[y][x+1] = [2, 0]
                        if board[y][x+1] == [1, 0]:
                            length += 1
                            fruit_eaten = True
                        elif board[y][x+1] != [0, 0]:
                            game_over = True
                            return

                    elif y < 14 and direction == 'S':
                        next_board[y+1][x] = [2, 0]
                        if board[y+1][x] == [1, 0]:
                            length += 1
                            fruit_eaten = True
                        elif board[y+1][x] != [0, 0]:
                            game_over = True
                            return

                    elif x > 0 and direction == 'W':
                        next_board[y][x-1] = [2, 0]
                        if board[y][x-1] == [1, 0]:
                            length += 1
                            fruit_eaten = True
                        elif board[y][x-1] != [0, 0]:
                            game_over = True
                            return

                    next_board[y][x] = [2, 1]
                else:  # Body
                    next_board[y][x][1] += 1
                    if next_board[y][x][1] == length:
                        next_board[y][x] = [0, 0]

    board = next_board
    if fruit_eaten:
        generate_fruit()
        score += 1
        if score > highscore:
            with open("snake-assets/highscore.txt", 'w') as file:
                file.write(str(score))


def generate_fruit():
    global board
    free_spaces = []
    for y, j in enumerate(board):
        for x, i in enumerate(j):
            if i == [0, 0]:
                free_spaces.append((y, x))
    fruit_y, fruit_x = random.choice(free_spaces)
    board[fruit_y][fruit_x] = [1, 0]


def draw_scores():
    global highscore

    if score > highscore:
        highscore = score

    score_text = font40.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))
    highscore_text = font40.render(f"High Score: {highscore}", True, (255, 255, 255))
    screen.blit(highscore_text, (SCREEN_WIDTH - 10 - highscore_text.get_width(), 10))


def snake():
    global next_dir, paused, snake_colour, speed

    set_icon()

    running = True
    while running:
        timer.tick(FPS)

        if next_dir[1] <= 0:
            next_dir = ['', 1]
        next_dir[1] -= 1

        screen.fill((24, 24, 38))
        draw_board()
        move()
        draw_displays()
        draw_scores()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if game_over:
                    reset()
                paused = False
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    if direction != 'S':
                        next_dir = ['N', 30]
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    if direction != 'W':
                        next_dir = ['E', 30]
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    if direction != 'N':
                        next_dir = ['S', 30]
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    if direction != 'E':
                        next_dir = ['W', 30]
                elif event.key == pygame.K_SPACE:
                    snake_colour = (40, 46, 173) if snake_colour == (44, 128, 29) else (44, 128, 29)
                    set_icon()
                elif event.key == pygame.K_p:
                    speed = 0.1 if speed == 0.3 else 0.3
                elif event.key == pygame.K_o:
                    speed = 0.05 if speed != 0.05 else 0.1
            elif event.type == pygame.MOUSEBUTTONDOWN and game_over:
                if pygame.Rect(SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 + 100, 100, 100).collidepoint(pygame.mouse.get_pos()):
                    running = False  # Clicked the Home button
                if pygame.Rect(SCREEN_WIDTH // 2 + 150, SCREEN_HEIGHT // 2 + 100, 100, 100).collidepoint(pygame.mouse.get_pos()):
                    reset()  # Clicked the Replay button

        pygame.display.update()

    reset()


if __name__ == "__main__":
    snake()
    pygame.quit()
