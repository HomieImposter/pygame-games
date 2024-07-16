import pygame
from pygame import gfxdraw
import copy
pygame.init()
pygame.mixer.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1366, 768
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Chess")
pygame.display.set_icon(pygame.image.load("chess-assets/pieces/Black Pawn.png"))
font = pygame.sysfont.SysFont("franklingothicmedium", 50)
timer = pygame.time.Clock()
FPS = 60

black_king = pygame.transform.smoothscale(pygame.image.load("chess-assets/pieces/Black King.png"), (88, 88))
black_queen = pygame.transform.smoothscale(pygame.image.load("chess-assets/pieces/Black Queen.png"), (88, 88))
black_rook = pygame.transform.smoothscale(pygame.image.load("chess-assets/pieces/Black Rook.png"), (88, 88))
black_bishop = pygame.transform.smoothscale(pygame.image.load("chess-assets/pieces/Black Bishop.png"), (88, 88))
black_knight = pygame.transform.smoothscale(pygame.image.load("chess-assets/pieces/Black Knight.png"), (88, 88))
black_pawn = pygame.transform.smoothscale(pygame.image.load("chess-assets/pieces/Black Pawn.png"), (88, 88))

white_king = pygame.transform.smoothscale(pygame.image.load("chess-assets/pieces/White King.png"), (88, 88))
white_queen = pygame.transform.smoothscale(pygame.image.load("chess-assets/pieces/White Queen.png"), (88, 88))
white_rook = pygame.transform.smoothscale(pygame.image.load("chess-assets/pieces/White Rook.png"), (88, 88))
white_bishop = pygame.transform.smoothscale(pygame.image.load("chess-assets/pieces/White Bishop.png"), (88, 88))
white_knight = pygame.transform.smoothscale(pygame.image.load("chess-assets/pieces/White Knight.png"), (88, 88))
white_pawn = pygame.transform.smoothscale(pygame.image.load("chess-assets/pieces/White Pawn.png"), (88, 88))

sound_on_icon = pygame.transform.smoothscale(pygame.image.load("chess-assets/icons/Sound On.png"), (96, 74))
sound_off_icon = pygame.transform.smoothscale(pygame.image.load("chess-assets/icons/Sound Off.png"), (78, 74))
flip_icon = pygame.image.load("chess-assets/icons/Flip Icon.png").convert_alpha()
home_icon = pygame.image.load("misc/Home Icon.png").convert_alpha()
replay_icon = pygame.image.load("misc/Replay Icon.png").convert_alpha()

move_sound = pygame.mixer.Sound("chess-assets/audio/move-self.mp3")
capture_sound = pygame.mixer.Sound("chess-assets/audio/capture.mp3")

black_pieces = [black_king, black_queen, black_rook, black_bishop, black_knight, black_pawn]
white_pieces = [white_king, white_queen, white_rook, white_bishop, white_knight, white_pawn]

display_board = pygame.Surface((704, 704))
take_piece_circle = pygame.Surface((88, 88), pygame.SRCALPHA, 32)
gfxdraw.filled_circle(take_piece_circle, 44, 44, 44, (100, 100, 100, 100))
pygame.draw.circle(take_piece_circle, (0, 0, 0, 0), (44, 44), 30)
take_piece_circle.convert_alpha()

in_hand = [0, (0, 0)]
white_turn = True
white_in_check = False
black_in_check = False
white_checkmate = False
black_checkmate = False
white_can_castle = [True, True]  # Left, Right
black_can_castle = [True, True]
stalemate = False
game_over = False
sound_on = True
sound_rect = pygame.Rect(80, 630, 136, 114)
flipped = False

board = [[13, 15, 14, 12, 11, 14, 15, 13],
         [16, 16, 16, 16, 16, 16, 16, 16],
         [0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0, 0, 0, 0],
         [6, 6, 6, 6, 6, 6, 6, 6],
         [3, 5, 4, 2, 1, 4, 5, 3]]


