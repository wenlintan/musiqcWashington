import pygame
from pygame.locals import *

from vector3 import *

colors = [ vector3( r, g, b )
           for r in range(0, 256, 64)
           for g in range(0, 256, 64)
           for b in range(0, 256, 64) ]

image = pygame.image.load( "run.bmp" )

size = image.get_size()
screen = pygame.display.set_mode( size )
screen.blit( image, (0,0) )

for x in range( size[0] ):
    for y in range( size[1] ):

        pixel = raw_to_vec3( screen.get_at( (x,y) ) )
        
        closest = None
        distsqd = 1000000000000.0

        for c in colors:
            ds = ( pixel - c ).mag_squared()

            if ds < distsqd:
                distsqd = ds
                closest = c

        screen.set_at( (x,y), closest.raw )
        

    pygame.display.flip()
    event = pygame.event.poll()
    while event.type != pygame.NOEVENT:
        if event.type == pygame.QUIT:
            i_dont_exist +=4
        
        event = pygame.event.poll()
        

event = pygame.event.poll()
while True:
    if event.type == pygame.QUIT:
        break
    event = pygame.event.poll()
