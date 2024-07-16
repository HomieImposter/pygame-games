import pygame
import random
import math
import copy
from pygame import gfxdraw
pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1366, 768
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Uno")
pygame.display.set_icon(pygame.image.load("uno-assets/logo.png"))
timer = pygame.time.Clock()
FPS = 60
font1 = pygame.font.Font("fonts/Kenney Mini Square.ttf", 60)
font2 = pygame.font.Font("fonts/Kenney Pixel.ttf", 50)


def get_card(path):
    card = pygame.image.load("uno-assets/outline.png").convert_alpha()
    card_img = pygame.image.load(path).convert_alpha()
    card_img = pygame.transform.scale_by(card_img, 6)
    card.blit(card_img, (-40, -16))
    card.set_colorkey((0, 0, 0))
    return card


def get_cards(colour):
    cards = []
    for ending in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'draw', 'reverse', 'skip']:
        card = get_card(f"uno-assets/color_{colour}_{ending}.png")
        cards.append(card)
    return cards


red = get_cards("red")
yellow = get_cards("yellow")
green = get_cards("green")
blue = get_cards("blue")
wildcard = get_card("uno-assets/color_wild.png")
draw4 = get_card("uno-assets/color_draw.png")
card_back = get_card("uno-assets/color_back.png")
logo = pygame.image.load("uno-assets/logo.png").convert_alpha()
logo = pygame.transform.smoothscale_by(logo, 1/6)
home_icon = pygame.image.load("misc/Home Icon.png").convert_alpha()
replay_icon = pygame.image.load("misc/Replay Icon.png").convert_alpha()

deck = ['R0', 'R1', 'R1', 'R2', 'R2', 'R3', 'R3', 'R4', 'R4', 'R5', 'R5', 'R6', 'R6', 'R7', 'R7', 'R8', 'R8', 'R9', 'R9', 'RD', 'RD', 'RR', 'RR', 'RS', 'RS',
        'Y0', 'Y1', 'Y1', 'Y2', 'Y2', 'Y3', 'Y3', 'Y4', 'Y4', 'Y5', 'Y5', 'Y6', 'Y6', 'Y7', 'Y7', 'Y8', 'Y8', 'Y9', 'Y9', 'YD', 'YD', 'YR', 'YR', 'YS', 'YS',
        'G0', 'G1', 'G1', 'G2', 'G2', 'G3', 'G3', 'G4', 'G4', 'G5', 'G5', 'G6', 'G6', 'G7', 'G7', 'G8', 'G8', 'G9', 'G9', 'GD', 'GD', 'GR', 'GR', 'GS', 'GS',
        'B0', 'B1', 'B1', 'B2', 'B2', 'B3', 'B3', 'B4', 'B4', 'B5', 'B5', 'B6', 'B6', 'B7', 'B7', 'B8', 'B8', 'B9', 'B9', 'BD', 'BD', 'BR', 'BR', 'BS', 'BS',
        '0W', '0W', '0W', '0W', '0D', '0D', '0D', '0D']

game_state = [[] for _ in range(5)]
game_state[4] = deck.copy()
random.shuffle(game_state[4])
moving_cards = []
discard_pile = []
animation_in_progress = False
selected_card = -1
next_game_state = []
discarded_card = ''
current_player = random.randint(0, 3)
selected_colour = '0'  # For when a wildcard is played
set_up_complete = 0
direction = 1
card_played = False
next_player_draw = 0
prev_player_draw = 0
next_player_skip = False
added_card_ind = -1
highlighted_colour = ''
decide_colour = False
uno_counter = 0
won_round = -1
won_round_announcment_counter = 0
scores = [0 for _ in range(4)]
moving_scores = []
moving_scores_arrived = False
cards_move_countdown = 60
game_over = False


