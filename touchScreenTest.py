import pygame

from os import uname
raspberry = uname()[4].startswith('arm')

WIDTH = 720
HEIGHT = 720

pygame.display.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
screen.fill((0,0,0))
pygame.display.flip()

pygame.mouse.set_visible(False)

minx = 65535
maxx = 0
miny = 65535
maxy = 0

while True:
    event = pygame.event.wait() # sleep until the user acts

    if event.type == pygame.MOUSEBUTTONDOWN:
        print(f'down   {event.pos}')
    if event.type == pygame.MOUSEMOTION:
        print(f'motion {event.pos}')
    if event.type == pygame.MOUSEBUTTONUP:
        print(f'up     {event.pos}')


    if event.type  == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEMOTION and event.buttons[0] == 1:
        
        if raspberry:
            x,y = event.pos
            event.pos = (WIDTH-x, HEIGHT-y)

        x, y = event.pos
        if x > maxx:
            maxx = x
        if y > maxy:
            maxy = y
        if x < minx:
            minx = x
        if y < miny:
            miny = y
        

        screen.fill((0,0,0))
        pygame.draw.circle(screen, (255,255,255), event.pos, 10)

        pygame.display.flip()

    # Allow for ways to exit the application
    if event.type == pygame.QUIT: # closing the (proverbial) window
        break
    if event.type == pygame.KEYDOWN and event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL:
        break
print(f'Min X = {minx}, Max X = {maxx}')
print(f'Min Y = {miny}, Max Y = {maxy}')