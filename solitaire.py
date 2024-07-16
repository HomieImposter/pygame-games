import pygame
import random
import math
from pygame import gfxdraw
pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1366 - 146, 768 + 100
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Solitaire")
pygame.display.set_icon(pygame.image.load("card-game-assets/cards/card_diamonds_A.png"))
timer = pygame.time.Clock()
FPS = 60
font = pygame.font.Font("fonts/Kenney Pixel.ttf", 70)
font_2 = pygame.font.Font("fonts/Kenney Mini Square.ttf", 150)

# From Blackjack
deck = ["A♥", "2♥", "3♥", "4♥", "5♥", "6♥", "7♥", "8♥", "9♥", "10♥", "J♥", "Q♥", "K♥",
        "A♠", "2♠", "3♠", "4♠", "5♠", "6♠", "7♠", "8♠", "9♠", "10♠", "J♠", "Q♠", "K♠",
        "A♦", "2♦", "3♦", "4♦", "5♦", "6♦", "7♦", "8♦", "9♦", "10♦", "J♦", "Q♦", "K♦",
        "A♣", "2♣", "3♣", "4♣", "5♣", "6♣", "7♣", "8♣", "9♣", "10♣", "J♣", "Q♣", "K♣"]

card_back = pygame.image.load("card-game-assets/cards/card_back.png").convert_alpha()
file_endings = ['A', '02', '03', '04', '05', '06', '07', '08', '09', '10', 'J', 'Q', 'K']

hearts = [pygame.image.load(f"card-game-assets/cards/card_hearts_{ending}.png").convert_alpha() for ending in file_endings]
diamonds = [pygame.image.load(f"card-game-assets/cards/card_diamonds_{ending}.png").convert_alpha() for ending in file_endings]
clubs = [pygame.image.load(f"card-game-assets/cards/card_clubs_{ending}.png").convert_alpha() for ending in file_endings]
spades = [pygame.image.load(f"card-game-assets/cards/card_spades_{ending}.png").convert_alpha() for ending in file_endings]


def convert_cards(suit):
    # Crops the cards to the relevant part and scales 3x
    for i, card in enumerate(suit):
        card_surface = pygame.Surface((42, 60))
        card_surface.blit(card, (-11, -2))
        card_surface = pygame.transform.scale_by(card_surface, 3)
        card_surface.set_colorkey((0, 0, 0))
        suit[i] = card_surface.convert_alpha()
    return suit


def fill(surface, color):  # From StackOverflow lol
    """Fill all pixels of the surface with color, preserve transparency."""
    w, h = surface.get_size()
    r, g, b = color
    for x in range(w):
        for y in range(h):
            a = surface.get_at((x, y))[3]
            surface.set_at((x, y), pygame.Color(r, g, b, a))


card_back = convert_cards([card_back])[0]
hearts = convert_cards(hearts)
diamonds = convert_cards(diamonds)
clubs = convert_cards(clubs)
spades = convert_cards(spades)
background = pygame.image.load("card-game-assets/solitaire-assets/Solitaire Board.png").convert_alpha()
home_icon = pygame.image.load("misc/Home Icon.png").convert_alpha()
replay_icon = pygame.image.load("misc/Replay Icon.png").convert_alpha()
fill(home_icon, (255, 255, 255))
fill(replay_icon, (255, 255, 255))


