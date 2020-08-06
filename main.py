
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

def createGrid(divisor):
    if WIDTH % divisor != 0:
        raise ValueError(f'{WIDTH} is divisable by almost everything but not by {divisor}, try again!')

    elementSize = int(WIDTH / divisor)
    grid = []

    # generate x,y positions for all elements in the grid
    for rowIndex in range(divisor):
        row = []
        for colIndex in range(divisor):
            row.append((colIndex * elementSize, rowIndex * elementSize))
        grid.append(row.copy())
        row.clear()

    return (grid, (elementSize, elementSize))

def offset(tup, offset):
    return tuple(map(lambda x: x + int(offset), tup))

# Helper for importing icons
rasterizer = Rasterizer()
def svg2surface(svgFile, size):

    # use pynanosvg to convert svg file to bytes
    global rasterizer
    svg = Parser.parse_file(svgFile)#, PPI) ..I do not understand DPI

    # figure out the scaling, making sure not to draw outside the lines
    scale = min(size[0] / svg.width, size[1] / svg.height)
    
    buf = rasterizer.rasterize(svg, size[0], size[1], scale)

    return pygame.image.frombuffer(buf, size, 'RGBA')

def importIcon(icon, size):
    pressed = size[0] * 0.1 # reduce icon when pressed
    surf = svg2surface(icon, size)
    surfPressed = svg2surface(icon, offset(size, -pressed))
    return (surf, surfPressed)


# Connect to Philips Hue Bridge
hue = PhilipsHueBridge()
hue.connect()

# Build the default GUI
homeScreen = pygame.Surface((WIDTH, HEIGHT))
homeScreen.fill((0,0,0,0))

#(grid, size) = createGrid(3)
grid = Grid(3,3, WIDTH, HEIGHT)


grid.elem[0][0].setSurfaces(importIcon('icons/lightLinealGradient.svg', grid.elem[0][0].rect.size))
grid.elem[0][1].setSurfaces(importIcon('icons/lightLinealGradient.svg', grid.elem[0][1].rect.size))
grid.elem[0][2].setSurfaces(importIcon('icons/gearLinealGradient.svg', grid.elem[0][2].rect.size))

homeScreen.blit(grid.elem[0][0].surf, grid.elem[0][0].rect.topleft)
homeScreen.blit(grid.elem[0][1].surf, grid.elem[0][1].rect.topleft)
homeScreen.blit(grid.elem[0][2].surf, grid.elem[0][2].rect.topleft)

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