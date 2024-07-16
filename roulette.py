import pygame
import random
import math
from pygame import gfxdraw
pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1366, 768
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Roulette")
pygame.display.set_icon(pygame.image.load("roulette-assets/Roulette Wheel.png"))
timer = pygame.time.Clock()
FPS = 60
font = pygame.font.Font("fonts/coolvetica.otf", 35)
font2 = pygame.font.Font("fonts/coolvetica.otf", 70)

background = pygame.image.load("roulette-assets/Roulette Table.png").convert_alpha()
wheel = pygame.image.load("roulette-assets/Roulette Wheel 2.png").convert_alpha()
ball = pygame.image.load("roulette-assets/Ball.png").convert_alpha()
rake = pygame.image.load("roulette-assets/Rake.png").convert_alpha()
chips = [pygame.image.load(f"roulette-assets/chips/Betting Chip {ending}.png").convert_alpha() for ending in ['5', '10', '25', '50', '100', '1k', '10k', '100k', '1m']]
home_icon = pygame.image.load("misc/Home Icon.png").convert_alpha()
replay_icon = pygame.image.load("misc/Replay Icon.png").convert_alpha()

ball_pos = [(296, 450), (271, 144), (321, 448), (183, 192), (410, 401), (143, 283),  # 0-5
            (450, 309), (166, 381), (425, 212), (246, 442), (346, 150),  # 6-10
            (183, 400), (409, 192), (246, 150), (346, 442), (167, 212),  # 11-15
            (426, 381), (143, 309), (450, 283), (438, 234), (155, 358),  # 16-20
            (446, 334), (146, 258), (391, 418), (202, 175), (369, 161),  # 21-25
            (223, 432), (321, 145), (270, 449), (390, 175), (201, 418),  # 26-30
            (446, 258), (146, 334), (438, 358), (155, 234), (370, 432),  # 30-35
            (223, 161), (296, 142)]  # 36 & 00
