import pygame
import random
import math
from pygame import gfxdraw
pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1366, 768
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Blackjack")
pygame.display.set_icon(pygame.image.load("card-game-assets/cards/card_spades_A.png"))
timer = pygame.time.Clock()
FPS = 60
font = pygame.font.Font("fonts/Kenney Pixel.ttf", 50)
font_2 = pygame.font.Font("fonts/Kenney Mini Square.ttf", 50)

# Taken from Blackjack v1
deck = ["A♥", "2♥", "3♥", "4♥", "5♥", "6♥", "7♥", "8♥", "9♥", "10♥", "J♥", "Q♥", "K♥",
        "A♠", "2♠", "3♠", "4♠", "5♠", "6♠", "7♠", "8♠", "9♠", "10♠", "J♠", "Q♠", "K♠",
        "A♦", "2♦", "3♦", "4♦", "5♦", "6♦", "7♦", "8♦", "9♦", "10♦", "J♦", "Q♦", "K♦",
        "A♣", "2♣", "3♣", "4♣", "5♣", "6♣", "7♣", "8♣", "9♣", "10♣", "J♣", "Q♣", "K♣"]

# Import the images
card_back = pygame.image.load("card-game-assets/cards/card_back.png").convert_alpha()
file_endings = ['A', '02', '03', '04', '05', '06', '07', '08', '09', '10', 'J', 'Q', 'K']

hearts = [pygame.image.load(f"card-game-assets/cards/card_hearts_{ending}.png").convert_alpha() for ending in file_endings]
diamonds = [pygame.image.load(f"card-game-assets/cards/card_diamonds_{ending}.png").convert_alpha() for ending in file_endings]
clubs = [pygame.image.load(f"card-game-assets/cards/card_clubs_{ending}.png").convert_alpha() for ending in file_endings]
spades = [pygame.image.load(f"card-game-assets/cards/card_spades_{ending}.png").convert_alpha() for ending in file_endings]

play_button = pygame.image.load("card-game-assets/blackjack-assets/Play Button.png").convert_alpha()
clear_button = pygame.image.load("card-game-assets/blackjack-assets/Clear Button.png").convert_alpha()
hit_button = pygame.image.load("card-game-assets/blackjack-assets/Hit Button.png").convert_alpha()
stand_button = pygame.image.load("card-game-assets/blackjack-assets/Stand Button.png").convert_alpha()
undo_button = pygame.image.load("card-game-assets/blackjack-assets/Undo Button.png").convert_alpha()
bet_all_button = pygame.image.load("card-game-assets/blackjack-assets/Bet All Button.png").convert_alpha()


# ...and scale them up
def convert_cards(suit):
    for i, card in enumerate(suit):
        card_surface = pygame.Surface((42, 60))
        card_surface.blit(card, (-11, -2))
        card_surface = pygame.transform.scale_by(card_surface, 3)
        card_surface.set_colorkey((0, 0, 0))
        suit[i] = card_surface.convert_alpha()
    return suit


card_back = convert_cards([card_back])[0]
hearts = convert_cards(hearts)
diamonds = convert_cards(diamonds)
clubs = convert_cards(clubs)
spades = convert_cards(spades)

background = pygame.image.load("card-game-assets/blackjack-assets/Blackjack Board.png").convert_alpha()
chip_file_endings = ['5', '10', '25', '50', '100', '1k', '10k', '100k', '1m']
chips = [pygame.image.load(f"card-game-assets/chips/Betting Chip {ending}.png").convert_alpha() for ending in chip_file_endings]
home_icon = pygame.image.load("misc/Home Icon.png").convert_alpha()
replay_icon = pygame.image.load("misc/Replay Icon.png").convert_alpha()

