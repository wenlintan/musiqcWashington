
import pygame
from pygame.locals import *
pygame.init()

width = 512
height = 512
screen = pygame.display.set_mode( (width, height), 0, 24 )
screen.fill( (0,0,0) )

class display:
    def __init__( self, x, y, color ):
        self.x = x
        self.y = y
        self.c = color

import sympy
def attr_draw( z, func, scale, displays ):

    niter = 12  
    recurse = z - func / sympy.diff( func, z )   
    for x in range( -width/2, width/2 ):
        for y in range( -height/2, height/2 ):

            val = y*scale*sympy.I + x*scale
            for i in range( niter ):
                val = recurse.subs( z, val ).evalf()

            outx = sympy.re( val ).evalf()
            outy = sympy.im( val ).evalf()
            del val

            for disp in displays:
                if (outx - disp.x)**2 + (outy - disp.y)**2 < 0.2:
                    out = (x+width/2,height-(y+height/2))
                    print out
                    
                    screen.set_at( out, disp.c )
                    break

        print "Vertical line %d complete" % ( x )
        sympy.core.cache.clear_cache()

        event = pygame.event.poll()
        while event.type != pygame.NOEVENT:
            if event.type == pygame.QUIT:
                return False
            event = pygame.event.poll()
        pygame.display.flip()

pos = [ 1.0, -0.5 + 0.8666*sympy.I, -0.5 - 0.8666*sympy.I ]
d1 = display( sympy.re( pos[0] ), sympy.im( pos[0] ), (255, 0, 0) )
d2 = display( sympy.re( pos[1] ), sympy.im( pos[1] ), (0, 255, 0) )
d3 = display( sympy.re( pos[2] ), sympy.im( pos[2] ), (0, 0, 255) )
displays = [d1, d2, d3]

z = sympy.Symbol( "z" )
func = ( z - pos[0] ) * ( z - pos[1] ) * ( z - pos[2] )
scale = 1.5 / (width/2.0)

attr_draw( z, func, scale, displays )
            

running = True
while running:
    
    event = pygame.event.poll()
    while event.type != pygame.NOEVENT:

        if event.type == pygame.QUIT:
            running = False

        event = pygame.event.poll()

    pygame.display.flip()
