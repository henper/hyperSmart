
# external dependencies
import pygame, yaml
#from phue import Bridge as PhilipsHueBridge
#from miio.fan import FanZA3
from requests import post
from threading import Timer
from os import uname
from pigpio import pi

# internal dependencies
from grid import Grid, gridFactory
from gesture import *

# HyperPixel Weirdly Square
WIDTH = 720
HEIGHT = 720
COLORDEPTH = 18
REFRESHRATE = 60
PPI = '254in'

# Connect to Philips Hue Bridge
#hue = PhilipsHueBridge()
#hue.connect()

# Connect to Xiomei devices
#fan = FanZA3('192.168.88.232', open('tokens/zhimi-fan-za3_mibtFDE2.ascii', 'r').readline())
#fanStatus = fan.status() # FIXME: this takes a second or two, do in separate process?
# speed, direct_speed, natural_speed, angle, oscillate,
#fanState = fanStatus.power
fanState = 'off'

# Actions
'''
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
'''
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
'''
actionLibrary = {'toggleHueLight': toggleHueLight,
                 'setHueLightBrightness': setHueLightBrightness,
                 'toggleFan': toggleFan,
                 'swingLeft': swingLeft,
                 'swingRight': swingRight,
                 'swingStop': swingStop}
lightGroupsGrid = gridFactory(yaml.load(open('grids/lightGroups.yaml'), Loader=yaml.FullLoader), (WIDTH, HEIGHT), actionLibrary)
'''

uno  = gridFactory(yaml.load(open('grids/uno.yaml' ), Loader=yaml.FullLoader), (WIDTH, HEIGHT))
dos  = gridFactory(yaml.load(open('grids/dos.yaml' ), Loader=yaml.FullLoader), (WIDTH, HEIGHT))
tres = gridFactory(yaml.load(open('grids/tres.yaml'), Loader=yaml.FullLoader), (WIDTH, HEIGHT))

grids = [uno, dos, tres]

# Show default GUI
active = 0
pygame.display.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
grids[active].draw(screen)
pygame.display.flip()

# swipe between grids
swipe_surface = pygame.Surface((WIDTH*3, HEIGHT))

def swipe_set(grids, active):
    next = (active + 1) % len(grids)
    prev = (active - 1) % len(grids)

    swipe_surface.fill((0,0,0))
    grids[ prev ].draw(swipe_surface)
    grids[active].draw(swipe_surface, (1*WIDTH, 0))
    grids[ next ].draw(swipe_surface, (2*WIDTH, 0))
    swipe_surface.convert()

swipe_set(grids, active)
area = pygame.Rect(0,0,0,0)
target = 0
current = 0
velocity = 0

'''
showcase = pygame.transform.scale(swipe_surface, (WIDTH, HEIGHT/len(grids)))
screen.fill((0,0,0))
screen.blit(showcase, (0, 0))
pygame.display.flip()
'''

# input and gestures
pygame.mouse.set_visible(False) #conveniently this does not apply on WSL with VcXsrv window, or WSL2
relativeMotion = 0
lastPoint = 0

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

gestureDetection = GestureDetection()
pygame.event.set_allowed(gestureDetection.get_supported_events())
pygame.event.clear()

# Game loop
while True:

    # process animations before accepting more user input
    if current != target :
        if (current > target and current + velocity < target) or (current < target and current + velocity < target) :
            current = target
        else :
            current += velocity
        
        if current == target :
            grids[active].draw(screen)
        else :
            area=pygame.Rect(WIDTH + current, 0, WIDTH, HEIGHT)
            screen.blit(swipe_surface, (0,0), area)
        pygame.display.update()
        pygame.event.pump()
        continue

    event = pygame.event.wait() # sleep until the user acts
    
    wasSleeping = keepAlive()
    if wasSleeping:
        continue # don't process the event any further, just wake up
    
    gesture = gestureDetection.update(event)

    if gesture == Gesture.NONE:
        continue

    elif gesture == Gesture.QUIT:
        break

    elif gesture == Gesture.DOWN:
        # determine which element was activated
        elem, yrate = grids[active].getElement(gestureDetection.position)
        try:
            elem.onTouch(canvas=screen, yrate=yrate)
            pygame.display.update()
        except AttributeError:
            pass # user pressed an empty cell
        continue

    elif gesture == Gesture.UP :
        # determine which element was activated
        elem, yrate = grids[active].getElement(gestureDetection.position)
        try:            
            elem.onRelease(canvas=screen)
            pygame.display.update()
        except AttributeError:
            pass # user pressed an empty cell
        continue

    elif gesture == Gesture.SWIPE :
        area=pygame.Rect(WIDTH + gestureDetection.travel, 0, WIDTH, HEIGHT)
        screen.blit(swipe_surface, (0,0), area)
        pygame.display.update()

    elif gesture == Gesture.SWUP :
        current = gestureDetection.travel
        velocity = gestureDetection.velocity
        
        if gestureDetection.travel <  -WIDTH / 2 :
            # swipe left
            active = (active - 1) % len(grids)
            swipe_set(grids, active)
            target = WIDTH * 0
        elif gestureDetection.travel > WIDTH / 2 :
            # swipe right
            active = (active + 1) % len(grids)
            swipe_set(grids, active)
            target = WIDTH * 2
        else :
            # back to center
            velocity *= -1
            target = WIDTH * 1

        #grids[active].draw(screen)
        #pygame.display.update()



timer.cancel()
setBrightness(0.25)
pygame.quit()