inside_bets = [pygame.Rect(71.7 * (i % 3) + 826.7, 50.7 * (i // 3) + 86.8, 71.7, 50.7) for i in range(36)]
inside_bets.insert(0, pygame.Rect(826.7, 36.1, 107.6, 50.6))
inside_bets.append(pygame.Rect(934.3, 36.1, 107.6, 50.6))

angle = 0
incr = 0
ball_num = -1
highlighted_numbers = []
in_hand = pygame.Surface((0, 0))
bets = []
balance = 25
moving_chips = []
rake_pos = SCREEN_HEIGHT
clear_chips = False
game_over = False

greyed_chips = []
for chip in chips:
    greyed_chip = chip.copy()
    for y in range(45):
        for x in range(45):
            col = greyed_chip.get_at((x, y))
            avg = (col[0] + col[1] + col[2]) / 3
            new_col = (avg, avg, avg, col[3])
            greyed_chip.set_at((x, y), new_col)
    greyed_chips.append(greyed_chip)


class MovingChip:
    def __init__(self, pos, target, sprite, speed=20):
        self.pos = pos
        self.target = target
        self.sprite = sprite
        self.speed = speed

        distance_vetor = (self.target[0] - self.pos[0], self.target[1] - self.pos[1])
        distance = math.sqrt(distance_vetor[0] ** 2 + distance_vetor[1] ** 2)
        self.movement_vector = (distance_vetor[0] / distance * self.speed, distance_vetor[1] / distance * self.speed)

    def move(self):
        self.pos = (self.pos[0] + self.movement_vector[0], self.pos[1] + self.movement_vector[1])
        if abs(self.pos[0] - self.target[0]) < self.speed and abs(self.pos[1] - self.target[1]) < self.speed:
            self.pos = self.target

    def draw(self):
        screen.blit(self.sprite, self.sprite.get_rect(center=self.pos))


def draw_wheel():
    global angle, incr

    incr_was_zero = incr == 0

    angle += incr
    angle -= 360 if angle >= 360 else 0
    incr -= 0.02 if incr > 0 else incr

    if incr == 0 and not incr_was_zero:
        spin_over()

    rotated_wheel = wheel.copy()
    if ball_num >= 0:
        rotated_wheel.blit(ball, ball_pos[ball_num])
    rotated_wheel = pygame.transform.rotozoom(rotated_wheel, angle, 1)
    screen.blit(rotated_wheel, rotated_wheel.get_rect(center=(377, 384)))


def spin():
    global angle, incr, ball_num

    incr = 15
    angle = random.randint(0, 360)
    ball_num = random.randint(0, 37)


def spin_over():
    global clear_chips

    payed_bets = []

    for bet in bets:
        if ball_num in bet[2]:
            payouts = {1: 35, 2: 17, 3: 11, 4: 8, 5: 6, 6: 5, 12: 2, 18: 1}
            payout = payouts[len(bet[2])]

            for _ in range(payout):
                moving_chips.append(MovingChip((-50, random.randint(100, SCREEN_HEIGHT - 100)), (SCREEN_WIDTH, SCREEN_HEIGHT // 2), bet[1]))

            moving_chips.append(MovingChip(bet[0], (SCREEN_WIDTH, SCREEN_HEIGHT // 2), bet[1]))
            payed_bets.append(bet)

    for bet in payed_bets:
        if bet in bets:
            del bets[bets.index(bet)]

    if bets:
        clear_chips = True


def draw_highlighted_numbers():
    global highlighted_numbers

    if in_hand.get_width() == 0:
        return

    # Calculate which numbers should be highlighted
    highlighted_numbers = []
    chip_rect = pygame.Rect(pygame.mouse.get_pos()[0] - 20, pygame.mouse.get_pos()[1] - 20, 40, 40)

    # Inside bets
    for i, square in enumerate(inside_bets):
        if square.colliderect(chip_rect):
            highlighted_numbers.append(i)
            if pygame.Rect(755, 125, 70, 530).colliderect(chip_rect):
                highlighted_numbers.extend([i+1, i+2])
            elif pygame.Rect(1042, 125, 70, 530).colliderect(chip_rect):
                highlighted_numbers.extend([i-1, i-2])
    if highlighted_numbers == [0, 2, 37]:
        highlighted_numbers = [0, 1, 2, 3, 37]

    # Outside bets
    if not highlighted_numbers:
        # Outside bets on left
        if pygame.Rect(765, 97, 50, 588).colliderect(chip_rect):
            box = (pygame.mouse.get_pos()[1] - 86.8) // 101.3
            if box == 0:
                highlighted_numbers = [x + 1 for x in range(18)]
            elif box == 1:
                highlighted_numbers = [x + 1 for x in range(36) if x % 2]
            elif box == 2:
                highlighted_numbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
            elif box == 3:
                highlighted_numbers = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
            elif box == 4:
                highlighted_numbers = [x + 1 for x in range(36) if not x % 2]
            elif box == 5:
                highlighted_numbers = [x + 19 for x in range(18)]
        # Outside bets on right
        elif pygame.Rect(1053.4, 97, 50, 588).colliderect(chip_rect):
            box = (pygame.mouse.get_pos()[1] - 86.8) // 202.7
            if box == 0:
                highlighted_numbers = [x + 1 for x in range(12)]
            elif box == 1:
                highlighted_numbers = [x + 13 for x in range(12)]
            elif box == 2:
                highlighted_numbers = [x + 25 for x in range(12)]
        # Outside bets on bottom
        elif pygame.Rect(836.7, 704.7, 195.2, 30.7).colliderect(chip_rect):
            box = (pygame.mouse.get_pos()[0] - 826.7) // 71.7
            if box == 0:
                highlighted_numbers = [x + 1 for x in range(36) if not x % 3]
            elif box == 1:
                highlighted_numbers = [x + 1 for x in range(36) if not (x - 1) % 3]
            elif box == 2:
                highlighted_numbers = [x + 1 for x in range(36) if not (x - 2) % 3]

    # Draw the highlighted numbers
    for num in highlighted_numbers:
        if num == 0:
            pygame.draw.polygon(screen, (165, 207, 20), ((826.7, 36.1), (880.5, 22.6), (934.3, 36.1), (934.3, 86.8), (826.7, 86.8)))
        elif num == 37:
            pygame.draw.polygon(screen, (165, 207, 20), ((934.3, 36.1), (988.1, 22.6), (1041.9, 36.1), (1041.9, 86.8), (934.3, 86.8)))
        else:
            pygame.draw.rect(screen, (165, 207, 20), inside_bets[num])


def get_chip_value(ind):
    return [5, 10, 25, 50, 100, 1_000, 10_000, 100_000, 1_000_000][ind]


def draw_chips():
    global balance

    # Draw the ones at the side
    for i, chip in enumerate(chips):
        if get_chip_value(i) <= balance:
            screen.blit(chip, (1217, i * 60 + 121))
        else:
            screen.blit(greyed_chips[i], (1217, i * 60 + 121))

    # Draw chips on the board
    for bet in bets:
        screen.blit(bet[1], bet[1].get_rect(center=bet[0]))

    # Draw the chip in hand
    screen.blit(in_hand, in_hand.get_rect(center=pygame.mouse.get_pos()))

    # Draw moving chips
    for i, chip in enumerate(moving_chips):
        chip.move()
        chip.draw()
        if chip.pos == chip.target:
            balance += get_chip_value(chips.index(chip.sprite))
            del moving_chips[i]


def place_bet():
    global highlighted_numbers

    bet = [pygame.mouse.get_pos(), in_hand, highlighted_numbers]
    highlighted_numbers = []
    bets.append(bet)


def draw_hud():
    balance_text = font.render(f"Balance: {balance:,}", True, (255, 255, 255))
    screen.blit(balance_text, (10, 2))


def pick_up_chip():
    global in_hand, balance

    if pygame.Rect(1217, 121, 45, 525).collidepoint(pygame.mouse.get_pos()):
        y = pygame.mouse.get_pos()[1] - 121
        if y % 60 <= 45 and get_chip_value(y // 60) <= balance:
            in_hand = chips[y // 60]
            balance -= get_chip_value(y // 60)

    for i, bet in enumerate(bets):
        if bet[1].get_rect(center=bet[0]).collidepoint(pygame.mouse.get_pos()):
            in_hand = bet[1]
            del bets[i]


def rake_chips():
    global rake_pos, clear_chips

    rake_pos -= 40
    screen.blit(rake, (724.3, rake_pos))

    for i, bet in enumerate(bets):
        if bet[0][1] >= rake_pos + 538:
            del bets[i]

    if rake_pos < -565:
        clear_chips = False
        rake_pos = SCREEN_HEIGHT


def draw_game_over_screen():
    gfxdraw.filled_polygon(screen, ((0, 0), (0, SCREEN_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT), (SCREEN_WIDTH, 0)), (0, 0, 0, 200))
    game_over_text = font2.render("You've Gone Bankrupt!", True, (255, 255, 255))
    screen.blit(game_over_text, game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50)))
    screen.blit(home_icon, (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 + 50))
    screen.blit(replay_icon, (SCREEN_WIDTH // 2 + 150, SCREEN_HEIGHT // 2 + 50))


def roulette():
    global balance, in_hand

    SCREEN_WIDTH, SCREEN_HEIGHT = 1366, 768
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Roulette")
    pygame.display.set_icon(pygame.image.load("roulette-assets/Roulette Wheel.png"))

    running = True
    while running:
        timer.tick(FPS)

        game_over = balance == 0 and not bets and not moving_chips and in_hand.get_width() == 0 and rake_pos == SCREEN_HEIGHT

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0] and incr == 0 and not clear_chips and not moving_chips:
                    if game_over:
                        if pygame.Rect(SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 + 50, 100, 100).collidepoint(pygame.mouse.get_pos()):
                            running = False  # Clicked the Home button
                        elif pygame.Rect(SCREEN_WIDTH // 2 + 150, SCREEN_HEIGHT // 2 + 50, 100, 100).collidepoint(pygame.mouse.get_pos()):
                            balance = 25  # Clicked the Replay button
                    else:
                        if pygame.Rect(73, 80, 610, 610).collidepoint(pygame.mouse.get_pos()) and bets:
                            spin()
                        else:
                            pick_up_chip()
            elif event.type == pygame.MOUSEBUTTONUP:
                if highlighted_numbers:
                    place_bet()
                elif in_hand.get_width() != 0:
                    balance += get_chip_value(chips.index(in_hand))
                in_hand = pygame.Surface((0, 0))

        screen.fill((0, 118, 58))
        draw_wheel()
        draw_highlighted_numbers()
        screen.blit(background, (0, 0))
        draw_chips()
        draw_hud()
        if clear_chips:
            rake_chips()
        if game_over:
            draw_game_over_screen()

        pygame.display.update()

    balance = 25


if __name__ == "__main__":
    roulette()
    pygame.quit()
