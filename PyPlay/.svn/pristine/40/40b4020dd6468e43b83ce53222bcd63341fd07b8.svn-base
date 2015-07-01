#!/usr/bin/env python

import pdb
from ctypes import *

from renderer import *
from draws import Block
from world import World
from planet import Planet

src = """
#version 330
uniform float block_size;
uniform int chunk_size;

uniform mat4 modelview, projection;
uniform vec3 chunk_position;

uniform float block_tex_size;
uniform isampler3D blocks;

in vec3 v, n;
in vec2 t;

out vec2 tex_coord;
out vec3 normal;

void main() {
    ivec3 block_offset = ivec3(
            gl_InstanceID % chunk_size,
            (gl_InstanceID / chunk_size) % chunk_size,
            gl_InstanceID / chunk_size / chunk_size
        );

    vec3 vertex = vec3(block_offset) * block_size + v + chunk_position;
    gl_Position = projection * modelview * vec4( vertex, 1.0 );
    
    normal = n;

    int block = texelFetch( blocks, block_offset, 0 ).r;
    tex_coord = vec2( t.x, 1. - (t.y + block_tex_size * block) );
}

--Vertex/Fragment--
#version 330
uniform sampler2D tex;

in vec2 tex_coord;
in vec3 normal;

out vec4 out_color;

void main() {
    out_color = texture( tex, tex_coord ) + vec4(normal, 1.) / 1000.;
}
"""

#pdb.set_trace()
r = Renderer( 800, 600 )
r.perspective( 75., 0.01, 1000. )

print "Renderer ready."
empty_data = ( c_uint * 32**3 )()
for i in range( 32**3 ):
    empty_data[ i ] = 1<<24

#blocks = Material( empty_data, (32, 32, 32), 
#            precision = GL_RGBA8I, 
#            format = GL_RGBA_INTEGER, 
#            type = GL_UNSIGNED_INT_8_8_8_8,
#            filter = GL_NEAREST			
#        )

print "Blocks loaded."
tiles = Material.load( "tiles.png" )
print "Materials loaded."

block = [Block(0., 0., 0.)]
batch = Batch( block )
batch_draw = Batch.DrawData.instanced(32**3)

#program = Program.create( src, "out_color" )
#program.set_matrices_from_gl( "modelview", "projection" )
#program.variables.block_size = 1.0
#program.variables.chunk_size = 32
#program.variables.chunk_position = 0., 0., -40.
#program.variables.block_tex_size = 32. / 256.

#blocks.apply( 0 )
#program.variables.blocks = 0
#tiles.apply( 1 )
#program.variables.tex = 1

#program.variables.v = Program.Vertex
#program.variables.n = Program.Normal
#program.variables.t = Program.TexCoord0
#program.apply()

pos = numpy.array((0., 0., -20.))
look = numpy.array((0., 0., 1.))
up = numpy.array((0., 1., 0.))
c = Camera( pos, look, up )

#w = World( r )
w = Planet( r )

handle_key = {}
handle_event = {}
handle_event[ KEYDOWN ] = lambda ev: handle_key[ ev.key ]( ev.key, True )
handle_event[ KEYUP ] = lambda ev: handle_key[ ev.key ]( ev.key, False )
handle_event[ MOUSEMOTION ] = lambda ev: c.rotate( -ev.rel[1]*0.01, -ev.rel[0]*0.01 )

handle_key[K_w] = lambda k, d: c.set_translation( z = (0.05 if d else 0.) )
handle_key[K_s] = lambda k, d: c.set_translation( z = (-0.05 if d else 0.) )
handle_key[K_a] = lambda k, d: c.set_translation( x = (-0.05 if d else 0.) )
handle_key[K_d] = lambda k, d: c.set_translation( x = (0.05 if d else 0.) )
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
    #program.set_matrices_from_gl( "modelview", "projection" )
    #batch.draw( batch_draw, program )
    w.draw( r, c )
    r.end_frame()


