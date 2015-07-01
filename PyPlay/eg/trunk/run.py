
import pdb
from ctypes import *

from renderer import *
from world import World

#pdb.set_trace()
r = Renderer( 800, 600 )
r.perspective( 75., 0.01, 1000. )

pos = numpy.array((16., 16., -20.))
look = numpy.array((0., 0., 1.))
up = numpy.array((0., 1., 0.))
c = Camera( pos, look, up )

w = World( r )

handle_key = {}
handle_event = {}
handle_event[ KEYDOWN ] = lambda ev: handle_key[ ev.key ]( ev.key, True )
handle_event[ KEYUP ] = lambda ev: handle_key[ ev.key ]( ev.key, False )
handle_event[ MOUSEMOTION ] = lambda ev: \
		c.rotate( -ev.rel[1]*0.01, -ev.rel[0]*0.01 )

handle_key[K_w] = lambda k, d: c.set_translation( z = (0.5 if d else 0.) )
handle_key[K_s] = lambda k, d: c.set_translation( z = (-0.5 if d else 0.) )
handle_key[K_a] = lambda k, d: c.set_translation( x = (-0.5 if d else 0.) )
handle_key[K_d] = lambda k, d: c.set_translation( x = (0.5 if d else 0.) )
handle_key[K_p] = lambda k, d: pdb.set_trace()

handle_key[K_UP] =    lambda k, d: c.set_rotation( x = (0.01 if d else 0.) )
handle_key[K_DOWN] =  lambda k, d: c.set_rotation( x = (-0.01 if d else 0.) )
handle_key[K_RIGHT] = lambda k, d: c.set_rotation( y = (0.01 if d else 0.) )
handle_key[K_LEFT] =  lambda k, d: c.set_rotation( y = (-0.01 if d else 0.) )

event = pygame.event.poll()
while event.type not in ( NOEVENT, QUIT ):
    event = pygame.event.poll()

while event.type != QUIT:
    event = pygame.event.poll()
    while event.type not in ( NOEVENT, QUIT ):
        if event.type in handle_event:
            handle_event[ event.type ]( event )
        event = pygame.event.poll()

    r.begin_frame()
    c.update( r )
    w.draw( r, c )
    r.end_frame()