class MovingCard:
    def __init__(self, pos, sprite, target_pos=(0, 0), scale=1.0, target_scale=1.0, angle=0.0, target_angle=0.0, discard=False):
        self.target = target_pos
        self.origin = pos
        self.current_pos = pos
        self.progress = 0

        self.MAX_SPEED = 50
        self.sprite = sprite
        self.arrived = False

        self.do_flip = False
        self.flip_counter = 0
        self.flip_card = None

        self.scale = scale
        self.target_scale = target_scale
        self.draw_scale = scale

        self.angle = angle
        self.target_angle = target_angle
        self.draw_angle = angle
        # Always rotate in the fastest direction, CW or CCW
        if self.target_angle - self.angle < -180:
            self.target_angle += 360
        elif self.target_angle - self.angle > 180:
            self.target_angle -= 360

        self.discard = discard

    def move(self):
        if self.target != (0, 0) and self.target != self.origin:
            dx = self.target[0] - self.origin[0]
            dy = self.target[1] - self.origin[1]
            distance_vector = (dx, dy)
            distance = math.sqrt(dx**2 + dy**2)
            normalised_distance_vector = (distance_vector[0] / distance, distance_vector[1] / distance)

            dx = self.current_pos[0] - self.origin[0]
            dy = self.current_pos[1] - self.origin[1]
            self.progress = math.sqrt(dx**2 + dy**2) / distance
            if self.progress == 0:
                self.progress = 0.01
            speed = (-4*self.MAX_SPEED + 10) * self.progress ** 2 + (4*self.MAX_SPEED - 15) * self.progress + 5
            movement_vector = (normalised_distance_vector[0] * speed, normalised_distance_vector[1] * speed)
            self.current_pos = (self.current_pos[0] + movement_vector[0], self.current_pos[1] + movement_vector[1])

            if round(self.progress, 2) == 1:
                self.arrived = True
                self.current_pos = self.target
                self.target = (0, 0)
        else:
            self.arrived = True

    def flip(self):
        if self.do_flip and self.flip_card is not None:
            if self.progress > 0.5:
                self.sprite = self.flip_card

    def rescale(self):
        self.draw_scale = self.scale - (self.scale - self.target_scale) * self.progress

    def rotate(self):
        self.draw_angle = self.angle + (self.target_angle - self.angle) * self.progress

    def draw(self):
        if self.do_flip:
            draw_sprite = pygame.transform.scale(self.sprite, (112 * abs(self.progress - 0.5) * 2, 154))
        else:
            draw_sprite = self.sprite
        draw_sprite = pygame.transform.rotozoom(draw_sprite, self.draw_angle, self.draw_scale)
        draw_sprite.set_colorkey((0, 0, 0))
        screen.blit(draw_sprite, draw_sprite.get_rect(center=self.current_pos))


class MovingScore:
    def __init__(self, pos, score, target):
        self.pos = pos
        self.score = score
        self.target = target
        self.SPEED = 25
        self.arrived = False

    def move(self):
        if self.pos != self.target:
            distance_vector = (self.target[0] - self.pos[0], self.target[1] - self.pos[1])
            distance = math.sqrt(distance_vector[0] ** 2 + distance_vector[1] ** 2)
            normalised_distance_vector = (distance_vector[0] / distance, distance_vector[1] / distance)
            movement_vector = (normalised_distance_vector[0] * self.SPEED, normalised_distance_vector[1] * self.SPEED)
            self.pos = (self.pos[0] + movement_vector[0], self.pos[1] + movement_vector[1])

            if abs(self.target[0] - self.pos[0]) < self.SPEED and abs(self.target[1] - self.pos[1]) < self.SPEED:
                self.pos = self.target
        else:
            self.arrived = True


def get_card_image(card: str):
    # Input validation (for some reason)
    if len(card) != 2:
        raise ValueError("Expected card code of length 2")
    if card[0] not in list("RYGB0"):
        raise ValueError("Expected first character value of R/Y/G/B/0")
    if card[1] not in list("0123456789RSDW"):
        raise ValueError("Expected second character to be 0-9, 'D', 'R', 'S', 'W'")

    if card == '0W':
        return wildcard
    elif card == '0B':
        return card_back
    elif card == '0D':
        return draw4

    ind = 0
    if card[1].isdigit():
        ind = int(card[1])
    elif card[1] == 'D':
        ind = 10
    elif card[1] == 'R':
        ind = 11
    elif card[1] == 'S':
        ind = 12

    if card[0] == 'R':
        return red[ind]
    elif card[0] == 'Y':
        return yellow[ind]
    elif card[0] == 'G':
        return green[ind]
    elif card[0] == 'B':
        return blue[ind]


def get_card_value(card: str, ai_evaluaion=False):
    if card[0] == '0':
        return 50 if not ai_evaluaion else 0  # AI prefers to hold on to wildcards
    if card[1].isdigit():
        return int(card[1])
    else:
        return 20