class MovingCard:
    # All from blackjack.py
    def __init__(self, pos, sprite, target=(0, 0)):
        self.target = target
        self.origin = pos
        self.current_pos = pos

        self.MAX_SPEED = 100
        self.centre = (self.current_pos[0] + 63, self.current_pos[1] + 90)
        self.sprite = sprite
        self.arrived = False

        self.do_flip = False
        self.flip_counter = 0
        self.flip_card = None

    def move(self):
        if self.target != (0, 0):
            dx = self.target[0] - self.origin[0]
            dy = self.target[1] - self.origin[1]
            distance_vector = (dx, dy)
            distance = math.sqrt(dx**2 + dy**2)
            normalised_distance_vector = (distance_vector[0] / distance, distance_vector[1] / distance)

            dx = self.current_pos[0] - self.origin[0]
            dy = self.current_pos[1] - self.origin[1]
            progress = math.sqrt(dx**2 + dy**2) / distance
            if progress == 0:
                progress = 0.01
            speed = (-4*self.MAX_SPEED + 10) * progress ** 2 + (4*self.MAX_SPEED - 15) * progress + 5
            movement_vector = (normalised_distance_vector[0] * speed, normalised_distance_vector[1] * speed)
            self.current_pos = (self.current_pos[0] + movement_vector[0], self.current_pos[1] + movement_vector[1])

            if round(progress, 2) == 1:
                self.arrived = True
                self.current_pos = self.target
                self.target = (0, 0)

            self.update_centre()

    def flip(self):
        if self.do_flip and self.flip_counter < 20 and self.flip_card is not None:
            self.flip_counter += 1
            if self.flip_counter > 10:
                self.sprite = self.flip_card

            self.sprite = pygame.transform.scale(self.sprite, (126 * abs(self.flip_counter / 10 - 1), 180))

    def update_centre(self):
        self.centre = (self.current_pos[0] + 63, self.current_pos[1] + 90)

    def draw(self):
        screen.blit(self.sprite, self.sprite.get_rect(center=self.centre))


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


def card_is_red(card: str) -> bool:
    return True if card[-1] in ['♥', '♦'] else False


random.shuffle(deck)
foundations = ["none", "none", "none", "none"]  # Cards at the top-left; how far up, starting from Ace=1 to King=13
pile = []  # The cards on the right; technically called the waste
board = [[] for _ in range(7)]  # [card: str, cover_face: bool]; technically called the tableau
for i, column in enumerate(board):
    for card in range(i):
        board[i].append([deck.pop(random.randint(0, len(deck) - 1)), True])  # Random cards with face covered
    board[i].append([deck.pop(random.randint(0, len(deck) - 1)), False])  # Random card with face showing

order = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '1', 'J', 'Q', 'K']
in_hand = []
hide_last_pile_card = False  # If card from pile is in hand, don't draw it at the pile
picked_up_pos = (0, 0)  # Relative positioon of where card was picked up from
cards_came_from = ()  # Where the currently held card(s) came from on the tableau
click_pos = ()
card_came_from_foundation = 0
moving_cards = []
returning_cards = []
flipping_card = MovingCard((-200, -200), card_back)
animation_in_proress = False
flip_animation_in_progress = False
move_animation_in_progress = False
flip_card = (0, "none")  # index (along x), card: str
moving_card_strings = []
deck = deck[:-1]
pile_shift = 0
shift_animation_in_progress = False
game_over = False
clock_counter = FPS
time = 0  # Time in seconds
moves = 0


def convert_time(seconds: int) -> str:  # Turns time in seconds into usable format
    mins, secs = divmod(seconds, 60)
    return f"{mins}:{str(secs).zfill(2)}"


def draw_cards():
    if deck:  # Draws the deck in the top-right
        screen.blit(card_back, (SCREEN_WIDTH - 146, 20))

    for i, card in enumerate(pile[-3:]):  # Shows the next three cards on the right
        if not (hide_last_pile_card and (i == 2 or i == len(pile) - 1)):
            if i == 0:
                screen.blit(get_card_image(card), (SCREEN_WIDTH - 146, i * 42 + 220))
            else:
                screen.blit(get_card_image(card), (SCREEN_WIDTH - 146, i * 42 + 220 - pile_shift))

    for i, column in enumerate(board):  # Draws the cards in the tableau; the main area
        for j, card in enumerate(column):
            draw_card = card_back if card[1] else get_card_image(card[0])
            screen.blit(draw_card, (i * 146 + 20, j * 42 + 220))

    for i, card in enumerate(foundations):  # Draws the cards in the top-left
        screen.blit(get_card_image(card), (i * 146 + 20, 20))