# Game variables
players_hand = []
dealers_hand = []
hide_dealers_card = True
moving_cards = []
MAX_SPEED = 50
card_to_draw = ''
card_animation_in_progress = False
card_animation = True
hands_shift = [0, 0]
balance = 100
stake = []
potential_stake = []
selected_chip = 0
moving_chips = []
chip_to_add = 0
chips_shift = 0
chip_animation_in_progress = False
selected_button = "none"
hide_chip_bar = False
chip_bar_offset = 0
won_round = False
lost_round = False
drew_round = False
round_over = False
stand_animation_in_progress = False
dealers_hidden_card = ''
new_round = False
stake_chips_offset = 0
draw_double_chips = False
reset_pause = 0
round_over_pause = 0
continue_round = False
game_over = False
with open("card-game-assets/blackjack-assets/highscore.txt") as file:
    highscore = int(file.readline())


class MovingObject:
    def __init__(self, origin, target, sprite):
        self.origin = origin
        self.current_pos = origin
        self.target = target
        self.sprite = sprite
        self.arrived = False
        self.flip_counter = 0
        self.flip_card = card_back
        self.do_flip = False
        if self.sprite in chips:
            self.centre = (self.current_pos[0] + 45, self.current_pos[1] + 45)
        else:
            self.centre = (self.current_pos[0] + 63, self.current_pos[1] + 90)

    def move(self):  # Fancy af because it moves quadratically, not linearly
        if self.target != (0, 0):
            dx = self.target[0] - self.origin[0]
            dy = self.target[1] - self.origin[1]
            distance_vector = (dx, dy)
            distance = math.sqrt(dx**2 + dy**2)  # Pythagoras
            normalised_distance_vector = (distance_vector[0] / distance, distance_vector[1] / distance)  # Normalise; make magnitude equal to 1; d̂ = d / ║d║

            dx = self.current_pos[0] - self.origin[0]
            dy = self.current_pos[1] - self.origin[1]
            progress = math.sqrt(dx**2 + dy**2) / distance
            if progress == 0:
                progress = 0.01
            # speed = -4 * MAX_SPEED * progress ** 2 + 4 * MAX_SPEED * progress  # Quadratic between 0 and 1 with T.P. of MAX_SPEED; y=-4mx²+4mx
            speed = (-4*MAX_SPEED + 10) * progress ** 2 + (4*MAX_SPEED - 15) * progress + 5  # Fancy ah quadratic speed curve
            movement_vector = (normalised_distance_vector[0] * speed, normalised_distance_vector[1] * speed)
            self.current_pos = (self.current_pos[0] + movement_vector[0], self.current_pos[1] + movement_vector[1])

            if round(progress, 2) == 1:
                self.arrived = True
                self.current_pos = self.target
                self.target = (0, 0)

            if self.sprite in chips:
                self.centre = (self.current_pos[0] + 45, self.current_pos[1] + 45)
            else:
                self.centre = (self.current_pos[0] + 63, self.current_pos[1] + 90)

    def flip(self):
        if self.do_flip and self.flip_counter < 20:
            self.flip_counter += 1
            if self.flip_counter > 10:
                self.sprite = self.flip_card

            # Inspired by Wordle
            self.sprite = pygame.transform.scale(self.sprite, (126 * abs(self.flip_counter / 10 - 1), 180))

    def draw(self):
        screen.blit(self.sprite, self.sprite.get_rect(center=self.centre))


def calculate_total(hand, dealer=False):
    ace = 0
    total = 0
    for i in range(len(hand)):
        if hand[i][0] == 'A':
            total += 1
            ace += 1
        elif hand[i][0] in ['J', 'Q', 'K', '1']:
            total += 10
        elif hand[i] == 'none':
            total += 0
        else:
            total += int(hand[i][0])

    # Don't give the aces option if it makes you go bust (and not having it doesn't)
    while total + ace * 10 > 21 and total <= 21:
        if ace != 0:
            ace -= 1

    # Don't give aces option if you're already bust
    if total > 21 and ace > 0:
        ace = 0

    # If the dealer has an ace that puts them above the player, always use it
    if dealer and total >= 16:
        if total < calculate_total(players_hand)[1] < total + ace * 10:
            total += 10
            ace -= 1

    # If you have a blackjack (or otherwise 21), don't add aces option
    if total != 21 and total + ace * 10 == 21:
        total += ace * 10
        ace = 0

    return total, total + ace * 10


