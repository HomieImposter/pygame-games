import pygame
import random
import math
pygame.init()

WIDTH, HEIGHT = 1366, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT), vsync=True)
pygame.display.set_caption("Poker")
timer = pygame.time.Clock()
FPS = 60

# Taken from Blackjack
deck = ["A♥", "2♥", "3♥", "4♥", "5♥", "6♥", "7♥", "8♥", "9♥", "10♥", "J♥", "Q♥", "K♥",
        "A♠", "2♠", "3♠", "4♠", "5♠", "6♠", "7♠", "8♠", "9♠", "10♠", "J♠", "Q♠", "K♠",
        "A♦", "2♦", "3♦", "4♦", "5♦", "6♦", "7♦", "8♦", "9♦", "10♦", "J♦", "Q♦", "K♦",
        "A♣", "2♣", "3♣", "4♣", "5♣", "6♣", "7♣", "8♣", "9♣", "10♣", "J♣", "Q♣", "K♣"]
random.shuffle(deck)

# Import the images
card_back = pygame.image.load("card-game-assets/cards/card_back.png").convert_alpha()
file_endings = ['A', '02', '03', '04', '05', '06', '07', '08', '09', '10', 'J', 'Q', 'K']

hearts = [pygame.image.load(f"card-game-assets/cards/card_hearts_{ending}.png").convert_alpha() for ending in file_endings]
diamonds = [pygame.image.load(f"card-game-assets/cards/card_diamonds_{ending}.png").convert_alpha() for ending in file_endings]
clubs = [pygame.image.load(f"card-game-assets/cards/card_clubs_{ending}.png").convert_alpha() for ending in file_endings]
spades = [pygame.image.load(f"card-game-assets/cards/card_spades_{ending}.png").convert_alpha() for ending in file_endings]


# ...and scale them up
def convert_cards(suit):
    for i, card in enumerate(suit):
        card_surface = pygame.Surface((42, 60))
        card_surface.blit(card, (-11, -2))
        card_surface = pygame.transform.scale_by(card_surface, 4)  # 168x240
        card_surface.set_colorkey((0, 0, 0))
        suit[i] = card_surface.convert_alpha()
    return suit


card_back = convert_cards([card_back])[0]
hearts = convert_cards(hearts)
diamonds = convert_cards(diamonds)
clubs = convert_cards(clubs)
spades = convert_cards(spades)

held = pygame.image.load("poker-assets/Held.png").convert_alpha()
draw = pygame.image.load("poker-assets/Draw.png").convert_alpha()

paused = False
hand = ['' for _ in range(5)]
held_cards = [False for _ in range(5)]
greyed_cards = [False for _ in range(5)]
animation_in_progress = False
accept_input = False
starting_round = True
drawing_cards = False
drawing_card_ind = 0
drawing_cooldown = 0
drawn = False
evaluation_cooldown = 0
reset_cooldown = 0


class Card:
    instances = []

    def __init__(self, pos: pygame.Vector2, new_pos: pygame.Vector2, card: str, hand_ind: int):
        Card.instances.append(self)
        self.start_pos = pos.copy()
        self.pos = pos.copy()
        self.new_pos = new_pos
        self.ind = hand_ind
        self.card = card
        self.flip_card = get_card_image(card)
        self.progress = 0.0
        self.total_distance = pos.distance_to(new_pos)
        self.direction_vector = (new_pos - pos).normalize()
        self.max_speed = self.total_distance / 20

    def update(self):
        global starting_round

        distance_travelled = self.pos.distance_to(self.start_pos)
        self.progress = distance_travelled / self.total_distance

        # Speed changes quadratically based on progress, makes a smoother animation than linear movement
        speed = (-4 * self.max_speed + 4) * self.progress ** 2 + (4 * self.max_speed - 4) * self.progress + 1
        velocity = self.direction_vector * speed
        self.pos += velocity

        if round(self.progress, 2) == 1:
            if self.ind != -1:
                hand[self.ind] = self.card
            else:
                starting_round = True
            del Card.instances[Card.instances.index(self)]

    def draw(self):
        if self.progress <= 0.5:
            card = card_back
        else:
            card = self.flip_card

        # Rotation (in the z-axis (flipping))
        if self.flip_card != card_back:
            angle = self.progress * math.pi
            width_scale = abs(math.cos(angle))
            draw_card = pygame.transform.scale(card, (card.get_width() * width_scale, card.get_height()))
        else:
            draw_card = card

        if self.ind == -1:
            draw_card = self.flip_card

        screen.blit(draw_card, draw_card.get_rect(center=self.pos))