def pick_up_card():
    global hide_last_pile_card, in_hand, picked_up_pos, board, cards_came_from, moves
    global foundations, card_came_from_foundation, deck, pile, moving_card_strings, returning_cards

    cards_came_from = ()
    card_came_from_foundation = 0

    # Clicked on the deck
    if pygame.Rect(1074, 20, 126, 180).collidepoint(pygame.mouse.get_pos()):
        moves += 1
        if deck:
            cards_drawn = 0
            for i in range(3):
                if len(deck) > i:  # Avoid referencing an invalid index
                    cards_drawn += 1
                    if len(deck) > 2:
                        moving_cards.append(MovingCard((1074, 20), get_card_image(deck[-(i+1)]), (1074, 220 + i * 42)))
                    else:
                        moving_cards.append(MovingCard((1074, 20), get_card_image(deck[-(i + 1)]), (1074, 220 + (i + 3 - len(deck)) * 42)))
                    moving_cards[-1].MAX_SPEED = 25
                    moving_card_strings.append(deck[-(i+1)])
            deck = deck[:-cards_drawn]
        else:  # Renew the deck
            for i in range(3):
                if len(pile) > i:
                    returning_cards.append(MovingCard((1074, 304 - i * 42), card_back, (1074, 20)))
            for card in returning_cards:
                card.MAX_SPEED = 50
            deck = [card for card in reversed(pile)]
            pile = []

    # Got card from pile
    if len(pile) > 2 and pygame.Rect(1074, 304, 126, 180).collidepoint(pygame.mouse.get_pos()):
        in_hand = [pile[-1]]
        hide_last_pile_card = True
        picked_up_pos = (pygame.mouse.get_pos()[0] - 1074, pygame.mouse.get_pos()[1] - 304)
        return
    elif pile and pygame.Rect(1074, 178 + len(pile) * 42, 126, 180).collidepoint(pygame.mouse.get_pos()):
        in_hand = [pile[-1]]
        hide_last_pile_card = True
        picked_up_pos = (pygame.mouse.get_pos()[0] - 1074, pygame.mouse.get_pos()[1] - 178 - len(pile) * 42)
        return

    # Bottom (fully exposed) cards on the tableau
    for i, column in enumerate(board):
        if pygame.Rect(i * 146 + 20, (len(column) - 1) * 42 + 220, 126, 180).collidepoint(pygame.mouse.get_pos()):
            in_hand = [column[-1][0]]
            picked_up_pos = (pygame.mouse.get_pos()[0] - i * 146 - 20,
                             pygame.mouse.get_pos()[1] - (len(column) - 1) * 42 - 220)
            del board[i][-1]
            cards_came_from = (i, len(column) - 1)

    # Rest of the cards on the tableau
    board_x = pygame.mouse.get_pos()[0] - 20
    board_y = pygame.mouse.get_pos()[1] - 220
    if board_x % 146 <= 126:  # Clicked on card, not gap
        board_x //= 146
        board_y //= 42
        if board_x < 7 and 0 <= board_y < len(board[board_x]) and not board[board_x][board_y][1]:
            for i, card in enumerate(board[board_x][board_y:]):
                in_hand.append(card[0])  # Removes the True/False show_card_back value
            del board[board_x][board_y:]
            cards_came_from = (board_x, board_y)
            picked_up_pos = (pygame.mouse.get_pos()[0] - board_x * 146 - 20, pygame.mouse.get_pos()[1] - board_y * 42 - 220)
            return

        # Foundations
        if board_x < 4 and 20 <= pygame.mouse.get_pos()[1] <= 200:
            if foundations[board_x] != "none":
                in_hand = [foundations[board_x]]
                if foundations[board_x][0] == 'A':
                    foundations[board_x] = "none"
                else:
                    foundations[board_x] = order[order.index(foundations[board_x][0]) - 1] + foundations[board_x][-1]  # Does the next one down
                picked_up_pos = (pygame.mouse.get_pos()[0] - board_x * 146 - 20, pygame.mouse.get_pos()[1] - 20)
                card_came_from_foundation = board_x + 1


