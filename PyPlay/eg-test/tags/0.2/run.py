
import pdb
from renderer import *
from draws import Tile

import numpy
import numpy.linalg
from math import sin, cos, sqrt

src = """
#version 330
uniform mat4 modelview, projection;

in vec3 vertex;
in vec4 color;

out vec4 frag_color;

void main() {
    gl_Position = projection * modelview * vec4( vertex, 1.0 );
	frag_color = color; 
}

--Vertex/Fragment--
#version 330

in vec4 frag_color;
out vec4 out_color;

void main() {
    out_color = frag_color;
}
"""

r = Renderer( 800, 600 )
r.perspective( 75., 0.01, 1000. )

tiles = [ Tile( x, y ) for x in range( 80 ) for y in range( 60 ) ]
batch = Batch( tiles )

#pdb.set_trace()
program = Program.create( src, "out_color" )
program.variables.vertex = Program.Vertex
program.variables.color = Program.Color
program.apply()

pos = numpy.array((0., 10., -100.))
look = numpy.array((0., 0., 1.))
up = numpy.array((0., 1., 0.))
c = Camera( pos, look, up )

handle_key = {}
handle_event = {}
handle_event[ KEYDOWN ] = lambda ev: handle_key[ ev.key ]( ev.key, True )
handle_event[ KEYUP ] = lambda ev: handle_key[ ev.key ]( ev.key, False )
handle_event[ MOUSEMOTION ] = lambda ev: c.rotate( -ev.rel[1]*0.01, -ev.rel[0]*0.01 )

handle_key[K_w] = lambda key, down: c.set_translation( z = (0.5 if down else 0.) )
handle_key[K_s] = lambda key, down: c.set_translation( z = (-0.5 if down else 0.) )
handle_key[K_a] = lambda key, down: c.set_translation( x = (-0.5 if down else 0.) )
handle_key[K_d] = lambda key, down: c.set_translation( x = (0.5 if down else 0.) )
handle_key[K_p] = lambda key, down: pdb.set_trace()

handle_key[K_UP] =    lambda key, down: c.set_rotation( x = (0.01 if down else 0.) )
handle_key[K_DOWN] =  lambda key, down: c.set_rotation( x = (-0.01 if down else 0.) )
handle_key[K_RIGHT] = lambda key, down: c.set_rotation( y = (0.01 if down else 0.) )
handle_key[K_LEFT] =  lambda key, down: c.set_rotation( y = (-0.01 if down else 0.) )

event = pygame.event.poll()
while event.type != QUIT:

    event = pygame.event.poll()
    while event.type not in ( NOEVENT, QUIT ):
        if event.type in handle_event:
            handle_event[ event.type ]( event )
        event = pygame.event.poll()

    r.begin_frame()
    c.update( r )
    program.set_matrices_from_gl( "modelview", "projection" )
    batch.draw( shader = program )
    r.end_frame()


