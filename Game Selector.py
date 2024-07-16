import pygame
import json
from chess import chess
from blackjack import blackjack
from solitaire import solitaire
from connect4 import connect4
from hunt_the_wumpus import hunt_the_wumpus
from minesweeper import minesweeper
from tetris import tetris
from wordle import wordle
from snake import snake
from uno import uno
from roulette import roulette
import feedback

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1366, 768
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Game Selector")
pygame.display.set_icon(pygame.image.load("misc/Python Logo.png"))
timer = pygame.time.Clock()
FPS = 60
font = pygame.font.SysFont("franklingothic", 50)
font2 = pygame.font.SysFont("franklingothic", 40)

with open("misc/descriptions.json") as file:
    descriptions: dict = json.load(file)

total_lines = 218  # From this file
total_lines += feedback.line_count
for i in descriptions.keys():
    total_lines += descriptions[i]["Lines"]
selected_game = "none"
highlighted_game = "none"
selected_box = -1
run = True
games = ["Blackjack", "Chess", "Connect 4", "Hunt the Wumpus", "Minesweeper", "Roulette", "Snake", "Solitaire", "Tetris", "Uno", "Wordle"]
thumbnails = [pygame.image.load(f"thumbnails/{game}.png").convert_alpha() for game in games]
home = pygame.image.load("misc/Home Icon.png").convert_alpha()
home = pygame.transform.smoothscale(home, (80, 80))


