import network, console
import pygame
from pygame.locals import *

pygame.init()
screen = pygame.display.set_mode( (800,600), pygame.DOUBLEBUF, 32 )

c = console.Console(screen, Rect((0,0), (800,500)))
c.add_buffer("BlargH!")
for x in range(100):
    c.add_buffer( str(x) )


i = console.Command(screen, Rect((0,500), (800,100)))

print "starting loop"
run = True
while run:
    screen.fill( (0,0,0) )
    c.draw()
    i.draw()
    pygame.display.flip()

    while True:
        e = pygame.event.poll()
        if e.type == NOEVENT:
            break
        if e.type == QUIT:
            run = False
    
