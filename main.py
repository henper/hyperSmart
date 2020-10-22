
# external dependencies
import pygame, yaml
from phue import Bridge as PhilipsHueBridge
from miio.fan import FanZA3
from requests import post
from threading import Timer
from os import uname
from pigpio import pi

# internal dependencies
from grid import Grid, gridFactory

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


# Helpers
def getCoord(event):
    coord = (0,0)

    # Touch events on Raspbian lite with HyperPixel LCD are inverted
    if event.type in [pygame.FINGERUP, pygame.FINGERDOWN, pygame.FINGERMOTION] :
        coord = int((WIDTH-1) * (1.0 - event.x)), int((HEIGHT-1) * (1.0 - event.y))

    # Support for mouse on host
    elif event.type in [pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION]:
        coord = event.pos

    return coord

host = uname()[4].startswith('x86')
gpio = pi()
brightness = 1.0
def setBrightness(rate):
    global gpio
    global brightness
    if rate != brightness and not host:
        brightness = rate
        if brightness != 0:
            dutycycle = int(255*brightness)
        else:
            dutycycle = 0
        # broadcom pin number 19 is the brightness control for HyperPixel4
        gpio.set_PWM_dutycycle(19, dutycycle)

# Import grids
actionLibrary = {'toggleHueLight': toggleHueLight,
                 'setHueLightBrightness': setHueLightBrightness,
                 'toggleFan': toggleFan,
                 'swingLeft': swingLeft,
                 'swingRight': swingRight,
                 'swingStop': swingStop}
lightGroupsGrid = gridFactory(yaml.load(open('grids/lightGroups.yaml'), Loader=yaml.FullLoader), WIDTH, HEIGHT, actionLibrary)

# Show default GUI
activeGrid = lightGroupsGrid
pygame.display.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
activeGrid.draw(screen)
pygame.display.flip()

pygame.mouse.set_visible(False) #conveniently this does not apply on WSL with VcXsrv window

# Sleep system
isSleeping = False
def sleep():
    global timer
    global isSleeping
    timer.cancel()
    setBrightness(0)
    isSleeping = True

timer = Timer(5.0, sleep)
def keepAlive():
    global timer
    global isSleeping
    timer.cancel()
    timer = Timer(30.0, sleep)
    timer.start()
    setBrightness(0.25)
    wasSleeping = isSleeping
    isSleeping = False
    return wasSleeping

# Game loop
while True:
    event = pygame.event.wait() # sleep until the user acts
    
    wasSleeping = keepAlive()
    if wasSleeping:
        break # don't process the event any further, just wake up

    if event.type in [pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN, pygame.FINGERMOTION] or event.type == pygame.MOUSEMOTION and event.buttons[0] == 1:

        # determine which element was activated
        elem, yrate = activeGrid.getElement(getCoord(event))
        try:
            elem.onTouch(canvas=screen, yrate=yrate)
            pygame.display.update()
        except AttributeError:
            pass # user pressed an empty cell
        continue

    if event.type in [pygame.MOUSEBUTTONUP, pygame.FINGERUP] :

        # determine which element was activated
        elem, yrate = activeGrid.getElement(getCoord(event))
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

timer.cancel()
setBrightness(0.25)
pygame.quit()