def draw_hand(player: int, draw=True, hand: list | None = None):
    """player: int, 0 = human, 1-3 = AI (CW), (4 = draw/discard)"""
    global selected_card

    offset = 1380
    centre = [(683, SCREEN_HEIGHT + offset), (-offset, 384), (683, -offset), (SCREEN_WIDTH + offset, 384)][player]
    radius = 1500
    increment = 2.5

    if hand is None:
        hand = game_state[player]
    for i, card in enumerate(hand):
        if card is None:
            del hand[i]

    initial_angle = (len(hand) - 1) * -increment / 2
    initial_angle += player * 90
    cards = []

    # Calculate the positions & rotations for the cards
    for i, card_str in enumerate(hand):
        angle = initial_angle + i * increment
        x = centre[0] + radius * math.cos(math.radians(angle - 90))
        y = centre[1] + radius * math.sin(math.radians(angle - 90))

        card = get_card_image(card_str) if player == 0 else card_back
        card = pygame.transform.rotozoom(card, -angle, 1)
        card_rect = card.get_rect(center=(x, y))
        mask = pygame.mask.from_surface(card)

        if card_rect.collidepoint(pygame.mouse.get_pos()) and player == 0 and won_round == -1:  # Mouse over card & user/human player
            if mask.get_at((pygame.mouse.get_pos()[0] - card_rect.x, pygame.mouse.get_pos()[1] - card_rect.y)):
                selected_card = i if draw else selected_card

        cards.append([card_str, card, card_rect, angle])

    positions = []

    # Draw them, bigger if selected
    for i, card in enumerate(cards):
        if i == selected_card and player == current_player == 0 and draw:
            draw_card = get_card_image(card[0])
            draw_card = pygame.transform.rotozoom(draw_card, -card[3], 1.1)
            x = centre[0] + (radius + 112-112/1.1) * math.cos(math.radians(card[3] - 90 - 0.5))
            y = centre[1] + (radius + 154-154/1.1) * math.sin(math.radians(card[3] - 90 - 0.5))
            if draw:
                screen.blit(draw_card, draw_card.get_rect(center=(x, y)))
            else:
                positions.append([(x, y), -card[3]])
        else:
            if draw:
                screen.blit(card[1], card[2])
            else:
                positions.append([card[2].center, -card[3]])

    if not draw:
        return positions