def put_down_card():
    global hide_last_pile_card, in_hand, pile, shift_animation_in_progress, pile_shift, moves

    if click_pos == pygame.mouse.get_pos():
        ...  # special functionality for Clicks

    can_put_down = False

    for i, column in enumerate(board):
        # Check for release on the bottom (fully exposed) cards
        if pygame.Rect(i * 146 + 20, (len(column) - 1) * 42 + 220, 126, 180).collidepoint(pygame.mouse.get_pos()):
            if len(column) == 0 and in_hand[0][0] == 'K':
                can_put_down = True

            elif column and card_is_red(column[-1][0]) ^ card_is_red(in_hand[0]):  # Cards are of alternating colours, using xor (^)
                if order.index(column[-1][0][0]) - 1 == order.index(in_hand[0][0]):  # Cards are ascending
                    can_put_down = True

        # Check for release on the foundations
        elif i < 4 and pygame.Rect(i * 146 + 20, 20, 126, 180).collidepoint(pygame.mouse.get_pos()):
            can_put_down_foundation = False

            if len(in_hand) == 1 and foundations[i] == "none" and in_hand[0][0] == 'A':
                can_put_down_foundation = True
            elif len(in_hand) == 1 and foundations[i] != "none" and order.index(foundations[i][0]) == order.index(in_hand[0][0]) - 1:
                if foundations[i][-1] == in_hand[0][-1]:  # They are of the same suit
                    can_put_down_foundation = True

            if can_put_down_foundation:
                foundations[i] = in_hand[0]
                in_hand = []
                moves += 1
                if hide_last_pile_card:
                    pile = pile[:-1]
                    hide_last_pile_card = False
                    if len(pile) > 3:
                        shift_animation_in_progress = True
                        pile_shift = 42
                return

        if can_put_down:
            for card in in_hand:
                board[i].append([card, False])
            in_hand = []
            if cards_came_from and cards_came_from[0] != i:
                moves += 1
            if hide_last_pile_card:
                pile = pile[:-1]
                hide_last_pile_card = False
                if len(pile) > 3:
                    shift_animation_in_progress = True
                    pile_shift = 42
            return

    if cards_came_from:
        for card in in_hand:
            board[cards_came_from[0]].append([card, False])

    elif card_came_from_foundation:
        foundations[card_came_from_foundation - 1] = in_hand[0]

    in_hand = []
    hide_last_pile_card = False


def flip_cards():
    global flip_card
    for i, column in enumerate(board):
        if column and column[-1][1]:  # draw_card_back is True
            flipping_card.current_pos = (i * 146 + 20, (len(column) - 1) * 42 + 220)
            flipping_card.update_centre()
            flipping_card.do_flip = True
            flipping_card.flip_card = get_card_image(column[-1][0])
            flip_card = (i, column[-1][0])
            del column[-1]


def draw_hand():
    for i, card in enumerate(in_hand):
        dest = (pygame.mouse.get_pos()[0] - picked_up_pos[0],
                pygame.mouse.get_pos()[1] - picked_up_pos[1] + i * 42)
        screen.blit(get_card_image(card), dest)


def draw_moving_cards():
    global flip_animation_in_progress, move_animation_in_progress, moving_cards, moving_card_strings

    flip_animation_in_progress = False
    move_animation_in_progress = False

    was_flipping = flipping_card.flip_counter < 20
    flipping_card.flip()
    flipping_card.draw()

    # Just finished flipping, set the place it came from back to a real card
    if was_flipping and flipping_card.flip_counter >= 20:
        board[flip_card[0]].append([flip_card[1], False])
        flipping_card.do_flip = False
        flipping_card.flip_counter = 0
        flipping_card.sprite = card_back
        flipping_card.current_pos = (-200, -200)
        flipping_card.update_centre()

    if flipping_card.do_flip:
        flip_animation_in_progress = True

    was_moving_cards = False

    for moving_card in moving_cards:
        if not moving_card.arrived:
            was_moving_cards = True

        moving_card.move()
        moving_card.draw()

        if not moving_card.arrived:
            move_animation_in_progress = True

    # All cards finished moving
    if was_moving_cards and not move_animation_in_progress:
        for card in moving_card_strings:
            pile.append(card)
        moving_cards = []
        moving_card_strings = []

    # For when renewing the deck
    for i, returning_card in enumerate(returning_cards):
        returning_card.move()
        returning_card.draw()
        if returning_card.arrived:
            del returning_cards[i]
        else:
            move_animation_in_progress = True


def shift():
    global pile_shift, shift_animation_in_progress, pile, hide_last_pile_card
    pile_shift -= 5
    if pile_shift <= 0:
        shift_animation_in_progress = False