def hand_is_blackjack(hand):
    if len(hand) != 2:
        return False
    if hand[0][0] in ['1', 'J', 'Q', 'K'] and hand[1][0] == 'A':
        return True
    if hand[1][0] in ['1', 'J', 'Q', 'K'] and hand[0][0] == 'A':
        return True


def get_card_image(card: str):
    if card == "back":
        return card_back
    elif card == "none":
        return pygame.Surface((0, 0))

    if card[0] == 'A':
        ind = 0
    elif card[0] == '1':
        ind = 9
    elif card[0] == 'J':
        ind = 10
    elif card[0] == 'Q':
        ind = 11
    elif card[0] == 'K':
        ind = 12
    else:
        ind = int(card[0]) - 1

    if card[-1] == '♥':
        return hearts[ind]
    elif card[-1] == '♠':
        return spades[ind]
    elif card[-1] == '♦':
        return diamonds[ind]
    elif card[-1] == '♣':
        return clubs[ind]
    else:
        return pygame.Surface((0, 0))


def get_chip_image(chip):
    if chip == 5:
        return chips[0]
    elif chip == 10:
        return chips[1]
    elif chip == 25:
        return chips[2]
    elif chip == 50:
        return chips[3]
    elif chip == 100:
        return chips[4]
    elif chip == 1_000:
        return chips[5]
    elif chip == 10_000:
        return chips[6]
    elif chip == 100_000:
        return chips[7]
    elif chip == 1_000_000:
        return chips[8]
    else:
        return pygame.Surface((0, 0))


def get_chip_value_from_index(index):
    return [5, 10, 25, 50, 100, 1_000, 10_000, 100_000, 1_000_000][index]


def get_chip_index_from_value(value):
    if value == 5:
        return 0
    elif value == 10:
        return 1
    elif value == 25:
        return 2
    elif value == 50:
        return 3
    elif value == 100:
        return 4
    elif value == 1_000:
        return 5
    elif value == 10_000:
        return 6
    elif value == 100_000:
        return 7
    elif value == 1_000_000:
        return 8
    else:
        raise ValueError


def get_value_in_chips(value):
    pile = []  # Pile... of chips ("chips" was taken)
    while value > 0:
        for chip_value in [1_000_000, 100_000, 10_000, 1_000, 100, 50, 25, 10, 5]:
            if value >= chip_value:
                pile.append(chip_value)
                value -= chip_value
                break
    return pile


def draw_decorations():
    for x in range(5):  # Draw card stack in top right
        screen.blit(card_back, (1100 + x * 5, 50))

    balance_text = font.render(f"Balance: {balance:,}", True, (255, 255, 255))
    screen.blit(balance_text, (8, 0))

    highscore_text = font.render(f"Highscore: {highscore:,}", True, (255, 255, 255))
    screen.blit(highscore_text, highscore_text.get_rect(topright=(SCREEN_WIDTH - 8, 0)))


def draw_hands():
    # Draw player's hand
    for i, card in enumerate(players_hand):
        dest = SCREEN_WIDTH/2 - (126 + 45 * (len(players_hand) - 1))/2  # Origin of deck
        dest += i * 45 - hands_shift[0]
        screen.blit(get_card_image(card), (dest, 500))

    # Draw dealer's hand
    for i, card in enumerate(dealers_hand):
        dest = SCREEN_WIDTH / 2 - (126 + 45 * (len(dealers_hand) - 1)) / 2
        dest += i * 45 - hands_shift[1]
        if hide_dealers_card and i == 1:
            card = "back"
        screen.blit(pygame.transform.rotate(get_card_image(card), 180), (dest, 50))


