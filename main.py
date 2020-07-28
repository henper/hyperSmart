import pygame
from phue import Bridge as PhilipsHueBridge
from svg import Parser, Rasterizer # pynanosvg, depends on Cython

# HyperPixel Weirdly Square
WIDTH = 720
HEIGHT = 720
COLORDEPTH = 18
REFRESHRATE = 60
PPI = '254in'

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


# Connect to Philips Hue Bridge
hue = PhilipsHueBridge()
hue.connect()

# Build the default GUI
homeScreen = pygame.Surface((WIDTH, HEIGHT))
homeScreen.fill((0,0,0,0))

lightSurf = (svg2surface('icons/lightLinealGradient.svg', (HEIGHT, WIDTH)), (0,0))
lightSurfPressed = (svg2surface('icons/lightLinealGradient.svg', (HEIGHT-100, WIDTH-100)), (50,50))

homeScreen.blit(lightSurf[0], lightSurf[1])

# Show default GUI
pygame.display.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT)) # TODO: colordepth for display?
screen.blit(homeScreen, (0,0))
pygame.display.flip()

while True:
    event = pygame.event.wait() # sleep until the user acts

    if event.type == pygame.MOUSEBUTTONDOWN:
        
        screen.fill((0,0,0,0), rect=lightSurf[0].get_rect())
        screen.blit(lightSurfPressed[0], lightSurfPressed[1])
        pygame.display.update()
        continue

    if event.type == pygame.MOUSEBUTTONUP:

        screen.fill((0,0,0,0), rect=lightSurf[0].get_rect())
        screen.blit(lightSurf[0], lightSurf[1])
        pygame.display.update()

        # switch light state
        state = hue.get_light(1)['state']['on']
        state = not state
        hue.set_light(1, 'on', state)

        continue

    if event.type == pygame.QUIT:
        break

pygame.quit()