# From Blackjack
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


def evaluate_cards():
    global evaluation_cooldown, greyed_cards, reset_cooldown

    evaluation_cooldown -= 1 if evaluation_cooldown > 0 else 0

    if evaluation_cooldown == 0:
        for _ in range(1):  # Loop so we can use break
            # Find possible hands and respective payouts
            values = [card[0] for card in hand]
            suits = [card[-1] for card in hand]  # ♥ ♠ ♦ ♣

            card_order = ['2', '3', '4', '5', '6', '7', '8', '9', '1', 'J', 'Q', 'K', 'A']
            flush = (suits[0] == suits[1] == suits[2] == suits[3] == suits[4])

            straight = False
            for i in range(9):
                subset = card_order[i:i+5]
                if sorted(values) == sorted(subset):
                    straight = True

            payout = 0  # to 1

            # Royal flush
            if 'A' in values and straight and flush:
                payout = 250
                print("Royal Flush")
                break

            # Straight flush
            if straight and flush:
                payout = 50
                print("Straight Flush")
                break

            # 4 of a kind
            for i in range(5):
                subset = values.copy()
                del subset[i]
                if subset[0] == subset[1] == subset[2] == subset[3]:
                    greyed_cards[i] = True
                    payout = 25
                    print("4 of a kind")
                    break

            if payout != 0:
                break

            # Full house
            if len(set(values)) == 2:
                payout = 9
                print("Full house")
                break

            # Flush
            if flush:
                payout = 6
                print("Flush")
                break

            # Straight
            if straight:
                payout = 4
                print("Straight")
                break

            # 3 of a kind
            for card in card_order:
                like_cards = []
                for i, value in enumerate(values):
                    if value == card:
                        like_cards.append(i)

                if len(like_cards) == 3:
                    greyed_cards = [True for _ in range(5)]
                    for i in like_cards:
                        greyed_cards[i] = False
                    payout = 3
                    print("3 of a kind")
                    break
            if payout != 0:
                break

            # 2 pairs
            pairs = []
            for card in card_order:
                like_cards = []
                for i, value in enumerate(values):
                    if value == card:
                        like_cards.append(i)

                if len(like_cards) == 2:
                    pairs.append(like_cards)

            if len(pairs) == 2:
                greyed_cards = [True for _ in range(5)]
                for i in pairs[0] + pairs[1]:
                    greyed_cards[i] = False
                payout = 2
                print("2 Pairs")
                break

            # Pair
            if len(pairs) == 1:
                greyed_cards = [True for _ in range(5)]
                for i in pairs[0]:
                    greyed_cards[i] = False
                payout = 1
                print("Pair")

        reset_cooldown = FPS * 3


def reset():
    global hand, deck, reset_cooldown, greyed_cards, drawn

    reset_cooldown -= 1 if reset_cooldown > 0 else 0

    if reset_cooldown == 0:
        if len(deck) < 10:
            deck = ["A♥", "2♥", "3♥", "4♥", "5♥", "6♥", "7♥", "8♥", "9♥", "10♥", "J♥", "Q♥", "K♥",
                    "A♠", "2♠", "3♠", "4♠", "5♠", "6♠", "7♠", "8♠", "9♠", "10♠", "J♠", "Q♠", "K♠",
                    "A♦", "2♦", "3♦", "4♦", "5♦", "6♦", "7♦", "8♦", "9♦", "10♦", "J♦", "Q♦", "K♦",
                    "A♣", "2♣", "3♣", "4♣", "5♣", "6♣", "7♣", "8♣", "9♣", "10♣", "J♣", "Q♣", "K♣"]

        for i, card in enumerate(hand):
            Card(pygame.Vector2(200 * i + 284, 560), pygame.Vector2(-300, 560), card, -1)
        hand = ['' for _ in range(5)]
        greyed_cards = [False for _ in range(5)]
        drawn = False


