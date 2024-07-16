import pygame
import random
import math
from pygame import gfxdraw
pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1366, 768
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Hunt the Wumpus")
pygame.display.set_icon(pygame.image.load("hunt-the-wumpus-assets/Character Idle.png"))
timer = pygame.time.Clock()
FPS = 60
font = pygame.font.Font("fonts/Kenney Pixel.ttf", 50)
font2 = pygame.font.Font("fonts/Kenney Mini Square.ttf", 100)

background = pygame.image.load("hunt-the-wumpus-assets/Background.png").convert_alpha()
torch_glow = pygame.image.load("hunt-the-wumpus-assets/Torch Glow.png").convert_alpha()
fire_arrow = pygame.image.load("hunt-the-wumpus-assets/Fire Arrow.png").convert_alpha()
fire_arrow = pygame.transform.scale_by(fire_arrow, 3)
fire_arrow = pygame.transform.rotate(fire_arrow, 90)
move_arrow = pygame.image.load("hunt-the-wumpus-assets/Move Arrow.png").convert_alpha()
move_arrow = pygame.transform.scale_by(move_arrow, 3)
move_arrow = pygame.transform.rotate(move_arrow, 90)
character_idle = pygame.image.load("hunt-the-wumpus-assets/Character Idle.png").convert_alpha()
character_idle = pygame.transform.scale_by(character_idle, 3)
move_button = pygame.image.load("hunt-the-wumpus-assets/Move Button.png").convert_alpha()
move_button = pygame.transform.scale_by(move_button, 4)
fire_button = pygame.image.load("hunt-the-wumpus-assets/Fire Button.png").convert_alpha()
fire_button = pygame.transform.scale_by(fire_button, 4)
home_icon = pygame.image.load("misc/Home Icon.png").convert_alpha()
replay_icon = pygame.image.load("misc/Replay Icon.png").convert_alpha()

neighbours = [
    [1, 4, 7],
    [0, 2, 9],
    [1, 3, 11],
    [2, 4, 13],
    [0, 3, 5],
    [4, 6, 14],
    [5, 7, 16],
    [0, 6, 8],
    [7, 9, 17],
    [1, 8, 10],
    [9, 11, 18],
    [2, 10, 12],
    [11, 13, 19],
    [3, 12, 14],
    [5, 13, 15],
    [14, 16, 19],
    [6, 15, 17],
    [8, 16, 18],
    [10, 17, 19],
    [12, 15, 18]
]
caves = ["empty" for _ in range(20)]
centres = [(363, 77), (654, 286), (546, 629), (186, 633), (71, 293), (174, 325), (245, 225), (362, 187), (478, 222), (552, 321),
           (553, 444), (482, 542), (367, 581), (250, 546), (176, 447), (279, 412), (310, 311), (416, 310), (449, 408), (365, 471)]


def find_empty_caves():
    empty_caves = []
    for i, cave in enumerate(caves):
        if cave == "empty":
            empty_caves.append(i)
    return empty_caves


caves[0] = "player"
for obstacle in ["wumpus", "pit", "bat"]:
    caves[random.choice(find_empty_caves())] = obstacle

selected_button = "none"
move = True
arrow_radius = 60
won = False
lost = False
death_message = ''
WHITE = (250, 250, 250)


def draw_buttons():
    global selected_button
    selected_button = "none"
    if pygame.Rect(20, 20, 128, 64).collidepoint(pygame.mouse.get_pos()):
        screen.blit(pygame.transform.scale(move_button, (138, 74)), (15, 15))
        selected_button = "move"
    else:
        screen.blit(move_button, (20, 20))
    if pygame.Rect(600, 20, 128, 64).collidepoint(pygame.mouse.get_pos()):
        screen.blit(pygame.transform.scale(fire_button, (138, 74)), (595, 15))
        selected_button = "fire"
    else:
        screen.blit(fire_button, (600, 20))


def find_player_index():
    for i, cave in enumerate(caves):
        if cave == "player":
            player_ind = i
            return player_ind


def face(origin, target) -> float:
    # From Rotation.py
    dx = target[0] - origin[0]
    dy = target[1] - origin[1]
    if dx == 0:
        angle = 0 if dy < 0 else 180
    elif dx > 0:
        angle = -90 - math.degrees(math.atan(dy/dx))
    else:
        angle = 90 - math.degrees(math.atan(dy/dx))
    return angle


def find_arrow_centre(origin, target):
    # Caculate the intersection with a circle around character and lines between character and next cave
    gradient = (target[1] - origin[1]) / (target[0] - origin[0])
    x1 = math.sqrt(arrow_radius**2 / (1 + gradient**2))
    x2 = x1 * -1
    y1 = gradient * x1
    y2 = gradient * x2

    # Adjust for calculating arounf the origin
    x1 += origin[0]
    y1 += origin[1]
    x2 += origin[0]
    y2 += origin[1]

    # Compare which answer is actually on line segment (line crosses circle at two places)
    if min(origin[0], target[0]) < x1 < max(origin[0], target[0]) and min(origin[1], target[1]) < y1 < max(origin[1], target[1]):
        return x1, y1
    elif min(origin[0], target[0]) < x2 < max(origin[0], target[0]) and min(origin[1], target[1]) < y2 < max(origin[1], target[1]):
        return x2, y2
    else:
        raise ArithmeticError("No roots were found")