def draw_chips():  # And buttons
    global selected_chip, selected_button, hide_chip_bar, chip_bar_offset

    if hide_chip_bar:
        chip_bar_offset += 10
    if chip_bar_offset >= 120:
        hide_chip_bar = False

    selected_chip = 0
    selected_button = "none"

    # Draw the chips at the bottom
    for x, chip in enumerate(chips):
        dest = (SCREEN_WIDTH // 2) - 480 + x * 110
        if chip_bar_offset == 0 and pygame.Rect(dest, 650, 90, 90).collidepoint(pygame.mouse.get_pos()):
            img = pygame.transform.scale(chip, (100, 100))
            screen.blit(img, (dest - 5, 645))
            selected_chip = get_chip_value_from_index(x)
        else:
            screen.blit(chip, (dest, 650 + chip_bar_offset))

    # Draw the stake chips in the middle of the table
    for i, chip in enumerate(potential_stake):
        dest = SCREEN_WIDTH / 2 - (90 + 45 * (len(potential_stake) - 1)) / 2
        dest += i * 45 - chips_shift
        screen.blit(get_chip_image(chip), (dest, 340))

    for i, chip in enumerate(stake):
        dest = SCREEN_WIDTH / 2 - (90 + 45 * (len(stake) - 1)) / 2
        dest += i * 45
        screen.blit(get_chip_image(chip), (dest, 340 - stake_chips_offset))

    if draw_double_chips:  # Doubled chips from winning
        for i, chip in enumerate(stake):
            dest = SCREEN_WIDTH / 2 - (90 + 45 * (len(stake) - 1)) / 2
            dest += i * 45
            screen.blit(get_chip_image(chip), (dest, 340 + stake_chips_offset))

    if not stake and potential_stake:  # Draw text & buttons
        # Draw the sum of the potential stake
        if sum(potential_stake) <= balance:
            stake_text = font.render(f"{sum(potential_stake):,}", False, (255, 255, 255))
        else:  # Draw red if over balance
            stake_text = font.render(f"{sum(potential_stake):,}", False, (191, 34, 34))

        stake_rect = stake_text.get_rect(center=(SCREEN_WIDTH/2, 500))
        pygame.draw.rect(screen, (0, 50, 20), (stake_rect.x - 10, stake_rect.y - 5, stake_rect.w + 20, stake_rect.h + 10), 0, 10)
        screen.blit(stake_text, stake_rect)

        # Draw clear, play and undo buttons
        if pygame.Rect(416, 500, 150, 90).collidepoint(pygame.mouse.get_pos()):
            screen.blit(clear_button, (416, 505))
            selected_button = "clear"
        else:
            screen.blit(clear_button, (416, 500))
        if pygame.Rect(800, 500, 150, 90).collidepoint(pygame.mouse.get_pos()):
            screen.blit(play_button, (800, 505))
            selected_button = "play"
        else:
            screen.blit(play_button, (800, 500))
        if pygame.Rect(SCREEN_WIDTH - 120, 645, 100, 100).collidepoint(pygame.mouse.get_pos()):
            screen.blit(undo_button, (SCREEN_WIDTH - 120, 650))
            selected_button = "undo"
        else:
            screen.blit(undo_button, (SCREEN_WIDTH - 120, 645))
    elif not (stake or potential_stake or moving_chips):
        # Draw bet all button
        if bet_all_button.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)).collidepoint(pygame.mouse.get_pos()):
            screen.blit(bet_all_button, bet_all_button.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 5)))
            selected_button = "bet all"
        else:
            screen.blit(bet_all_button, bet_all_button.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)))

        bet_all_text = font.render("or place a bet using the chips below", False, (255, 255, 255))
        bet_all_text = pygame.transform.scale_by(bet_all_text, 1.4)
        screen.blit(bet_all_text, bet_all_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100)))


def draw_moving_objects():
    for moving_card in moving_cards:
        moving_card.move()
        moving_card.flip()
        moving_card.draw()

    for moving_chip in moving_chips:
        moving_chip.move()
        moving_chip.draw()


def draw_round_over_text():
    global round_over_pause

    if round_over_pause < FPS * 0.8:
        round_over_pause += 1
        return

    if won_round:
        text = "You win!"
    elif drew_round:
        text = "Push!"
    elif lost_round:
        text = "You lose!"
    else:
        text = "Error"

    round_over_text = font_2.render(text, False, (255, 255, 255))
    round_over_text = pygame.transform.scale_by(round_over_text, 3)
    box = round_over_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 10))
    gfxdraw.filled_polygon(screen, ((0, 0), (0, SCREEN_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT), (SCREEN_WIDTH, 0)), (0, 0, 0, 100))
    screen.blit(round_over_text, box)

    continue_text = font_2.render("Click to Continue", False, (255, 255, 255))
    continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 90))
    screen.blit(continue_text, continue_rect)


