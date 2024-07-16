import pygame
pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1366, 768
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Battleship")
timer = pygame.time.Clock()
FPS = 60

aircraft_carrier = pygame.image.load("battleship-assets/AircraftCarrier.png").convert_alpha()
battleship = pygame.image.load("battleship-assets/BattleShip.png").convert_alpha()
cruiser = pygame.image.load("battleship-assets/Cruiser.png").convert_alpha()
patrol_boat = pygame.image.load("battleship-assets/PatrolBoat.png").convert_alpha()
submarine = pygame.image.load("battleship-assets/Submarine.png").convert_alpha()
gridlines = pygame.image.load("battleship-assets/gridlines.png").convert_alpha()

aircraft_carrier = pygame.transform.scale2x(aircraft_carrier)
battleship = pygame.transform.scale2x(battleship)
cruiser = pygame.transform.scale2x(cruiser)
patrol_boat = pygame.transform.scale2x(patrol_boat)
submarine = pygame.transform.scale2x(submarine)

running = True
while running:
    timer.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((8, 89, 209))
    screen.blit(gridlines, (64, 64))
    screen.blit(aircraft_carrier, (64, 64 * 1))
    screen.blit(battleship, (64, 64 * 2))
    screen.blit(cruiser, (64, 64 * 3))
    screen.blit(patrol_boat, (64, 64 * 4))
    screen.blit(submarine, (64, 64 * 5))


    pygame.display.update()

pygame.quit()
