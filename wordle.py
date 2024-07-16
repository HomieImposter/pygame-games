import pygame
import random
import math
from pygame import gfxdraw
pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Wordle")
pygame.display.set_icon(pygame.image.load("wordle-assets/Wordle Logo.png"))
timer = pygame.time.Clock()
FPS = 60
font80 = pygame.font.SysFont("helvetica.ttf", 80)
font30 = pygame.font.SysFont("helvetica.ttf", 30)

# Define colours
BLACK = (18, 18, 19)
DARK_GREY = (58, 58, 60)
LIGHT_GREY = (58, 58, 61)  # Bit bodged icl
WHITE = (248, 248, 248)
YELLOW = (181, 159, 59)
GREEN = (83, 141, 78)

home_icon = pygame.image.load("misc/Home Icon.png").convert_alpha()
replay_icon = pygame.image.load("misc/Replay Icon.png").convert_alpha()

# Other game related stuff
animation_in_progress = False
animation = "None"
won = False
lost = False
game_over = False
current_line = 0
entry = ''
board = [[('', DARK_GREY) for column in range(5)] for row in range(6)]

# Global animation variables
flip = [0, 0]  # Letter index, time in frames
flip_time = 20  # How long the flipping sequence for each letter is in frames
shake = 0  # How far through the shaking animation we are, in frames
shake_time = 30  # How long to shake for, in frames
shake_reason = ''
bounces = [1, 1, 1, 1, 1]  # Letter index, time in frames
bounce_time = 30  # How long each letter should bounce for
lose_countdown = 3 * 60  # How long to display losing message

# Get word lists from file
with open("wordle-assets/combined_wordlist.txt") as file:
    valid_words = [word[:-1] for word in file][1:]  # Removes inital comment line and newline characters
with open("wordle-assets/shuffled_real_wordles.txt") as file:
    valid_answers = [word[:-1] for word in file][1:]

answer = random.choice(valid_answers)


def draw_board():
    for y, line in enumerate(board):
        if animation_in_progress and animation != "Shake" and y == current_line:
            continue
        for x, square in enumerate(line):
            width = 0
            if square[1] == DARK_GREY:
                width = 3
            draw_x = x * 90 + 415
            draw_x += math.sin(shake) * math.pi * 2 if y == current_line else 0
            draw_y = y * 90 + 90
            pygame.draw.rect(screen, square[1], (draw_x, draw_y, 80, 80), width)

            if y == current_line:
                char = font80.render(entry.ljust(5)[x].upper(), True, WHITE)
            else:
                char = font80.render(square[0], True, WHITE)
            char_rect = char.get_rect(center=(draw_x + 39, draw_y + 41))
            screen.blit(char, char_rect)


def popup(text):
    shake_text = font30.render(text, True, (10, 10, 10))
    shake_rect = shake_text.get_rect(centerx=SCREEN_WIDTH / 2, centery=45)
    shake_bg = pygame.Rect(shake_rect.x - 8, shake_rect.y - 8, shake_rect.w + 16, shake_rect.h + 16)
    pygame.draw.rect(screen, WHITE, shake_bg, 0, 8)
    screen.blit(shake_text, shake_rect)


def shake_animation():
    global animation_in_progress, animation, shake

    shake += 1

    popup(shake_reason)

    if shake == shake_time:
        animation_in_progress = False
        shake = 0


def flip_animation():
    global animation_in_progress, animation, entry
    global flip, current_line, won, lost, game_over

    # Draw the flipping square in its current state of animation
    square = pygame.Surface((80, 80))
    square.fill(BLACK)
    if flip[1] <= flip_time / 2:
        pygame.draw.rect(square, DARK_GREY, (0, 0, 80, 80), 3)
    else:
        pygame.draw.rect(square, board[current_line][flip[0]][1], (0, 0, 80, 80))

    char = font80.render(board[current_line][flip[0]][0], True, WHITE)
    char_rect = char.get_rect(center=(39, 41))
    square.blit(char, char_rect)

    square = pygame.transform.smoothscale(square, (80, 80 * abs((flip[1] / (flip_time / 2)) - 1)))
    square_rect = square.get_rect(center=(flip[0] * 90 + 455, current_line * 90 + 130))
    screen.blit(square, square_rect)

    # Draw the rest of the row
    for x, square in enumerate(board[current_line]):
        if x == flip[0]:
            continue
        draw_x = x * 90 + 415
        draw_y = current_line * 90 + 90
        if x < flip[0]:  # To the left of the flipping square; flipped
            pygame.draw.rect(screen, square[1], (draw_x, draw_y, 80, 80))
        elif x > flip[0]:  # To the right of the flipping square; unflipped
            pygame.draw.rect(screen, DARK_GREY, (draw_x, draw_y, 80, 80), 3)

        char = font80.render(square[0], True, WHITE)
        char_rect = char.get_rect(center=(draw_x + 39, draw_y + 41))
        screen.blit(char, char_rect)

    # Increase the letter index and time on each letter accordingly
    flip[1] += 1
    if flip[1] >= flip_time:
        flip[0] += 1
        flip[1] = 0

    if flip[0] >= 5:  # All letters flipped, end animation
        animation_in_progress = False
        flip = [0, 0]
        entry = ''

        # Check win condition
        greens = [x for x in board[current_line] if x[1] == GREEN]
        if len(greens) == 5:
            won = True
            animation_in_progress = True
            animation = "Win"
            return

        # Check lose condition
        current_line += 1
        if current_line >= 6 and not won:
            lost = True
            animation_in_progress = True
            animation = "Lose"

        return