def draw_decorations():
    global selected_card

    # Draw pile
    screen.blit(card_back, card_back.get_rect(center=(SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT // 2 + 10)))
    screen.blit(card_back, card_back.get_rect(center=(SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT // 2 + 5)))
    screen.blit(card_back, card_back.get_rect(center=(SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT // 2)))

    if pygame.Rect(SCREEN_WIDTH//2 + 100 - 56, SCREEN_HEIGHT//2 - 77, 112, 164).collidepoint(pygame.mouse.get_pos()):
        selected_card = -2

    # Discard pile
    for i, card in enumerate(discard_pile):
        if len(discard_pile) - i < 10:  # Only draw the last 10 cards, looks better this way
            card_surf = card[0]
            card_surf = pygame.transform.rotozoom(card_surf, card[1], 1)
            card_rect = card_surf.get_rect(center=card[2])
            screen.blit(card_surf, card_rect)

    if discarded_card and discarded_card[0] == '0' and selected_colour != '0' and not (won_round or game_over):
        colour = (0, 0, 0)
        if selected_colour == 'R':
            colour = (245, 44, 78)
        elif selected_colour == 'Y':
            colour = (255, 173, 47)
        elif selected_colour == 'G':
            colour = (0, 150, 50)
        elif selected_colour == 'B':
            colour = (0, 72, 167)

        gfxdraw.filled_circle(screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 12, (255, 255, 255))
        gfxdraw.aacircle(screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 12, (255, 255, 255))

        gfxdraw.filled_circle(screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 10, colour)
        gfxdraw.aacircle(screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 10, colour)


def draw_moving_cards():
    all_arrived = True
    for card in moving_cards:
        card.move()
        card.flip()
        card.rescale()
        card.rotate()
        card.draw()
        if not card.arrived:
            all_arrived = False

    if all_arrived:
        convert_obj_to_game_state()


def convert_obj_to_game_state():
    global moving_cards, game_state, animation_in_progress, set_up_complete, card_played, current_player
    global next_player_skip, next_player_draw, selected_card, discarded_card, prev_player_draw

    for card in moving_cards:
        if card.discard:
            discard_pile.append((card.sprite, card.target_angle, card.current_pos))
    moving_cards = []
    game_state = copy.deepcopy(next_game_state)
    animation_in_progress = False

    if set_up_complete >= 2:
        if added_card_ind != -1 and move_is_legal(current_player, added_card_ind) and next_player_draw == prev_player_draw == 0:
            selected_card = added_card_ind
            convert_game_state_to_obj()
            return

        if card_played:
            action()
            card_played = False

        if next_player_skip:
            current_player += direction
            next_player_skip = False

        current_player += direction if next_player_draw == 0 and not decide_colour else 0
        current_player %= 4

        if next_player_draw:
            selected_card = -2
            convert_game_state_to_obj()
            next_player_draw -= 1
        if prev_player_draw:
            prev_player_draw -= 1

    elif set_up_complete == 1:  # Phase 2 of setup, draw first card
        animation_in_progress = True
        discarded_card = game_state[4].pop()
        while discarded_card[0] == '0':
            discarded_card = game_state[4].pop()
        moving_card = MovingCard((SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT // 2), card_back, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2), discard=True)
        moving_card.MAX_SPEED = 20
        moving_card.flip_card = get_card_image(discarded_card)
        moving_card.do_flip = True
        moving_cards.append(moving_card)

        for i, hand in enumerate(game_state[:4]):
            for j, card in enumerate(hand):
                pos, angle = draw_hand(i, draw=False)[j]
                target_pos, target_angle = draw_hand(i, draw=False)[j]
                sprite = get_card_image(card) if i == 0 else card_back

                moving_card = MovingCard(pos, sprite, target_pos, 1, 1, angle, target_angle)
                moving_card.MAX_SPEED = 5
                moving_cards.append(moving_card)

        action()  # Do action the first card, rules say so

    elif set_up_complete == -1:
        set_up_complete += 1
        set_up()

    else:
        set_up_complete += 1
        convert_obj_to_game_state()

    set_up_complete += 1


def convert_game_state_to_obj():
    global animation_in_progress, next_game_state, game_state, discarded_card, card_played, added_card_ind

    animation_in_progress = True
    next_game_state = [[] for _ in range(4)]
    next_game_state.append(game_state[4].copy())
    added_card_ind = -1

    for i, hand in enumerate(game_state):
        if i == 4:  # Draw pile
            continue

        next_hand = hand.copy()
        next_discarded_card = ''
        next_added_card = ''
        next_added_card_ind = -1
        card_discarded = False
        card_added = False

        if i == current_player:
            if selected_card == -2:  # Draw from draw pile
                next_hand.append(game_state[4][-1])
                if current_player == 0:
                    next_hand.sort()
                next_added_card = game_state[4][-1]
                next_added_card_ind = next_hand.index(next_added_card)
                if current_player != 0:
                    next_added_card_ind = len(game_state[current_player])
                added_card_ind = next_added_card_ind
                del next_game_state[4][-1]
            else:  # Play a card
                next_discarded_card = hand[selected_card]
                del next_hand[selected_card]
                card_played = True

        if next_discarded_card:
            # CARD DISCARDED
            for j, card in enumerate(hand):
                if card == next_discarded_card and j == selected_card:
                    # DISCARD
                    pos, angle = draw_hand(i, draw=False)[j]
                    target_pos = (SCREEN_WIDTH // 2 - 100 + random.randint(-5, 5), SCREEN_HEIGHT // 2 + random.randint(-5, 5))
                    target_angle = random.uniform(-10, 10)
                    scale = 1.1 if i == 0 else 1
                    sprite = get_card_image(next_discarded_card) if i == 0 else card_back

                    moving_card = MovingCard(pos, sprite, target_pos, scale, 1, angle, target_angle, discard=True)
                    moving_card.MAX_SPEED = 20
                    if i != 0:
                        moving_card.flip_card = get_card_image(next_discarded_card)
                        moving_card.do_flip = True
                    moving_cards.append(moving_card)
                    card_discarded = True
                else:
                    # HAND
                    ind = j - 1 if card_discarded else j

                    pos, angle = draw_hand(i, draw=False)[j]
                    target_pos, target_angle = draw_hand(i, draw=False, hand=next_hand)[ind]
                    sprite = get_card_image(card) if i == 0 else card_back

                    moving_card = MovingCard(pos, sprite, target_pos, 1, 1, angle, target_angle)
                    moving_card.MAX_SPEED = 5
                    moving_cards.append(moving_card)
        elif next_added_card:
            # CARD ADDED
            for j, card in enumerate(next_hand):
                # ADD
                if next_added_card and j == next_added_card_ind:
                    pos = (SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT // 2)
                    target_pos, target_angle = draw_hand(i, draw=False, hand=next_hand)[j]

                    moving_card = MovingCard(pos, card_back, target_pos, 1, 1, 0, target_angle)
                    moving_card.MAX_SPEED = 20
                    if i == 0:
                        moving_card.flip_card = get_card_image(next_added_card)
                        moving_card.do_flip = True
                    moving_cards.append(moving_card)
                    card_added = True
                else:
                    # HAND
                    ind = j - 1 if card_added else j

                    pos, angle = draw_hand(i, draw=False)[ind]
                    target_pos, target_angle = draw_hand(i, draw=False, hand=next_hand)[j]
                    sprite = get_card_image(card) if i == 0 else card_back

                    moving_card = MovingCard(pos, sprite, target_pos, 1, 1, angle, target_angle)
                    moving_card.MAX_SPEED = 5
                    moving_cards.append(moving_card)
        else:
            # NO CHANGE
            for j, card in enumerate(hand):
                # HAND
                pos, angle = draw_hand(i, draw=False)[j]
                target_pos, target_angle = draw_hand(i, draw=False, hand=next_hand)[j]
                sprite = get_card_image(card) if i == 0 else card_back

                moving_card = MovingCard(pos, sprite, target_pos, 1, 1, angle, target_angle)
                moving_card.MAX_SPEED = 5
                moving_cards.append(moving_card)

        next_game_state[i] = next_hand

        if next_discarded_card:
            discarded_card = next_discarded_card


def move_is_legal(player, ind):
    card = game_state[player][ind]
    if card == '0D':
        # Draw 4 card, only playable if no other moves are available
        playable = True
        for i, other_card in enumerate(game_state[player]):
            if other_card != '0D' and move_is_legal(player, i):
                playable = False
        return playable
    if card == '0W':
        return True  # Wildcard
    if card[0] == discarded_card[0] or (card[1] == discarded_card[1] and card[0] != '0' and discarded_card[0] != '0'):
        return True  # Colour or number match (extra to prevent Draw 4 and Draw 2 from mixing)
    if discarded_card[0] == '0' and card[0] == selected_colour:
        return True  # Prev was wildcard and this is correct colour

    return False  # All other cases, move is not legal


def choose_move(player):
    global selected_colour

    legal_moves = []
    for i, move in enumerate(game_state[player]):
        if move_is_legal(player, i):
            legal_moves.append((get_card_value(move, ai_evaluaion=True), move))

    if legal_moves:
        # Chooses the move with the highest value
        legal_moves.sort()
        legal_moves.reverse()
        move = legal_moves[0][1]
        chosen_move = game_state[player].index(move)
        if move[0] == '0':  # A wild card
            # Randomly chooses a colour from its hand, incidentally proportional to how many of that colour it has
            colours = [card[0] for card in game_state[player] if card[0] != '0']
            colours = list("RYGB") if not colours else colours  # Just in case they only have wildcards
            selected_colour = random.choice(colours)
    else:
        chosen_move = -2

    return chosen_move


def set_up():
    global animation_in_progress, next_game_state, discarded_card

    animation_in_progress = True
    next_game_state = copy.deepcopy(game_state)

    # Initialise the hands with 7 cards each
    for player in range(4):
        next_game_state[player] = [next_game_state[4].pop() for _ in range(7)]
    next_game_state[0].sort()

    # Convert all the hands to obj
    for i, next_hand in enumerate(next_game_state):
        if i == 4:  # Draw pile
            continue
        for j, card in enumerate(next_hand):
            pos = (SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT // 2)
            target_pos, target_angle = draw_hand(i, draw=False, hand=next_hand)[j]

            moving_card = MovingCard(pos, card_back, target_pos, 1, 1, 0, target_angle)
            moving_card.MAX_SPEED = 20
            if i == 0:
                moving_card.flip_card = get_card_image(card)
                moving_card.do_flip = True
            moving_cards.append(moving_card)


def action():
    global direction, next_player_draw, prev_player_draw, next_player_skip, decide_colour, selected_colour, uno_counter,  won_round, won_round_announcment_counter

    if discarded_card[1] == 'R':  # Reverse
        direction *= -1
    elif discarded_card == '0D':  # Draw 4
        next_player_draw = 4
        prev_player_draw = 5
        next_player_skip = True  # Cheeky way of making it go onto the next person before dealing them cards
    elif discarded_card[1] == 'D':  # Draw 2
        next_player_draw = 2
        prev_player_draw = 3
        next_player_skip = True  # Cheeky way of making it go onto the next person before dealing them cards
    elif discarded_card[1] == 'S':  # Skip
        next_player_skip = True

    if discarded_card[0] == '0' and current_player == 0:
        selected_colour = '0'
        decide_colour = True

    if len(game_state[current_player]) == 1:
        uno_counter = 60
    elif len(game_state[current_player]) == 0:
        won_round = current_player
        won_round_announcment_counter = 100
        selected_colour = '0'


def draw_choose_colour_screen():
    global highlighted_colour

    highlighted_colour = ''
    colours = [(245, 44, 78), (255, 173, 47), (0, 150, 50), (0, 72, 167)]

    for i, colour in enumerate(colours):
        a, b = [(-1, -1), (1, -1), (-1, 1), (1, 1)][i]
        offset = 80
        gfxdraw.filled_circle(screen, SCREEN_WIDTH // 2 + offset * a, SCREEN_HEIGHT // 2 + offset * b, 60, (255, 255, 255))
        gfxdraw.aacircle(screen, SCREEN_WIDTH // 2 + offset * a, SCREEN_HEIGHT // 2 + offset * b, 60, (0, 0, 0))

        gfxdraw.filled_circle(screen, SCREEN_WIDTH // 2 + offset * a, SCREEN_HEIGHT // 2 + offset * b, 50, colour)
        gfxdraw.aacircle(screen, SCREEN_WIDTH // 2 + offset * a, SCREEN_HEIGHT // 2 + offset * b, 50, colour)

        if pygame.Rect(SCREEN_WIDTH // 2 + offset * a - 60, SCREEN_HEIGHT // 2 + offset * b - 60, 120, 120).collidepoint(pygame.mouse.get_pos()):
            highlighted_colour = ['R', 'Y', 'G', 'B'][i]


def round_over_sequence():
    global won_round, won_round_announcment_counter, cards_move_countdown, animation_in_progress, current_player, selected_colour
    global next_game_state, set_up_complete, discard_pile, game_over, moving_scores_arrived, moving_scores, added_card_ind

    if won_round_announcment_counter:
        won_round_announcment_counter -= 1
        gfxdraw.filled_polygon(screen, ((0, 0), (0, SCREEN_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT), (SCREEN_WIDTH, 0)), (0, 0, 0, 100))
        round_winner = font1.render(f"Player {won_round + 1} wins", False, (255, 255, 255))
        round_winner_rect = round_winner.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(round_winner, round_winner_rect)
    else:
        if moving_scores_arrived:
            # Move the cards to the draw pile
            cards_move_countdown = 60
            moving_scores_arrived = False

            for card in discard_pile:
                moving_card = MovingCard(card[2], card[0], (SCREEN_WIDTH//2 + 100, SCREEN_HEIGHT//2), 1, 1, card[1], 0)
                moving_card.MAX_SPEED = 5
                moving_card.flip_card = card_back
                moving_card.do_flip = True
                moving_cards.append(moving_card)

            for i, hand in enumerate(game_state[:4]):
                for j, card in enumerate(hand):
                    pos, angle = draw_hand(i, False)[j]
                    sprite = get_card_image(card) if i == 0 else card_back

                    moving_card = MovingCard(pos, sprite, (SCREEN_WIDTH//2 + 100, SCREEN_HEIGHT//2), 1, 1, angle, 0)
                    moving_card.MAX_SPEED = 25
                    if i == 0:
                        moving_card.flip_card = card_back
                        moving_card.do_flip = True
                    moving_cards.append(moving_card)

            animation_in_progress = True
            next_game_state = [[] for _ in range(5)]
            next_game_state[4] = deck.copy()
            random.shuffle(next_game_state[4])
            discard_pile = []
            moving_scores = []
            current_player = won_round - 1  # -1 because it increments anyway
            current_player %= 4
            added_card_ind = -1
            selected_colour = '0'

            for score in scores:
                if score >= 500:
                    game_over = True
            if not game_over:
                set_up_complete = -1  # Re-deal the cards
                won_round = -1

        elif not moving_scores:
            # Create the moving score objects
            for i, hand in enumerate(game_state[:4]):
                for j, card in enumerate(hand):
                    pos = draw_hand(i, False)[j][0]
                    dest = [(683, 745), (20, 384), (683, 20), (1345, 384)][won_round]
                    moving_scores.append(MovingScore(pos, get_card_value(card), dest))
        else:
            draw_moving_scores()


def draw_scores():
    for i, score in enumerate(scores):
        centre = [(683, 745), (20, 384), (683, 20), (1345, 384)][i]
        rotation = [0, -90, 0, 90][i]
        score_text = font2.render(str(score), False, (255, 255, 255))
        score_text = pygame.transform.rotate(score_text, rotation)
        screen.blit(score_text, score_text.get_rect(center=centre))


def draw_moving_scores():
    global moving_scores_arrived, cards_move_countdown

    moving_scores_arrived = True
    decreased = False

    for i, moving_score in enumerate(moving_scores):
        if cards_move_countdown != 0:
            cards_move_countdown -= 1 if not decreased else 0
            decreased = True
        else:
            moving_score.move()

        score_text = font2.render(str(moving_score.score), False, (255, 255, 255))
        screen.blit(score_text, score_text.get_rect(center=moving_score.pos))

        if moving_score.arrived:
            scores[won_round] += moving_score.score
            del moving_scores[i]
        else:
            moving_scores_arrived = False


def draw_game_over_screen():
    gfxdraw.filled_polygon(screen, ((0, 0), (0, SCREEN_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT), (SCREEN_WIDTH, 0)), (0, 0, 0, 100))
    round_winner = font1.render(f"Player {won_round + 1} wins", False, (255, 255, 255))
    round_winner_rect = round_winner.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(round_winner, round_winner_rect)

    screen.blit(home_icon, (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 + 50))
    screen.blit(replay_icon, (SCREEN_WIDTH // 2 + 150, SCREEN_HEIGHT // 2 + 50))


def reset():
    global scores, won_round, set_up_complete, game_over

    scores = [0 for _ in range(4)]
    won_round = -1
    game_over = False
    set_up_complete = 0
    set_up()


def uno():
    global decide_colour, uno_counter, current_player, selected_colour, highlighted_colour, selected_card

    SCREEN_WIDTH, SCREEN_HEIGHT = 1366, 768
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Uno")
    pygame.display.set_icon(pygame.image.load("uno-assets/logo.png"))
    set_up()

    running = True
    while running:
        timer.tick(FPS)

        selected_card = -1

        screen.fill((0, 118, 58))
        draw_decorations()
        if animation_in_progress:
            draw_moving_cards()
        else:
            for player in range(4):
                draw_hand(player)
            if decide_colour:
                draw_choose_colour_screen()
        if uno_counter:
            screen.blit(logo, logo.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))
            uno_counter -= 1
        draw_scores()

        if won_round >= 0 and not (animation_in_progress or game_over):
            round_over_sequence()
        if game_over:
            draw_game_over_screen()

        if current_player != 0 and won_round < 0 and not (animation_in_progress or decide_colour or uno_counter):
            selected_card = choose_move(current_player)
            convert_game_state_to_obj()

        # Somewhat crude fix for a rare bug where AI doesn't choose a colour
        if discarded_card and discarded_card[0] == selected_colour == '0' and not (animation_in_progress or decide_colour):
            with open("misc/feedback.txt", 'a') as file:
                file.write(f"Uno: DEBUG: No colour was chosen so one was picked at random {game_state = }\n")
            selected_colour = random.choice(list("RYGB"))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0] and not uno_counter:
                    if won_round < 0:
                        if decide_colour and highlighted_colour:
                            selected_colour = highlighted_colour
                            highlighted_colour = ''
                            decide_colour = False
                            current_player += direction
                            current_player %= 4
                        elif current_player == 0 and not animation_in_progress and selected_card == -2 or (selected_card != -1 and move_is_legal(0, selected_card)):
                            convert_game_state_to_obj()
                    else:
                        if pygame.Rect(SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 + 50, 100, 100).collidepoint(pygame.mouse.get_pos()):
                            running = False  # Clicked home icon
                        elif pygame.Rect(SCREEN_WIDTH // 2 + 150, SCREEN_HEIGHT // 2 + 50, 100, 100).collidepoint(pygame.mouse.get_pos()):
                            reset()  # Clicked replay icon

        pygame.display.update()


if __name__ == "__main__":
    uno()
    pygame.quit()