def win_screen():
    global game_over
    if "K♥" in foundations and "K♠" in foundations and "K♦" in foundations and "K♣" in foundations:
        game_over = True
        gfxdraw.filled_polygon(screen, ((0, 0), (0, SCREEN_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT), (SCREEN_WIDTH, 0)), (0, 0, 0, 100))
        win_text = font_2.render("You Win!", False, (255, 255, 255))
        screen.blit(win_text, win_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50)))
        screen.blit(home_icon, (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 + 50))
        screen.blit(replay_icon, (SCREEN_WIDTH // 2 + 150, SCREEN_HEIGHT // 2 + 50))


def draw_text():
    global clock_counter, time
    if not game_over:
        clock_counter += 1
    if clock_counter >= FPS:
        clock_counter = 0
        time += 1 if not game_over else 0

    time_text = font.render(f"Time: {convert_time(time)}", False, (255, 255, 255))
    screen.blit(time_text, (620, 20))

    moves_text = font.render(f"Moves: {moves}", False, (255, 255, 255))
    screen.blit(moves_text, (620, 70))


def reset():
    global deck, foundations, pile, board, in_hand, hide_last_pile_card, picked_up_pos, cards_came_from, click_pos
    global card_came_from_foundation, moving_cards, returning_cards, flipping_card, animation_in_proress
    global flip_animation_in_progress, move_animation_in_progress, flip_card, moving_card_strings, pile_shift
    global shift_animation_in_progress, game_over, clock_counter, time, moves

    deck = ["A♥", "2♥", "3♥", "4♥", "5♥", "6♥", "7♥", "8♥", "9♥", "10♥", "J♥", "Q♥", "K♥",
            "A♠", "2♠", "3♠", "4♠", "5♠", "6♠", "7♠", "8♠", "9♠", "10♠", "J♠", "Q♠", "K♠",
            "A♦", "2♦", "3♦", "4♦", "5♦", "6♦", "7♦", "8♦", "9♦", "10♦", "J♦", "Q♦", "K♦",
            "A♣", "2♣", "3♣", "4♣", "5♣", "6♣", "7♣", "8♣", "9♣", "10♣", "J♣", "Q♣", "K♣"]

    random.shuffle(deck)
    foundations = ["none", "none", "none", "none"]
    pile = []
    board = [[] for _ in range(7)]
    for i, column in enumerate(board):
        for card in range(i):
            board[i].append([deck.pop(random.randint(0, len(deck) - 1)), True])
        board[i].append([deck.pop(random.randint(0, len(deck) - 1)), False])

    in_hand = []
    hide_last_pile_card = False
    picked_up_pos = (0, 0)
    cards_came_from = ()
    click_pos = ()
    card_came_from_foundation = 0
    moving_cards = []
    returning_cards = []
    flipping_card = MovingCard((-200, -200), card_back)
    animation_in_proress = False
    flip_animation_in_progress = False
    move_animation_in_progress = False
    flip_card = (0, "none")
    moving_card_strings = []
    deck = deck[:-1]
    pile_shift = 0
    shift_animation_in_progress = False
    game_over = False
    clock_counter = FPS
    time = 0
    moves = 0


def solitaire():
    global click_pos

    SCREEN_WIDTH, SCREEN_HEIGHT = 1366 - 146, 768 + 100
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Solitaire")
    pygame.display.set_icon(pygame.image.load("card-game-assets/cards/card_diamonds_A.png"))

    running = True
    while running:
        timer.tick(FPS)

        animation_in_proress = flip_animation_in_progress or move_animation_in_progress or shift_animation_in_progress

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not animation_in_proress:
                if not game_over:
                    if event.button == 1:
                        click_pos = pygame.mouse.get_pos()
                        pick_up_card()
                else:
                    if pygame.Rect(SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 + 50, 100, 100).collidepoint(pygame.mouse.get_pos()):
                        running = False  # Clicked on the Home button
                    if pygame.Rect(SCREEN_WIDTH // 2 + 150, SCREEN_HEIGHT // 2 + 50, 100, 100).collidepoint(pygame.mouse.get_pos()):
                        reset()  # Clicked on the Replay button
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and in_hand:
                    put_down_card()
                    flip_cards()

        if shift_animation_in_progress:
            shift()

        screen.fill((0, 118, 58))
        screen.blit(background, (0, 0))
        draw_cards()
        draw_moving_cards()
        draw_text()
        draw_hand()
        win_screen()

        pygame.display.update()

    reset()


if __name__ == "__main__":
    solitaire()
    pygame.quit()
