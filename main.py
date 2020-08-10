
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

def toggleHueLight(id=1):
    state = hue.get_light(id)['state']['on']
    state = not state
    hue.set_light(id, 'on', state)

# Connect to Philips Hue Bridge
hue = PhilipsHueBridge()
hue.connect()

# Build the default GUI
grid = Grid(3,3, WIDTH, HEIGHT)

grid.elem[0][0].setGraphics('icons/lightLinealGradient.svg')
grid.elem[0][0].setAction(toggleHueLight)

grid.elem[0][1].setGraphics('icons/lightLinealGradient.svg')
grid.elem[2][2].setGraphics('icons/gearLinealGradient.svg')



# Show default GUI
pygame.display.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT)) # TODO: colordepth for display?

for elem in grid.elems:
    elem.draw(screen)

pygame.display.flip()


elem = None # keep track of activated element
while True:
    event = pygame.event.wait() # sleep until the user acts

    if event.type == pygame.MOUSEBUTTONDOWN:

        # determine which element was activated
        elem = grid.getElement(event.pos)

        try:
            elem.draw(screen, pressed=True)
            pygame.display.update()

        except AttributeError:
            pass # user pressed an empty cell

        continue

    if event.type == pygame.MOUSEBUTTONUP:

        try:
            # restore graphics
            elem.draw(screen)
            pygame.display.update()

            # perform action
            elem.callback()

            # state = hue.get_light(1)['state']['on']
            # state = not state
            # hue.set_light(1, 'on', state)

        except AttributeError:
            pass # user pressed an empty cell

        continue

    if event.type == pygame.QUIT:
        break

pygame.quit()