def win_animation():
    global bounces, animation_in_progress, game_over, current_line

    comments = ["Lucky!", "Genius!", "Amazing!", "Formidable!", "Nice one!", "Phew!"]
    popup(comments[current_line])

    for x, square in enumerate(board[current_line]):
        draw_x = x * 90 + 415
        draw_y = current_line * 90 + 90
        draw_y -= 15 * (math.sin(0.21 * bounces[x] - 0.524) + 0.5)
        pygame.draw.rect(screen, GREEN, (draw_x, draw_y, 80, 80))

        char = font80.render(square[0], True, WHITE)
        char_rect = char.get_rect(center=(draw_x + 39, draw_y + 41))
        screen.blit(char, char_rect)

    for i, bounce in enumerate(bounces):
        if i == 0 and bounce != 0:
            bounces[i] += 1
        elif bounce != 0 and (bounces[i - 1] >= bounce_time / 3 or bounces[i - 1] == 0):
            bounces[i] += 1
        if bounce >= bounce_time:
            bounces[i] = 0

    if bounces == [0, 0, 0, 0, 0]:
        animation_in_progress = False
        current_line += 1
        game_over = True


def lose_animation():
    global lose_countdown, animation_in_progress, game_over
    popup(f"The word was {answer.upper()}")

    lose_countdown -= 1
    if lose_countdown <= 0:
        animation_in_progress = False
        game_over = True


def check_entry():
    global animation_in_progress, animation, current_line, shake_reason
    animation_in_progress = True

    if len(entry) < 5:
        animation = "Shake"
        shake_reason = "Not enough letters"
        return

    if entry not in valid_words:
        animation = "Shake"
        shake_reason = "Not in word lists"
        return

    unchecked_letters = list(answer)
    letters = list(entry)

    # Check greens
    for char in range(5):
        if entry[char] == answer[char]:
            board[current_line][char] = (entry[char].upper(), GREEN)
            unchecked_letters[char] = ''
            letters[char] = ' '

    # Check yellows
    for char in range(5):
        if letters[char] in unchecked_letters:
            board[current_line][char] = (entry[char].upper(), YELLOW)
            unchecked_letters[unchecked_letters.index(letters[char])] = ''
            letters[char] = ' '

    # Check greys
    for char in range(5):
        if letters[char] != ' ':
            board[current_line][char] = (entry[char].upper(), LIGHT_GREY)

    animation = "Flip"


def draw_game_over_screen():
    gfxdraw.filled_polygon(screen, ((0, 0), (0, SCREEN_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT), (SCREEN_WIDTH, 0)), (0, 0, 0, 100))
    screen.blit(home_icon, (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 50))
    screen.blit(replay_icon, (SCREEN_WIDTH // 2 + 150, SCREEN_HEIGHT // 2 - 50))


def reset():
    global animation_in_progress, animation, won, lost, game_over, current_line, entry, board, flip, shake, bounces, answer

    animation_in_progress = False
    animation = "None"
    won = False
    lost = False
    game_over = False
    current_line = 0
    entry = ''
    board = [[('', DARK_GREY) for column in range(5)] for row in range(6)]
    flip = [0, 0]
    shake = 0
    bounces = [1, 1, 1, 1, 1]
    answer = random.choice(valid_answers)


def wordle():
    global entry, screen

    SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Wordle")
    pygame.display.set_icon(pygame.image.load("wordle-assets/Wordle Logo.png"))

    running = True
    while running:
        timer.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and not (animation_in_progress or game_over):
                if pygame.K_a <= event.key <= pygame.K_z:
                    if len(entry) < 5:
                        entry += event.unicode.lower()
                elif event.key == pygame.K_BACKSPACE:
                    if len(entry) > 0:
                        entry = entry[:-1]
                elif event.key == pygame.K_RETURN:
                    check_entry()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.Rect(SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 50, 100, 100).collidepoint(pygame.mouse.get_pos()):
                    running = False  # Clicked the Home button
                if pygame.Rect(SCREEN_WIDTH // 2 + 150, SCREEN_HEIGHT // 2 - 50, 100, 100).collidepoint(pygame.mouse.get_pos()):
                    reset()  # Clicked the Replay button

        screen.fill(BLACK)
        draw_board()
        if game_over:
            draw_game_over_screen()

        if animation_in_progress:
            if animation == "Shake":
                shake_animation()
            elif animation == "Flip":
                flip_animation()
            elif animation == "Win":
                win_animation()
            elif animation == "Lose":
                lose_animation()

        pygame.display.update()

    reset()


if __name__ == "__main__":
    wordle()
    pygame.quit()
