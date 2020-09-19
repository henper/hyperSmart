
# external dependencies
import pygame
from phue import Bridge as PhilipsHueBridge
from miio.fan import FanZA3

# internal dependencies
from grid import Grid

# HyperPixel Weirdly Square
WIDTH = 720
HEIGHT = 720
COLORDEPTH = 18
REFRESHRATE = 60
PPI = '254in'

# Connect to Philips Hue Bridge
hue = PhilipsHueBridge()
hue.connect()

# Connect to Xiomei devices
#fan = FanZA3('192.168.88.232', open('tokens/zhimi-fan-za3_mibtFDE2.ascii', 'r').readline())
#fanStatus = fan.status() # FIXME: this takes a second or two, do in separate process?
# speed, direct_speed, natural_speed, angle, oscillate,
#fanState = fanStatus.power
fanState = 'off'

# Actions
def toggleHueLight(element):
    id = 1
    state = hue.get_light(id)['state']['on']
    state = not state
    hue.set_light(id, 'on', state)

    if state:
        element.highlight()
    else:
        element.mute()


def toggleFan(element):
    global fanState
    if fanState == 'on':
        fanState = 'off'
        #fan.off()
    else:
        fanState = 'on'
        #fan.on()

# Build the default GUI
grid = Grid(3,3, (WIDTH, HEIGHT))

grid.setIcon((0,0), 'icons/wifiLightLinealGradient.svg')
grid.elem[0][0].setReleaseAction(toggleHueLight)

grid.setIcon((1,0), 'icons/coolingFanLinealGradient.svg')
grid.elem[1][0].setReleaseAction(toggleFan)

grid.mergeElements([(0,1), (0,2)])
grid.setSlider((0,1), 0.01)

grid.setGrid((2,0), 2, 2)
inceptionGrid = grid.elem[2][0]
inceptionGrid.setIcon((0,0), 'icons/wifiLightLinealGradient.svg')
inceptionGrid.setIcon((0,1), 'icons/wifiLightLinealGradient.svg')
inceptionGrid.setIcon((1,0), 'icons/wifiLightLinealGradient.svg')
inceptionGrid.setIcon((1,1), 'icons/wifiLightLinealGradient.svg')

grid.mergeElements([(1,2), (2,2)])
grid.setTextBox((1,2),'text')

# Show default GUI
pygame.display.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
grid.draw(screen)
pygame.display.flip()

pygame.mouse.set_visible(False) #conveniently this does not apply on WSL with VcXsrv window

while True:
    event = pygame.event.wait() # sleep until the user acts

    if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEMOTION and event.buttons[0] == 1:
        # determine which element was activated
        elem, yrate = grid.getElement(event.pos)
        try:
            elem.onTouch(canvas=screen, yrate=yrate)
            pygame.display.update()
        except AttributeError:
            pass # user pressed an empty cell
        continue

    if event.type == pygame.MOUSEBUTTONUP:
        # determine which element was activated
        elem, yrate = grid.getElement(event.pos)
        try:            
            elem.onRelease(canvas=screen)
            pygame.display.update()
        except AttributeError:
            pass # user pressed an empty cell
        continue

    # Allow for ways to exit the application
    if event.type == pygame.QUIT: # closing the (proverbial) window
        break
    if event.type == pygame.KEYDOWN and event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL:
        break

pygame.quit()