def draw_arrows():
    global selected_button

    if won or lost:
        return
    player_ind = find_player_index()

    for neighbour in neighbours[player_ind]:
        arrow_pos = find_arrow_centre(centres[player_ind], centres[neighbour])
        if move:
            rotated_arrow = pygame.transform.rotate(move_arrow, face(centres[player_ind], centres[neighbour]))
        else:
            rotated_arrow = pygame.transform.rotate(fire_arrow, face(centres[player_ind], centres[neighbour]))
        rot_arrow_rect = rotated_arrow.get_rect(center=arrow_pos)

        if rot_arrow_rect.collidepoint(pygame.mouse.get_pos()):
            rotated_arrow = pygame.transform.scale_by(rotated_arrow, 4/3)
            selected_button = f"arrow {neighbour}"

        rot_arrow_rect = rotated_arrow.get_rect(center=arrow_pos)

        screen.blit(rotated_arrow, rot_arrow_rect)


def draw_player():
    player_ind = find_player_index()

    screen.blit(torch_glow, torch_glow.get_rect(center=centres[player_ind]))
    screen.blit(character_idle, character_idle.get_rect(center=centres[player_ind]))


def draw_text():
    texts = []
    player_ind = find_player_index()
    for neighbour in neighbours[player_ind]:
        if caves[neighbour] == "wumpus":
            texts.append("You smell a Wumpus")
        elif caves[neighbour] == "pit":
            texts.append("You feel a gust of wind")
        elif caves[neighbour] == "bat":
            texts.append("You hear flapping")

    for i, text in enumerate(texts):
        text = font.render(text, True, WHITE)
        screen.blit(text, (820, 70 + i * 50))


def move_player(index):
    global lost, death_message
    player_ind = find_player_index()
    if caves[index] == "wumpus":
        if random.randint(0, 1) == 1:
            # Wumpus is startled and moves to an empty cave
            caves[random.choice(find_empty_caves())] = "wumpus"
        else:
            lost = True
            death_message = "You got eaten by the Wumpus"
    elif caves[index] == "bat":
        # Bat moves player to random location
        move_player(random.randint(0, 20))
        caves[random.choice(find_empty_caves())] = "bat"  # Bat moves to a random empty cave
        caves[index] = "empty"
        return
    elif caves[index] == "pit":
        lost = True
        death_message = "You fell in a pit"
    caves[index] = "player"
    caves[player_ind] = "empty"


def fire(index):
    global won, lost
    if caves[index] == "wumpus":
        won = True
    else:  # Missed
        if random.randint(0, 4) != 4:  # Wumpus is startled with 75% chance
            for i, cave in enumerate(caves):
                if cave == "wumpus":
                    caves[i] = "empty"
            caves[random.choice(find_empty_caves())] = "wumpus"


def draw_game_over_screen():
    if won or lost:
        gfxdraw.filled_polygon(screen, ((0, 0), (0, SCREEN_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT), (SCREEN_WIDTH, 0)), (0, 0, 0, 100))
        screen.blit(home_icon, (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 + 100))
        screen.blit(replay_icon, (SCREEN_WIDTH // 2 + 150, SCREEN_HEIGHT // 2 + 100))
    if lost:
        lost_text = font2.render("YOU LOSE", False, WHITE)
        lost_rect = lost_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 20))
        screen.blit(lost_text, lost_rect)

        death_text = font.render(death_message, False, WHITE)
        death_rect = death_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 40))
        screen.blit(death_text, death_rect)
    elif won:
        won_text = font2.render("YOU WIN", False, WHITE)
        won_rect = won_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        screen.blit(won_text, won_rect)


def reset():
    global caves, move, won, lost

    caves = ["empty" for _ in range(20)]
    caves[0] = "player"
    for obstacle in ["wumpus", "pit", "bat"]:
        caves[random.choice(find_empty_caves())] = obstacle
    move = True
    won = False
    lost = False


def hunt_the_wumpus():
    global move

    SCREEN_WIDTH, SCREEN_HEIGHT = 1366, 768
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Hunt the Wumpus")
    pygame.display.set_icon(pygame.image.load("hunt-the-wumpus-assets/Character Idle.png"))

    running = True
    while running:
        timer.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not (won or lost):
                    if selected_button == "move":
                        move = True
                    elif selected_button == "fire":
                        move = False
                    elif selected_button.split()[0] == "arrow":
                        cave_ind = int(selected_button.split()[1])
                        if move:
                            move_player(cave_ind)
                        else:
                            fire(cave_ind)
                else:
                    if pygame.Rect(SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//2 + 100, 100, 100).collidepoint(pygame.mouse.get_pos()):
                        running = False  # Clicked the Home button
                    if pygame.Rect(SCREEN_WIDTH//2 + 150, SCREEN_HEIGHT//2 + 100, 100, 100).collidepoint(pygame.mouse.get_pos()):
                        reset()  # Clicked the Replay button

        screen.fill((24, 24, 38))
        screen.blit(background, (0, 0))

        draw_buttons()
        draw_player()
        draw_arrows()
        draw_text()
        draw_game_over_screen()

        pygame.display.update()

    reset()


if __name__ == "__main__":
    hunt_the_wumpus()
    pygame.quit()
