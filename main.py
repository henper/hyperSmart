
# external dependencies
import pygame, yaml
from phue import Bridge as PhilipsHueBridge
from miio.fan import FanZA3
from requests import post

# internal dependencies
from grid import Grid, gridFactory

# FIXME: ugly hack for inverted touch-input on rasbian. Revist when on pygame 2.0
from os import uname
raspberry = uname()[4].startswith('arm')

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
def toggleHueLight(element, **kwargs):
    id = kwargs['group_id']
    state = hue.get_group(id)['state']['all_on']
    state = not state
    hue.set_group(id, 'on', state)

    if state:
        element.highlight()
    else:
        element.mute()

def setHueLightBrightness(element, **kwargs):
    id = kwargs['group_id']
    rate = kwargs['yrate']
    brightness = int(rate*255)
    hue.set_group(id, 'bri', brightness)
    pass

def toggleFan(element):
    global fanState
    if fanState == 'on':
        fanState = 'off'
        #fan.off()
    else:
        fanState = 'on'
        #fan.on()

def swingLeft(element):
    post('http://192.168.88.229/multibrackets', data = 'left')
def swingRight(element):
    post('http://192.168.88.229/multibrackets', data = 'right')
def swingStop(element):
    post('http://192.168.88.229/multibrackets', data = 'ok')

# Import grids
actionLibrary = {'toggleHueLight': toggleHueLight,
                 'setHueLightBrightness': setHueLightBrightness,
                 'toggleFan': toggleFan,
                 'swingLeft': swingLeft,
                 'swingRight': swingRight,
                 'swingStop': swingStop}
lightGroupsGrid = gridFactory(yaml.load(open('grids/lightGroups.yaml')), WIDTH, HEIGHT, actionLibrary)

# Show default GUI
activeGrid = lightGroupsGrid
pygame.display.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
activeGrid.draw(screen)
pygame.display.flip()

pygame.mouse.set_visible(False) #conveniently this does not apply on WSL with VcXsrv window

while True:
    event = pygame.event.wait() # sleep until the user acts

    if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEMOTION and event.buttons[0] == 1:

        if raspberry:
            x,y = event.pos
            event.pos = (WIDTH-x, HEIGHT-y)

        # determine which element was activated
        elem, yrate = activeGrid.getElement(event.pos)
        try:
            elem.onTouch(canvas=screen, yrate=yrate)
            pygame.display.update()
        except AttributeError:
            pass # user pressed an empty cell
        continue

    if event.type == pygame.MOUSEBUTTONUP:

        if raspberry:
            x,y = event.pos
            event.pos = (WIDTH-x, HEIGHT-y)

        # determine which element was activated
        elem, yrate = activeGrid.getElement(event.pos)
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