def start_round():
    global starting_round

    # Keep adding cards to the hand until there are no empty spots left
    if '' in hand:
        if not animation_in_progress:
            empty_ind = hand.index('')
            Card(pygame.Vector2(584, 245), pygame.Vector2(200 * empty_ind + 284, 560), deck.pop(), empty_ind)
    else:
        starting_round = False


def draw_cards():
    global drawing_cards, drawing_card_ind, drawing_cooldown, evaluation_cooldown

    drawing_cooldown -= 1 if drawing_cooldown > 0 else 0

    # Replace cards that aren't held
    if not (animation_in_progress or drawing_cooldown > 0):
        if not held_cards[drawing_card_ind]:
            Card(pygame.Vector2(584, 245), pygame.Vector2(200 * drawing_card_ind + 284, 560), deck.pop(), drawing_card_ind)

        held_cards[drawing_card_ind] = False
        drawing_card_ind += 1

        if drawing_card_ind == 5:
            evaluation_cooldown = FPS * 1
        elif held_cards[drawing_card_ind]:
            drawing_cooldown = FPS * 0.8  # Wait 0.8 seconds

    if drawing_card_ind >= 5:
        drawing_card_ind = 0
        drawing_cards = False


def draw_hand():
    for i, card in enumerate(hand):
        if card:
            if greyed_cards[i]:
                greyed_card = get_card_image(card).copy()
                greyed_card.set_alpha(180)
                screen.blit(greyed_card, (200 * i + 200, 440))
            else:
                screen.blit(get_card_image(card), (200 * i + 200, 440))

    for i, is_held in enumerate(held_cards):
        if is_held:
            screen.blit(held, (200 * i + 224, 700))


def handle_inputs():
    global running, paused, drawing_cards, drawn

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if accept_input:
                    # Find card clicked on (to be held)
                    slots = [pygame.Rect(200 * i + 200, 440, 168, 240) for i in range(5)]
                    for i, slot in enumerate(slots):
                        if slot.collidepoint(event.pos):
                            held_cards[i] = not held_cards[i]

                    # Pressed the Draw button
                    if not drawn and pygame.Rect(734, 195, 100, 100).collidepoint(event.pos):
                        drawing_cards = True
                        drawn = True

                # Pressed the pause/info button
                if pygame.Rect(734, 195, 100, 100).collidepoint(event.pos):
                    ...

        elif event.type == pygame.KEYDOWN:
            if accept_input:
                if event.key == pygame.K_1:
                    held_cards[0] = not held_cards[0]
                elif event.key == pygame.K_2:
                    held_cards[1] = not held_cards[1]
                elif event.key == pygame.K_3:
                    held_cards[2] = not held_cards[2]
                elif event.key == pygame.K_4:
                    held_cards[3] = not held_cards[3]
                elif event.key == pygame.K_5:
                    held_cards[4] = not held_cards[4]
                elif event.key == pygame.K_RETURN:
                    drawing_cards = True
                    drawn = True


def game_update():
    global animation_in_progress, accept_input

    for card in Card.instances:
        card.update()

    # An animation is in progress if there are any instance of the Card class
    animation_in_progress = Card.instances != []
    accept_input = not (animation_in_progress or starting_round or drawing_cards)

    if starting_round:
        start_round()
    if drawing_cards:
        draw_cards()
    if evaluation_cooldown != 0:
        evaluate_cards()
    if reset_cooldown != 0:
        reset()


def draw_update():
    screen.fill((0, 118, 58))

    screen.blit(card_back, (500, 125))
    if accept_input and not drawn and '' not in hand:
        screen.blit(draw, (734, 195))

    draw_hand()

    for card in Card.instances:
        card.draw()


running = True
while running:
    timer.tick(FPS)

    handle_inputs()

    draw_update()

    if paused:
        # Display the list of hands & payouts (to be made)
        ...
    else:
        game_update()

    pygame.display.update()

pygame.quit()