def draw_thumbnails():
    global selected_box

    selected_box = -1
    title = font.render("Choose a game to play", True, (255, 255, 255))
    screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 25)))

    for i in range(len(games)):
        x = (i % 4) * 336 + 20
        y = (i // 4) * 240 + 48
        if pygame.Rect(x, y, 316, 220).collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(screen, (245, 218, 15), (x - 2, y - 2, 320, 224))
            selected_box = i
        pygame.draw.rect(screen, (204, 67, 12), (x, y, 316, 220))
        name = font.render(games[i], True, (255, 255, 255))
        screen.blit(name, name.get_rect(center=(x + 158, y + 200)))
        screen.blit(thumbnails[i], (x + 5, y + 5))

    total_lines_text = font.render(f"Total lines: {total_lines}", True, (41, 41, 64))
    screen.blit(total_lines_text, (SCREEN_WIDTH - 20 - total_lines_text.get_width(), SCREEN_HEIGHT - 15 - total_lines_text.get_height()))


def draw_info():
    pygame.draw.rect(screen, (204, 67, 12), (200, 30, 966, 708))
    pygame.draw.rect(screen, (163, 53, 8), (215, 45, 316, 678))
    thumbnail = thumbnails[games.index(highlighted_game)]
    screen.blit(thumbnail, (220, 50))
    name = font.render(highlighted_game, True, (255, 255, 255))
    screen.blit(name, name.get_rect(center=(373, 250)))

    screen.blit(font2.render("Originally released:", True, (255, 255, 255)), (220, 280))
    screen.blit(font2.render(f"{descriptions[highlighted_game]['Released']}", True, (255, 255, 255)), (220, 310))

    screen.blit(font2.render("Lines of code:", True, (255, 255, 255)), (220, 350))
    screen.blit(font2.render(f"{descriptions[highlighted_game]['Lines']}", True, (255, 255, 255)), (220, 380))

    screen.blit(font2.render("Programmed by:", True, (255, 255, 255)), (220, 420))
    screen.blit(font2.render(f"{descriptions[highlighted_game]['Author']}", True, (255, 255, 255)), (220, 450))

    screen.blit(font2.render("Players:", True, (255, 255, 255)), (220, 490))
    screen.blit(font2.render(f"{descriptions[highlighted_game]['Players']}", True, (255, 255, 255)), (220, 520))

    description = descriptions[highlighted_game]['Description'].split('\n')
    for i, line in enumerate(description):
        screen.blit(font2.render(line, True, (255, 255, 255)), (550, 50 + i * 30))

    play_rect = pygame.Rect(550, 653, 300, 70)
    if play_rect.collidepoint(pygame.mouse.get_pos()):
        pygame.draw.rect(screen, (6, 92, 19), play_rect)
    else:
        pygame.draw.rect(screen, (8, 135, 27), play_rect)
    play_text = font.render("Play", True, (255, 255, 255))
    screen.blit(play_text, play_text.get_rect(center=(700, 688)))

    feedback_rect = pygame.Rect(870, 653, 275, 70)
    if feedback_rect.collidepoint(pygame.mouse.get_pos()):
        pygame.draw.rect(screen, (148, 18, 18), feedback_rect)
    else:
        pygame.draw.rect(screen, (222, 27, 27), feedback_rect)
    feedback_text = font.render("Feedback", True, (255, 255, 255))
    screen.blit(feedback_text, feedback_text.get_rect(center=(1007, 688)))

    screen.blit(home, (30, 30))


def main():
    global selected_game, run, screen, highlighted_game, timer

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Game Selector")
    pygame.display.set_icon(pygame.image.load("misc/Python Logo.png"))
    timer = pygame.time.Clock()

    feedback_open = False

    running = True
    while running:
        timer.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                selected_game = "none"
                running = False
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
                if feedback_open:
                    if pygame.Rect(30, 30, 100, 100).collidepoint(pygame.mouse.get_pos()):
                        # Clicked Back
                        feedback_open = False
                        feedback.reset()
                    if pygame.Rect((533, 673, 300, 70)).collidepoint(pygame.mouse.get_pos()):
                        # Clicked Submit
                        feedback.submit()
                else:
                    if highlighted_game != "none":
                        if pygame.Rect(550, 653, 300, 70).collidepoint(pygame.mouse.get_pos()):
                            # Clicked Play
                            selected_game = highlighted_game
                            running = False
                        elif pygame.Rect(870, 653, 275, 70).collidepoint(pygame.mouse.get_pos()):
                            # Clicked Feedback
                            feedback_open = True
                        elif pygame.Rect(30, 30, 100, 100).collidepoint(pygame.mouse.get_pos()):
                            # Clicked Home
                            highlighted_game = "none"
                    elif selected_box != -1:
                        highlighted_game = games[selected_box]
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if feedback_open:
                        feedback_open = False
                        feedback.reset()
                    else:
                        highlighted_game = "none"
                elif feedback_open:
                    if event.key == pygame.K_BACKSPACE:
                        feedback.enter('\b')
                    elif event.key == pygame.K_RETURN:
                        feedback.enter('\n')
            elif event.type == pygame.TEXTINPUT:
                feedback.enter(event.text)

        screen.fill((24, 24, 38))
        if feedback_open:
            feedback.feedback(screen, highlighted_game)
        else:
            if highlighted_game == "none":
                pygame.display.set_caption("Game Selector")
                draw_thumbnails()
            else:
                pygame.display.set_caption(f"Game Selector - {highlighted_game}")
                draw_info()

        pygame.display.update()


while run:
    if selected_game == "Chess":
        chess()
        selected_game = "none"
    elif selected_game == "Connect 4":
        connect4()
        selected_game = "none"
    elif selected_game == "Hunt the Wumpus":
        hunt_the_wumpus()
        selected_game = "none"
    elif selected_game == "Minesweeper":
        minesweeper()
        selected_game = "none"
    elif selected_game == "Blackjack":
        blackjack()
        selected_game = "none"
    elif selected_game == "Solitaire":
        solitaire()
        selected_game = "none"
    elif selected_game == "Tetris":
        tetris()
        selected_game = "none"
    elif selected_game == "Wordle":
        wordle()
        selected_game = "none"
    elif selected_game == "Snake":
        snake()
        selected_game = "none"
    elif selected_game == "Uno":
        uno()
        selected_game = "none"
    elif selected_game == "Roulette":
        roulette()
        selected_game = "none"
    else:
        main()
        highlighted_game = "none"

pygame.quit()
