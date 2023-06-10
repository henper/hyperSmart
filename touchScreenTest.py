import pygame

from os import uname
raspberry = uname()[4].startswith('arm')

from gesture import *

WIDTH = 720
HEIGHT = 720

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
screen.fill((0,0,0))
pygame.display.flip()

pygame.mouse.set_visible(False)

minx = WIDTH
maxx = 0
miny = HEIGHT
maxy = 0

gestureDetection = GestureDetection()
pygame.event.set_blocked(None)
pygame.event.set_allowed(gestureDetection.get_supported_events())
pygame.event.clear()

while True:
    event = pygame.event.wait() # sleep until the user acts

    if pygame.event.get_blocked(event.type):
        print(event.type)
        continue
    
    gesture = gestureDetection.update(event)

    if gesture == Gesture.NONE:
        continue

    elif gesture == Gesture.QUIT:
        break

    x, y = gestureDetection.position
    if x > maxx:
        maxx = x
    if y > maxy:
        maxy = y
    if x < minx:
        minx = x
    if y < miny:
        miny = y

    elif gesture == Gesture.DOWN:
        print(f'down   {gestureDetection.position}')
        pygame.draw.circle(screen, (255,255,255), gestureDetection.position, 10)

    elif gesture == Gesture.UP or gesture == Gesture.SWUP:
        print(f'up     {gestureDetection.position}')
        screen.fill((0,0,0))

    elif gesture == Gesture.SWIPE :
        pygame.draw.circle(screen, (0,0,255), gestureDetection.position, 10)
    
    pygame.display.flip()


print(f'Min X = {minx}, Max X = {maxx}')
print(f'Min Y = {miny}, Max Y = {maxy}')