def draw_board():
    display_board.fill((209, 139, 71))
    for i in range(0, 8, 2):
        for j in range(0, 8):
            pygame.draw.rect(display_board, (255, 206, 158), (88 * i + 88 * (j % 2), 88 * j, 88, 88))

    for y, _ in enumerate(board):
        for x, _ in enumerate(board):
            draw_x = 7 - x if flipped else x

            if 0 < board[x][y] < 10:
                display_board.blit(white_pieces[board[x][y] - 1], (y*88, draw_x*88))
            elif board[x][y] > 10:
                display_board.blit(black_pieces[board[x][y] - 11], (y*88, draw_x*88))

    screen.blit(display_board, ((SCREEN_WIDTH - 704) / 2, (SCREEN_HEIGHT - 704) / 2))


def draw_hand():
    if in_hand[0] == 0:
        return
    if 0 < in_hand[0] < 10:
        screen.blit(white_pieces[in_hand[0] - 1], (pygame.mouse.get_pos()[0] - 44, pygame.mouse.get_pos()[1] - 44))
    elif in_hand[0] > 10:
        screen.blit(black_pieces[in_hand[0] - 11], (pygame.mouse.get_pos()[0] - 44, pygame.mouse.get_pos()[1] - 44))


def draw_valid_moves():
    if in_hand[0] != 0:
        valid_moves = calculate_moves(in_hand[0], in_hand[1], white_turn)
        for grid_y, grid_x in valid_moves:
            draw_y = 7 - grid_y if flipped else grid_y

            x = grid_x * 88 + 44 + (SCREEN_WIDTH - 704) // 2
            y = draw_y * 88 + 44 + (SCREEN_HEIGHT - 704) // 2

            if board[grid_y][grid_x] == 0:
                gfxdraw.filled_circle(screen, x, y, 20, (100, 100, 100, 50))
            else:
                screen.blit(take_piece_circle, (x - 44, y - 44))