def draw_game_over_screen():
    gfxdraw.filled_polygon(screen, ((0, 0), (0, SCREEN_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT), (SCREEN_WIDTH, 0)), (0, 0, 0, 100))
    game_over_text = font_2.render("You've gone", False, (255, 255, 255))
    game_over_text = pygame.transform.scale_by(game_over_text, 3)
    game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 60))
    screen.blit(game_over_text, game_over_rect)

    game_over_text = font_2.render("bankrupt!", False, (255, 255, 255))
    game_over_text = pygame.transform.scale_by(game_over_text, 3)
    game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 60))
    screen.blit(game_over_text, game_over_rect)

    screen.blit(home_icon, (SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//2 + 150))
    screen.blit(replay_icon, (SCREEN_WIDTH//2 + 150, SCREEN_HEIGHT//2 + 150))


def add_card_to_deck(player, card, flip=True):
    global moving_cards, hands_shift, lost_round, won_round, players_hand, dealers_hand
    if moving_cards:  # There is a MovingObject in the moving_cards list
        if moving_cards[0].arrived:
            # Start flipping animation (unless told not to because dealer's second card doesn't get flipped)
            if flip:
                moving_cards[0].flip_card = get_card_image(card)
                if not player:  # Dealer's cards face the other way
                    moving_cards[0].flip_card = pygame.transform.rotate(moving_cards[0].flip_card, 180)
                moving_cards[0].do_flip = True

            # When finished flipping animation
            if moving_cards[0].flip_counter >= 20 or not flip:
                # Gently slide the cards to the left, rather than jumping to centred state
                if player and players_hand:
                    hands_shift[0] += 5
                elif dealers_hand:
                    hands_shift[1] += 5
                # Only move over to the left if it isn't the first card (which is already in the centre)
                if players_hand or dealers_hand:
                    moving_cards[0].centre = (moving_cards[0].centre[0] - 5, moving_cards[0].centre[1])

                # When finished shifting animation
                if hands_shift[0] > 20 or hands_shift[1] > 20 or not (players_hand and dealers_hand):
                    moving_cards = []
                    hands_shift = [0, 0]

                    # Add the card to the deck and set card_animation_in_progress to False, ending the animation sequence
                    if player:
                        players_hand.append(card)
                        if calculate_total(players_hand)[0] > 21:
                            lost_round = True
                        elif len(players_hand) == 5:
                            won_round = True
                    else:
                        dealers_hand.append(card)
                        won_round = True if calculate_total(dealers_hand)[0] > 21 else won_round

                    return False
    else:  # Need to add a MovingObject to the moving_cards list
        if player:
            if players_hand:  # Target the centre if first card, else go to the next space over
                target = (SCREEN_WIDTH/2 - (126 + 45 * (len(players_hand) - 1))/2 + 45 * len(players_hand), 500)
            else:
                target = (SCREEN_WIDTH/2 - 126/2, 500)
        else:  # Dealer
            if dealers_hand:  # Target the centre if first card, else go to the next space over
                target = (SCREEN_WIDTH/2 - (126 + 45 * (len(dealers_hand) - 1))/2 + 45 * len(dealers_hand), 50)
            else:
                target = (SCREEN_WIDTH/2 - 126/2, 50)
        moving_cards.append(MovingObject((1125, 50), target, card_back))
    return True


def get_card_from_deck(player):
    global card_to_draw, card_animation_in_progress, card_animation, deck
    if card_animation_in_progress:
        return
    card_to_draw = deck.pop(random.randint(0, len(deck) - 1))
    card_animation_in_progress = True
    card_animation = player


def move_chip_to_board(chip):
    global moving_chips, chips_shift

    # This is all basically coppied from add_card_to_deck(), only simplified because there's only one "deck" in this instance
    if moving_chips:
        if moving_chips[0].arrived:
            if potential_stake:
                chips_shift += 2
                moving_chips[0].centre = (moving_chips[0].centre[0] - 2, moving_chips[0].centre[1])
            if chips_shift > 20 or not potential_stake:
                moving_chips = []
                chips_shift = 0
                potential_stake.append(chip)
                return False
    else:
        target = (SCREEN_WIDTH / 2 - (90 + 45 * (len(potential_stake) - 1)) / 2 + 45 * len(potential_stake), SCREEN_HEIGHT/2 - 45 + 1)  # The +1 is some error margin thing idrk
        if not potential_stake:
            target = (SCREEN_WIDTH / 2 - 45, SCREEN_HEIGHT/2 - 45 + 1)
        origin = (SCREEN_WIDTH // 2) - 480 + get_chip_index_from_value(chip) * 110
        moving_chips.append(MovingObject((origin, 650), target, get_chip_image(chip)))
    return True


def add_chip_to_stake(chip):
    global chip_to_add, chip_animation_in_progress
    if chip_animation_in_progress:
        return
    chip_to_add = chip
    chip_animation_in_progress = True


def stand():
    global hide_dealers_card, dealers_hidden_card, dealers_hand, moving_cards
    global won_round, drew_round, lost_round

    if not card_animation_in_progress:
        # Reveal the dealers card (by making a MovingObject and using its flip method)
        if hide_dealers_card:
            hide_dealers_card = False
            dealers_hidden_card = dealers_hand[1]
            dealers_hand[1] = "none"
            moving_cards.append(MovingObject((640, 50), (0, 0), card_back))
            moving_cards[0].flip_card = get_card_image(dealers_hidden_card)
            moving_cards[0].do_flip = True

        # When finished flipping (once)
        if moving_cards and moving_cards[0].flip_counter >= 20:
            moving_cards = []
            dealers_hand[1] = dealers_hidden_card

        # When finished flipping (recurring)
        if not moving_cards:
            dealers_total = calculate_total(dealers_hand)
            players_total = calculate_total(players_hand)
            if dealers_total[0] > 21:  # Dealer bust
                won_round = True
            elif dealers_total[1] >= 17:
                if players_total[1] > dealers_total[1]:
                    won_round = True
                elif players_total[1] == dealers_total[1]:
                    drew_round = True
                else:
                    lost_round = True
            else:  # Dealer must hit on soft 16
                get_card_from_deck(False)
                return True  # Keep going
            return False
    return True


def draw_totals():
    # Draw player's total
    players_total = calculate_total(players_hand)
    if players_total[0] == players_total[1]:
        players_total = str(players_total[0]) if players_total[0] != 0 else ''
    else:
        players_total = f"{players_total[0]}/{players_total[1]}"
    players_total_text = font.render(players_total, False, (255, 255, 255))
    players_total_rect = players_total_text.get_rect(center=(SCREEN_WIDTH/2, 710))
    screen.blit(players_total_text, players_total_rect)

    # Draw dealer's total
    if hide_dealers_card and dealers_hand:
        dealers_total = calculate_total([dealers_hand[0]], True)
    else:
        dealers_total = calculate_total(dealers_hand, True)
    if dealers_total[0] == dealers_total[1]:
        dealers_total = str(dealers_total[0]) if dealers_total[0] != 0 else ''
    else:
        dealers_total = f"{dealers_total[0]}/{dealers_total[1]}"
    dealers_total_text = font.render(dealers_total, False, (255, 255, 255))
    dealers_total_rect = dealers_total_text.get_rect(center=(SCREEN_WIDTH/2, 250))
    screen.blit(dealers_total_text, dealers_total_rect)


def reset():
    global deck, players_hand, dealers_hand, hide_dealers_card, stake, draw_double_chips, stake_chips_offset, chip_bar_offset
    global won_round, drew_round, lost_round, new_round, reset_pause, moving_cards, moving_chips, dealers_hidden_card, balance, continue_round

    deck = ["A♥", "2♥", "3♥", "4♥", "5♥", "6♥", "7♥", "8♥", "9♥", "10♥", "J♥", "Q♥", "K♥",
            "A♠", "2♠", "3♠", "4♠", "5♠", "6♠", "7♠", "8♠", "9♠", "10♠", "J♠", "Q♠", "K♠",
            "A♦", "2♦", "3♦", "4♦", "5♦", "6♦", "7♦", "8♦", "9♦", "10♦", "J♦", "Q♦", "K♦",
            "A♣", "2♣", "3♣", "4♣", "5♣", "6♣", "7♣", "8♣", "9♣", "10♣", "J♣", "Q♣", "K♣"]

    if won_round and stake_chips_offset < 50:
        draw_double_chips = True
        stake_chips_offset += 5
    elif hide_dealers_card:  # Code for reavealing dealer's card, coppied from stand()
        hide_dealers_card = False
        dealers_hidden_card = dealers_hand[1]
        dealers_hand[1] = "none"
        moving_cards.append(MovingObject((640, 50), (0, 0), card_back))
        moving_cards[0].flip_card = get_card_image(dealers_hidden_card)
        moving_cards[0].do_flip = True
    elif moving_cards and moving_cards[0].flip_counter >= 20:
        moving_cards = []
        dealers_hand[1] = dealers_hidden_card
    else:
        reset_pause += 1 if reset_pause < 30 else 0

    # When finished doubling chips (if applicable)
    if reset_pause >= 30 and (stake_chips_offset >= 50 or not won_round):
        # Move all the cards off-screen
        if dealers_hand:
            for i, card in enumerate(dealers_hand):
                origin = SCREEN_WIDTH / 2 - (126 + 45 * (len(dealers_hand) - 1)) / 2 + i * 45
                moving_cards.append(MovingObject((origin, 50), (0, -200), get_card_image(card)))
            dealers_hand = []
        if players_hand:
            for i, card in enumerate(players_hand):
                origin = SCREEN_WIDTH / 2 - (126 + 45 * (len(players_hand) - 1)) / 2 + i * 45
                moving_cards.append(MovingObject((origin, 500), (0, -200), get_card_image(card)))
            players_hand = []

        continue_round = True  # Prevents round (and thus reset) from stopping once stake is set to []
        # Move all the chips off-screen
        if won_round:
            for i, chip in enumerate(stake):
                origin = (SCREEN_WIDTH / 2 - (90 + 45 * (len(stake) - 1)) / 2) + i * 45
                moving_chips.append(MovingObject((origin, 390), (SCREEN_WIDTH/2 - 45, SCREEN_HEIGHT + 10), get_chip_image(chip)))
                moving_chips.append(MovingObject((origin, 290), (SCREEN_WIDTH/2 - 45, SCREEN_HEIGHT + 10), get_chip_image(chip)))
            balance += sum(stake) * 2
            stake = []
        elif drew_round:
            for i, chip in enumerate(stake):
                origin = (SCREEN_WIDTH / 2 - (90 + 45 * (len(stake) - 1)) / 2) + i * 45
                moving_chips.append(MovingObject((origin, SCREEN_HEIGHT/2 - 45 + 1), (SCREEN_WIDTH/2 - 45, SCREEN_HEIGHT + 10), get_chip_image(chip)))
            balance += sum(stake)
            stake = []
        else:  # Lost round
            for i, chip in enumerate(stake):
                origin = (SCREEN_WIDTH / 2 - (90 + 45 * (len(stake) - 1)) / 2) + i * 45
                moving_chips.append(MovingObject((origin, SCREEN_HEIGHT/2 - 45 + 1), (SCREEN_WIDTH/2 - 45, -200), get_chip_image(chip)))
            stake = []

        # Only continue when all moving objects have arrived
        cont = True
        for moving_card in moving_cards:
            if not moving_card.arrived:
                cont = False
        for moving_chip in moving_chips:
            if not moving_chip.arrived:
                cont = False

        if cont:
            moving_cards = []
            moving_chips = []
            if chip_bar_offset > 0:
                chip_bar_offset -= 10
            else:
                won_round = drew_round = lost_round = new_round = continue_round = False
                hide_dealers_card = True
                stake_chips_offset = reset_pause = 0


def game_round():
    global selected_button, round_over, highscore

    # Deal first two cards for each person, alternatingly
    if not (card_animation_in_progress or round_over):
        if len(dealers_hand) == 0:
            get_card_from_deck(False)
        elif len(players_hand) == 0:
            get_card_from_deck(True)
        elif len(dealers_hand) == 1:
            get_card_from_deck(False)
        elif len(players_hand) == 1:
            get_card_from_deck(True)

    # Update high score
    if balance > highscore:
        highscore = balance
        with open("card-game-assets/blackjack-assets/highscore.txt", 'w') as file:
            file.write(str(balance))

    # Handle starting the next round etc.
    round_over = won_round or drew_round or lost_round
    if round_over:
        if new_round:  # Clicked to continue
            reset()
        else:
            draw_round_over_text()

    # Draw hit and stand buttons
    if not (card_animation_in_progress or round_over or stand_animation_in_progress) and len(players_hand) >= 2:
        if pygame.Rect(875, 550, 150, 90).collidepoint(pygame.mouse.get_pos()):
            selected_button = "hit"
            screen.blit(hit_button, (875, 555))
        else:
            screen.blit(hit_button, (875, 550))

        if pygame.Rect(341, 550, 150, 90).collidepoint(pygame.mouse.get_pos()):
            selected_button = "stand"
            screen.blit(stand_button, (341, 555))
        else:
            screen.blit(stand_button, (341, 550))


def blackjack():
    global balance, stake, potential_stake, game_over, card_animation_in_progress, chip_animation_in_progress, stand_animation_in_progress, new_round, hide_chip_bar

    SCREEN_WIDTH, SCREEN_HEIGHT = 1366, 768
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Blackjack")
    pygame.display.set_icon(pygame.image.load("card-game-assets/cards/card_spades_A.png"))

    running = True
    while running:
        timer.tick(FPS)

        if balance <= 0 and not stake:
            game_over = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
                new_round = True if round_over else False

                if game_over:
                    if pygame.Rect(SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//2 + 150, 100, 100).collidepoint(pygame.mouse.get_pos()):
                        running = False  # Clicked the Home button
                    elif pygame.Rect(SCREEN_WIDTH//2 + 150, SCREEN_HEIGHT//2 + 150, 100, 100).collidepoint(pygame.mouse.get_pos()):
                        game_over = False  # Clicked the replay button
                        balance = 100

                if selected_chip != 0:
                    add_chip_to_stake(selected_chip)

                if selected_button == "clear":
                    potential_stake = []
                elif selected_button == "play" and not moving_chips:
                    if sum(potential_stake) <= balance:
                        balance -= sum(potential_stake)
                        stake = potential_stake.copy()
                        potential_stake = []
                        hide_chip_bar = True
                    else:
                        potential_stake = []

                elif selected_button == "undo" and not moving_chips:
                    potential_stake = potential_stake[:-1]
                elif selected_button == "bet all":
                    potential_stake = get_value_in_chips(balance)

                elif selected_button == "hit":
                    get_card_from_deck(True)
                elif selected_button == "stand":
                    stand_animation_in_progress = True

        screen.fill((0, 118, 58))
        screen.blit(background, (0, 0))
        draw_hands()
        draw_decorations()
        if not game_over:
            draw_chips()
        draw_moving_objects()
        draw_totals()
        if stake or continue_round:
            game_round()
        if game_over:
            draw_game_over_screen()

        # Animation system
        if card_animation_in_progress:
            if not card_animation and len(dealers_hand) == 1:  # Dealer's second card
                card_animation_in_progress = add_card_to_deck(card_animation, card_to_draw, False)
            else:
                card_animation_in_progress = add_card_to_deck(card_animation, card_to_draw)
        if chip_animation_in_progress:
            chip_animation_in_progress = move_chip_to_board(chip_to_add)
        if stand_animation_in_progress:
            stand_animation_in_progress = stand()

        pygame.display.update()

    game_over = False
    balance = 100 if not stake else balance


if __name__ == "__main__":
    blackjack()
    pygame.quit()
