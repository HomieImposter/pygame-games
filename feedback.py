import pygame
pygame.init()

# After pressing the (currently non-existent) feedback button, open this file and take in the feeback
# Have main func feedback() take parameter of which game it came from
# Save to a txt file, should be fun if it ever gets used

"""Want to report a bug? Suggest a feature? Leave a review? Generally harass me?
Well, this is the place to do it.

Thank you for your feedback.
(if you do not deserve thanks for your feedback, please do not read that)"""

font = pygame.font.SysFont("franklingothic", 50)
font2 = pygame.font.SysFont("franklingothic", 40)
back_arrow = pygame.image.load("misc/Back Arrow.png")
back_arrow = pygame.transform.smoothscale(back_arrow, (75, 75))
submitted = False
entry = ''
game = ''
line_count = 76


def feedback(screen: pygame.Surface, game_name: str):
    global game
    game = game_name

    screen.blit(back_arrow, (32, 32))
    if not submitted:
        title = font.render("Report a bug, suggest a feature, generally harass me:", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(1366//2, 60)))
        pygame.draw.rect(screen, (41, 41, 64), (107, 120, 1366 - 107*2, 768 - 120*2))

        # Draws submit button
        play_rect = pygame.Rect(533, 673, 300, 70)
        if play_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(screen, (6, 92, 19), play_rect)
        else:
            pygame.draw.rect(screen, (8, 135, 27), play_rect)
        play_text = font.render("Submit", True, (255, 255, 255))
        screen.blit(play_text, play_text.get_rect(center=(683, 708)))

        entry_text = entry.split('\n')
        for i, line in enumerate(entry_text):
            screen.blit(font.render(line, True, (255, 255, 255)), (117, 130 + i * 32))
    else:
        thank_text = font.render("Thank you for your feedback!", True, (255, 255, 255))
        screen.blit(thank_text, thank_text.get_rect(center=(683, 768//2 - 20)))

        thank_text = font2.render("(if your feedback does not deserve thanks, please disregard this message)", True, (255, 255, 255))
        screen.blit(thank_text, thank_text.get_rect(center=(683, 768 // 2 + 20)))


def submit():
    global submitted
    submitted = True

    with open("misc/feedback.txt", 'a') as file:
        file.write(f"{game}: {entry}\n")


def enter(char: str):
    global entry

    if char == '\b':
        entry = entry[:-1] if len(entry) > 0 else entry
    else:
        entry += char


def reset():
    global submitted, entry

    submitted = False
    entry = ''