def draw_side_info():
    white_header = font.render("White", True, (250, 250, 250))
    white_header_rect = white_header.get_rect(center=((SCREEN_WIDTH - 704) / 4, 55))
    black_header = font.render("Black", True, (250, 250, 250))
    black_header_rect = black_header.get_rect(center=(SCREEN_WIDTH - (SCREEN_WIDTH - 704) / 4, 55))
    if white_turn:
        pygame.draw.rect(screen, (55, 143, 30), (30, (SCREEN_HEIGHT - 704) // 2, (SCREEN_WIDTH - 704) // 2 - 60, 50))
    else:
        pygame.draw.rect(screen, (55, 143, 30), (SCREEN_WIDTH - (SCREEN_WIDTH - 704) // 2 + 30, (SCREEN_HEIGHT - 704) // 2, (SCREEN_WIDTH - 704) // 2 - 60, 50))
    screen.blit(white_header, white_header_rect)
    screen.blit(black_header, black_header_rect)

    if white_in_check or white_checkmate:
        if white_checkmate:
            text = "Checkmate!"
        else:
            text = "Check!"
        pygame.draw.rect(screen, (166, 22, 22), (30, (SCREEN_HEIGHT - 704) // 2 + 80, (SCREEN_WIDTH - 704) // 2 - 60, 50))
        check = font.render(text, True, (250, 250, 250))
        check_rect = check.get_rect(center=((SCREEN_WIDTH - 704) / 4, 135))
        screen.blit(check, check_rect)
    if black_in_check or black_checkmate:
        if black_checkmate:
            text = "Checkmate!"
        else:
            text = "Check!"
        pygame.draw.rect(screen, (166, 22, 22), (SCREEN_WIDTH - (SCREEN_WIDTH - 704) // 2 + 30, (SCREEN_HEIGHT - 704) // 2 + 80, (SCREEN_WIDTH - 704) // 2 - 60, 50))
        check = font.render(text, True, (250, 250, 250))
        check_rect = check.get_rect(center=(SCREEN_WIDTH - (SCREEN_WIDTH - 704) / 4, 135))
        screen.blit(check, check_rect)
    if stalemate:
        pygame.draw.rect(screen, (222, 120, 11), (30, (SCREEN_HEIGHT - 704) // 2 + 80, (SCREEN_WIDTH - 704) // 2 - 60, 50))
        pygame.draw.rect(screen, (222, 120, 11), (SCREEN_WIDTH - (SCREEN_WIDTH - 704) // 2 + 30, (SCREEN_HEIGHT - 704) // 2 + 80, (SCREEN_WIDTH - 704) // 2 - 60, 50))
        stalemate_text = font.render("Stalemate", True, (250, 250, 250))
        screen.blit(stalemate_text, stalemate_text.get_rect(center=((SCREEN_WIDTH - 704) / 4, 135)))
        screen.blit(stalemate_text, stalemate_text.get_rect(center=(SCREEN_WIDTH - (SCREEN_WIDTH - 704) / 4, 135)))

    if sound_on:
        screen.blit(sound_on_icon, (100, 650))
    else:
        screen.blit(sound_off_icon, (100, 650))

    screen.blit(flip_icon, (SCREEN_WIDTH - 200, SCREEN_HEIGHT - 130))


def pick_up_piece():
    global in_hand, board
    if in_hand[0] != 0:
        return
    if pygame.mouse.get_pos()[0] < (SCREEN_WIDTH - 704) / 2 or pygame.mouse.get_pos()[0] >= (SCREEN_WIDTH - 704) / 2 + 704:
        return
    if pygame.mouse.get_pos()[1] < (SCREEN_HEIGHT - 704) / 2 or pygame.mouse.get_pos()[1] >= (SCREEN_HEIGHT - 704) / 2 + 704:
        return

    grid_x = (pygame.mouse.get_pos()[1] - (SCREEN_HEIGHT - 704) // 2) // 88
    grid_y = (pygame.mouse.get_pos()[0] - (SCREEN_WIDTH - 704) // 2) // 88

    grid_x = 7 - grid_x if flipped else grid_x

    if (0 < board[grid_x][grid_y] < 10 and white_turn) or (board[grid_x][grid_y] > 10 and not white_turn):
        in_hand = [board[grid_x][grid_y], (grid_x, grid_y)]
        board[grid_x][grid_y] = 0


def put_down_piece():
    global in_hand, board, white_turn
    global white_in_check, black_in_check
    global white_can_castle, black_can_castle

    if in_hand[0] == 0:
        return
    if pygame.mouse.get_pos()[0] < (SCREEN_WIDTH - 704) / 2 or pygame.mouse.get_pos()[0] > (SCREEN_WIDTH - 704) / 2 + 704:
        board[in_hand[1][0]][in_hand[1][1]] = in_hand[0]
        in_hand[0] = 0
        return
    if pygame.mouse.get_pos()[1] < (SCREEN_HEIGHT - 704) / 2 or pygame.mouse.get_pos()[1] > (SCREEN_HEIGHT - 704) / 2 + 704:
        board[in_hand[1][0]][in_hand[1][1]] = in_hand[0]
        in_hand[0] = 0
        return

    grid_x = (pygame.mouse.get_pos()[1] - (SCREEN_HEIGHT - 704) // 2) // 88
    grid_y = (pygame.mouse.get_pos()[0] - (SCREEN_WIDTH - 704) // 2) // 88

    grid_x = 7 - grid_x if flipped else grid_x

    if (grid_x, grid_y) in calculate_moves(in_hand[0], in_hand[1], white_turn):
        # Move rook if castled
        if white_can_castle[0] and in_hand[0] == 1 and grid_y == 2:
            board[7][3] = 3
            board[7][0] = 0
        elif white_can_castle[1] and in_hand[0] == 1 and grid_y == 6:
            board[7][5] = 3
            board[7][7] = 0
        elif black_can_castle[0] and in_hand[0] == 11 and grid_y == 2:
            board[0][3] = 13
            board[0][0] = 0
        elif black_can_castle[1] and in_hand[0] == 11 and grid_y == 6:
            board[0][5] = 13
            board[0][7] = 0

        # Lose castling rights
        if in_hand[0] == 1:
            white_can_castle = [False, False]
        elif in_hand[0] == 3 and in_hand[1][1] == 0:
            white_can_castle[0] = False
        elif in_hand[0] == 3 and in_hand[1][1] == 7:
            white_can_castle[1] = False
        elif in_hand[0] == 11:
            black_can_castle = [False, False]
        elif in_hand[0] == 13 and in_hand[1][1] == 0:
            black_can_castle[0] = False
        elif in_hand[0] == 13 and in_hand[1][1] == 7:
            black_can_castle[1] = False

        if sound_on:
            if board[grid_x][grid_y] == 0:
                move_sound.play()
            else:
                capture_sound.play()

        board[grid_x][grid_y] = in_hand[0]
        in_hand[0] = 0
        white_in_check, black_in_check = check_in_check()
        white_turn = not white_turn
    else:
        board[in_hand[1][0]][in_hand[1][1]] = in_hand[0]
        in_hand[0] = 0


def check_promotion(draw=True, mouse_pos=(0, 0)):
    global white_in_check, black_in_check
    if 6 in board[0]:
        grid_y = 0
        grid_x = board[0].index(6)
    elif 16 in board[7]:
        grid_y = 7
        grid_x = board[7].index(16)
    else:
        return False

    y = grid_y * 88 + (SCREEN_HEIGHT - 704) // 2 - 51
    x = grid_x * 88 + (SCREEN_WIDTH - 704) // 2 - 51

    y += -30 if white_turn else 30
    y = SCREEN_HEIGHT - y - 191 if flipped else y

    if draw:
        gfxdraw.filled_polygon(screen, ((x, y), (x + 191, y), (x + 191, y + 191), (x, y + 191)), (117, 74, 33, 200))
        if white_turn:
            screen.blit(black_queen, (x + 5, y + 5))
            screen.blit(black_rook, (x + 98, y + 5))
            screen.blit(black_knight, (x + 5, y + 98))
            screen.blit(black_bishop, (x + 98, y + 98))
        else:
            screen.blit(white_queen, (x + 5, y + 5))
            screen.blit(white_rook, (x + 98, y + 5))
            screen.blit(white_knight, (x + 5, y + 98))
            screen.blit(white_bishop, (x + 98, y + 98))

    if pygame.Rect(x+5, y+5, 88, 88).collidepoint(mouse_pos):
        board[grid_y][grid_x] = 2
    elif pygame.Rect(x+98, y+5, 88, 88).collidepoint(mouse_pos):
        board[grid_y][grid_x] = 3
    elif pygame.Rect(x+5, y+98, 88, 88).collidepoint(mouse_pos):
        board[grid_y][grid_x] = 5
    elif pygame.Rect(x+98, y+98, 88, 88).collidepoint(mouse_pos):
        board[grid_y][grid_x] = 4
    else:
        return True

    board[grid_y][grid_x] += 10 if white_turn else 0
    white_in_check, black_in_check = check_in_check()


def check_in_check():
    white_check = False
    black_check = False
    for x, y in calculate_all_moves(True):
        if board[x][y] == 11:
            black_check = True
    for x, y in calculate_all_moves(False):
        if board[x][y] == 1:
            white_check = True
    return white_check, black_check


def check_checkmate():
    global white_in_check, black_in_check, white_checkmate, black_checkmate, stalemate
    if in_hand[0] != 0:
        return
    white_in_check, black_in_check = check_in_check()
    legal_moves = set()
    for i, _ in enumerate(board):
        for j, _ in enumerate(board[i]):
            piece = board[i][j]
            if 0 < piece < 10 and white_turn or piece > 10 and not white_turn:
                for move in calculate_moves(piece, (i, j), white_turn):
                    legal_moves.add(move)
    if legal_moves == set():
        white_checkmate = True if white_turn and white_in_check else False
        black_checkmate = True if not white_turn and black_in_check else False
        white_stalemate = True if white_turn and not white_in_check else False
        black_stalemate = True if not white_turn and not black_in_check else False
        stalemate = white_stalemate or black_stalemate


def calculate_moves(piece, pos, white, captures_only=False):
    global board
    valid_moves = set()  # Set avoids duplicates
    piece_type = int(str(piece)[-1])

    if piece_type == 1:  # King
        for x in range(-1, 2):
            for y in range(-1, 2):
                if 0 <= pos[0] + x <= 7 and 0 <= pos[1] + y <= 7:
                    valid_moves.add((pos[0] + x, pos[1] + y))
        if not captures_only:  # Castling
            if (white_can_castle[0] and white and not white_in_check) or (black_can_castle[0] and not white and not black_in_check):
                if board[pos[0]][1] == 0 and board[pos[0]][2] == 0 and board[pos[0]][3] == 0:
                    opponent_moves = calculate_all_moves(not white)
                    if not ((pos[0], 1) in opponent_moves or (pos[0], 2) in opponent_moves or (pos[0], 3) in opponent_moves):
                        valid_moves.add((pos[0], 2))
            if (white_can_castle[1] and white and not white_in_check) or (black_can_castle[1] and not white and not black_in_check):
                if board[pos[0]][5] == 0 and board[pos[0]][5] == 0:
                    opponent_moves = calculate_all_moves(not white)
                    if not ((pos[0], 5) in opponent_moves or (pos[0], 6) in opponent_moves):
                        valid_moves.add((pos[0], 6))
            if black_can_castle[0] and not white:
                pass
            if black_can_castle[1] and not white:
                pass

    if piece_type == 2 or piece_type == 3:  # Rook (and Queen)
        for dir in (-1, 1):
            y = dir
            while 0 <= pos[0] + y <= 7:
                valid_moves.add((pos[0] + y, pos[1]))
                if board[pos[0] + y][pos[1]] != 0:
                    break
                y += dir

            x = dir
            while 0 <= pos[1] + x <= 7:
                valid_moves.add((pos[0], pos[1] + x))
                if board[pos[0]][pos[1] + x] != 0:
                    break
                x += dir

    if piece_type == 2 or piece_type == 4:  # Bishop (and Queen)
        for dir in (-1, 1):
            y = dir
            x = dir
            while 0 <= pos[0] + y <= 7 and 0 <= pos[1] + x <= 7:
                valid_moves.add((pos[0] + y, pos[1] + x))
                if board[pos[0] + y][pos[1] + x] != 0:
                    break
                y += dir
                x += dir

            y = dir
            x = -dir
            while 0 <= pos[0] + y <= 7 and 0 <= pos[1] + x <= 7:
                valid_moves.add((pos[0] + y, pos[1] + x))
                if board[pos[0] + y][pos[1] + x] != 0:
                    break
                y += dir
                x -= dir

    if piece_type == 5:  # Knight
        for x_dir in (-1, 1):
            for y_dir in (-1, 1):
                valid_moves.add((pos[0] + x_dir, pos[1] + 2 * y_dir)) if 0 <= pos[0] + x_dir <= 7 and 0 <= pos[1] + 2 * y_dir <= 7 else None
                valid_moves.add((pos[0] + 2 * x_dir, pos[1] + y_dir)) if 0 <= pos[0] + 2 * x_dir <= 7 and 0 <= pos[1] + y_dir <= 7 else None

    if piece_type == 6:  # Pawn
        if white:
            valid_moves.add((pos[0] - 1, pos[1])) if not captures_only and pos[0] - 1 >= 0 and board[pos[0] - 1][pos[1]] == 0 else None

            if not captures_only and pos[0] == 6 and board[pos[0] - 1][pos[1]] == 0 and board[pos[0] - 2][pos[1]] == 0:
                valid_moves.add((pos[0] - 2, pos[1]))

            if pos[0] - 1 >= 0 and 0 <= pos[1] + 1 <= 7:  # Taking
                valid_moves.add((pos[0] - 1, pos[1] + 1)) if captures_only or board[pos[0] - 1][pos[1] + 1] != 0 else None
            if pos[0] - 1 >= 0 and 0 <= pos[1] - 1 <= 7:
                valid_moves.add((pos[0] - 1, pos[1] - 1)) if captures_only or board[pos[0] - 1][pos[1] - 1] != 0 else None
        else:
            valid_moves.add((pos[0] + 1, pos[1])) if not captures_only and pos[0] + 1 <= 7 and board[pos[0] + 1][pos[1]] == 0 else None

            if not captures_only and pos[0] == 1 and board[pos[0] + 1][pos[1]] == 0 and board[pos[0] + 2][pos[1]] == 0:
                valid_moves.add((pos[0] + 2, pos[1]))

            if pos[0] + 1 <= 7 and 0 <= pos[1] + 1 <= 7:  # Taking
                valid_moves.add((pos[0] + 1, pos[1] + 1)) if captures_only or board[pos[0] + 1][pos[1] + 1] != 0 else None
            if pos[0] + 1 <= 7 and 0 <= pos[1] - 1 <= 7:
                valid_moves.add((pos[0] + 1, pos[1] - 1)) if captures_only or board[pos[0] + 1][pos[1] - 1] != 0 else None

    # Remove move option if lands on peice of own colour
    if not captures_only:
        invalid_moves = set()
        for x, y in valid_moves:
            if 0 < board[x][y] < 10 and white or board[x][y] > 10 and not white:
                invalid_moves.add((x, y))
            if (x, y) == (pos[0], pos[1]):
                invalid_moves.add((x, y))

            # If you would (still) be in check after this move, it must be invalid
            temp_board = copy.deepcopy(board)
            board[pos[0]][pos[1]] = 0
            board[x][y] = piece
            white_check, black_check = check_in_check()
            if white_check and white or black_check and not white:
                invalid_moves.add((x, y))
            board = temp_board
        valid_moves -= invalid_moves

    return valid_moves


def calculate_all_moves(white: bool):
    moves = set()
    for i, _ in enumerate(board):
        for j, piece in enumerate(board[i]):
            if 0 < piece < 10 and white or piece > 10 and not white:
                for move in calculate_moves(piece, (i, j), white, True):
                    moves.add(move)
    return moves


def draw_game_over_screen():
    gfxdraw.filled_polygon(screen, ((0, 0), (0, SCREEN_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT), (SCREEN_WIDTH, 0)), (0, 0, 0, 100))
    screen.blit(home_icon, (SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//2 - 50))
    screen.blit(replay_icon, (SCREEN_WIDTH//2 + 150, SCREEN_HEIGHT//2 - 50))


def reset():
    global in_hand, white_turn, white_in_check, black_in_check, white_checkmate, black_checkmate, white_can_castle, black_can_castle, stalemate, game_over, board

    in_hand = [0, (0, 0)]
    white_turn = True
    white_in_check = False
    black_in_check = False
    white_checkmate = False
    black_checkmate = False
    white_can_castle = [True, True]  # Left, Right
    black_can_castle = [True, True]
    stalemate = False
    game_over = False
    board = [[13, 15, 14, 12, 11, 14, 15, 13],
             [16, 16, 16, 16, 16, 16, 16, 16],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [6, 6, 6, 6, 6, 6, 6, 6],
             [3, 5, 4, 2, 1, 4, 5, 3]]


def chess():
    global sound_on, game_over, flipped

    SCREEN_WIDTH, SCREEN_HEIGHT = 1366, 768
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Chess")
    pygame.display.set_icon(pygame.image.load("chess-assets/pieces/Black Pawn.png"))

    running = True
    while running:
        timer.tick(FPS)

        game_over = white_checkmate or black_checkmate or stalemate

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if sound_rect.collidepoint(pygame.mouse.get_pos()):
                    sound_on = not sound_on
                elif pygame.Rect(SCREEN_WIDTH - 200, SCREEN_HEIGHT - 130, 100, 100).collidepoint(pygame.mouse.get_pos()):
                    flipped = not flipped
                elif pygame.mouse.get_pressed()[0]:
                    if not game_over:
                        if not check_promotion(draw=False):
                            pick_up_piece()
                        else:
                            check_promotion(draw=False, mouse_pos=pygame.mouse.get_pos())
                    else:
                        if pygame.Rect(SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//2 - 50, 100, 100).collidepoint(pygame.mouse.get_pos()):
                            running = False  # Clicked the Home button
                        if pygame.Rect(SCREEN_WIDTH//2 + 150, SCREEN_HEIGHT//2 - 50, 100, 100).collidepoint(pygame.mouse.get_pos()):
                            reset()  # Clicked the Reset button
            elif event.type == pygame.MOUSEBUTTONUP and not check_promotion(draw=False):
                put_down_piece() if not game_over else None

        screen.fill((24, 24, 38))
        draw_board()
        draw_valid_moves()
        draw_hand()
        check_promotion()
        check_checkmate()
        draw_side_info()
        if game_over:
            draw_game_over_screen()

        pygame.display.update()

    reset()


if __name__ == "__main__":
    chess()
    pygame.quit()
