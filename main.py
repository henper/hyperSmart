
#external dependencies
import pygame
from phue import Bridge as PhilipsHueBridge
from svg import Parser, Rasterizer # pynanosvg, depends on Cython

#internal dependencies
from grid import Grid

# HyperPixel Weirdly Square
WIDTH = 720
HEIGHT = 720
COLORDEPTH = 18
REFRESHRATE = 60
PPI = '254in'

def offset(tup, offset):
    return tuple(map(lambda x: x + int(offset), tup))

# Connect to Philips Hue Bridge
hue = PhilipsHueBridge()
hue.connect()

# Build the default GUI
homeScreen = pygame.Surface((WIDTH, HEIGHT))
homeScreen.fill((0,0,0,0))

#(grid, size) = createGrid(3)
grid = Grid(3,3, WIDTH, HEIGHT)

grid.elem[0][0].setGraphics('icons/lightLinealGradient.svg')
grid.elem[1][1].setGraphics('icons/lightLinealGradient.svg')
grid.elem[2][2].setGraphics('icons/gearLinealGradient.svg')

homeScreen.blit(grid.elem[0][0].surf, grid.elem[0][0].rect.topleft)
homeScreen.blit(grid.elem[1][1].surf, grid.elem[1][1].rect.topleft)
homeScreen.blit(grid.elem[2][2].surf, grid.elem[2][2].rect.topleft)

# Show default GUI
pygame.display.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT)) # TODO: colordepth for display?
screen.blit(homeScreen, (0,0))
pygame.display.flip()


elem = None # keep track of activated element
while True:
    event = pygame.event.wait() # sleep until the user acts

    if event.type == pygame.MOUSEBUTTONDOWN:

        # determine which element was activated
        elem = grid.getElement(event.pos)

        try:
            # update graphics to pressed state
            screen.fill((0,0,0,0), rect=elem.rect)
            screen.blit(elem.surfPressed, elem.rect.topleft)
            pygame.display.update()

        except AttributeError:
            pass # user pressed an empty cell

        continue

    if event.type == pygame.MOUSEBUTTONUP:

        try:

            # restore graphics
            screen.fill((0,0,0,0), rect=elem.rect)
            screen.blit(elem.surf, elem.rect.topleft)
            pygame.display.update()

            # perform action
            state = hue.get_light(1)['state']['on']
            state = not state
            hue.set_light(1, 'on', state)

        except AttributeError:
            pass # user pressed an empty cell

        continue

    if event.type == pygame.QUIT:
        break

pygame.quit()