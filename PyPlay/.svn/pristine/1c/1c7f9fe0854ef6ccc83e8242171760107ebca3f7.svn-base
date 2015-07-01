
import numpy
from random import shuffle, random
from math import floor
from itertools import product
from ctypes import *

from renderer import *
from draws import Block

class Chunk:
    chunk_size = 32
    def __init__( self, position, sampler ):
        self.data = ( c_uint * 32**3 )()
        x, y, z = self.position = position
        for i, j, k in product( range(32), repeat=3 ):
            if sampler( x + i, y + j, z + k ) < 0.0:
                self.data[ k*32*32 + j*32 + i ] = 250 << 24
        
        self.material = Material(
                self.data,
                (32, 32, 32), 
                precision = GL_RGBA8UI, 
                format = GL_RGBA_INTEGER, 
                type = GL_UNSIGNED_INT_8_8_8_8,
                filter = GL_NEAREST			
            )

    def apply( self, program ):
        program.variables.chunk_position = self.position
        self.material.apply( 0 )
        program.variables.blocks = 0
        
class Perlin:
    def __init__( self ):
        self.random = list( range(256) )
        shuffle( self.random )
        self.random = self.random * 2
    
    def noise( self, x, y, z ):
        X, Y, Z = map( lambda x: int(x) & 255, (x, y, z) )
        x, y, z = x - floor(x), y - floor(y), z - floor(z)

        u, v, w = map( self.fade, (x, y, z) )
        A, B = self.random[X] + Y, self.random[X+1] + Y
        AA, AB = self.random[A] + Z, self.random[A+1] + Z
        BA, BB = self.random[B] + Z, self.random[B+1] + Z

        return self.lerp( w,
            self.lerp( v, self.lerp( u, self.grad( AA,   x,   y,   z ),
                                        self.grad( BA,   x-1, y,   z ) ),
                          self.lerp( u, self.grad( AB,   x,   y-1, z ),
                                        self.grad( BB,   x-1, y-1, z ) ) ),
            self.lerp( v, self.lerp( u, self.grad( AA+1, x,   y,   z-1 ),
                                        self.grad( BA+1, x-1, y,   z-1 ) ),
                          self.lerp( u, self.grad( AB+1, x,   y-1, z-1 ),
                                        self.grad( BB+1, x-1, y-1, z-1 ) ) ) )

    @staticmethod
    def fade( t ):
        return t * t * t * (t * (t * 6 - 15) + 10)

    @staticmethod
    def lerp( t, a, b ):
        return a + t * (b - a)

    def grad( self, h, x, y, z ):
        h = self.random[h] & 15
        u = x if h<8 else y
        v = y if h<4 else (x if h==12 or h==14 else z)
        return (u if h&1 else -u) + (v if h&2 else -v)

class Brownian:
    def __init__( self, amplitudes, frequencies ):
        self.ampls, self.freqs = amplitudes, frequencies
        self.perlins = [Perlin() for a in amplitudes]

    def noise( self, x, y, z ):
        i = zip( self.ampls, self.freqs, self.perlins )
        return sum( a*p.noise( x*f, y*f, z*f ) for a, f, p in i )

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
out vec4 test;
out vec3 vertex;

void main() {
    ivec3 block_offset = ivec3(
            gl_InstanceID % chunk_size,
            (gl_InstanceID / chunk_size) % chunk_size,
            (gl_InstanceID / chunk_size / chunk_size)
        );

    int block = texelFetch( blocks, block_offset, 0 ).r;
    vertex = vec3(block_offset) * block_size + v + chunk_position;
    vertex = vertex * float(block != 250);
    gl_Position = projection * modelview * vec4( vertex, 1.0 );
    
    normal = n;
    tex_coord = vec2( t.x, 1. - (t.y + block_tex_size * block) );
}

--Vertex/Fragment--
#version 330
uniform isampler2D random;
uniform vec3 gradients[ 16 ] = {
    vec3( 1., 1., 0. ), vec3( -1., 1., 0. ), vec3( 1., -1., 0. ), vec3( -1., -1., 0. ),
    vec3( 1., 0., 1. ), vec3( -1., 0., 1. ), vec3( 1., 0., -1. ), vec3( -1., 0., -1. ),
	vec3( 0., 1., 1. ), vec3( 0., -1., 1. ), vec3( 0., 1., -1. ), vec3( 0., -1., -1. ),
	vec3( 1., 1., 0. ), vec3( 0., -1., 1. ), vec3( -1., 1., 0. ), vec3( 0., -1., -1. )
};

uniform vec3 camera_position;

in vec3 vertex;
in vec2 tex_coord;
in vec3 normal;
in vec4 test;

out vec4 out_color;
float fade ( float t ) {
    return t * t * t * (t * (t * 6 - 15) + 10);
}

vec3 grad( int h, int y ) {
    return gradients[ texelFetch( random, ivec2( h, y ), 0 ).r & 15 ];
}

float noise2( int y, vec2 point ) {
    int X = int(floor( point.x )) & 255, Y = int(floor( point.y )) & 255;
    vec2 pt = vec2( point.x - floor( point.x ), point.y - floor( point.y ) );

    int A = texelFetch( random, ivec2( X, y ), 0 ).r + Y;
	int B = texelFetch( random, ivec2( X + 1, y ), 0 ).r + Y;

    return mix( 
        mix( 
            dot( grad( A, y ).xy, pt ), 
            dot( grad( B, y ).xy, pt + vec2( -1., 0. ) ), 
            fade(pt.x) ),
        mix( 
            dot( grad( A + 1, y ).xy, pt + vec2( 0., -1. ) ), 
            dot( grad( B + 1, y ).xy, pt + vec2( -1., -1. ) ), 
            fade(pt.x) ),
        fade(pt.y) );
}

float noise3( int y, vec3 point ) {
    int X = int(floor( point.x )) & 255, 
	    Y = int(floor( point.y )) & 255,
        Z = int(floor( point.z )) & 255;
		
    vec3 pt = vec3( 
        point.x - floor( point.x ), 
        point.y - floor( point.y ),
        point.z - floor( point.z ) );

    int A = texelFetch( random, ivec2( X, y ), 0 ).r + Y;
    int B = texelFetch( random, ivec2( X + 1, y ), 0 ).r + Y;
    
    int AA = texelFetch( random, ivec2( A , y ), 0 ).r + Z;
    int AB = texelFetch( random, ivec2( A + 1, y ), 0 ).r + Z;
    int BA = texelFetch( random, ivec2( B, y ), 0 ).r + Z;
    int BB = texelFetch( random, ivec2( B + 1, y ), 0 ).r + Z;

    return mix(
        mix( 
            mix( 
                dot( grad( AA, y ), pt ), 
                dot( grad( BA, y ), pt + vec3( -1., 0., 0. ) ), 
                fade(pt.x) ),
            mix( 
                dot( grad( AB, y ), pt + vec3( 0., -1., 0. ) ), 
                dot( grad( BB, y ), pt + vec3( -1., -1., 0. ) ), 
                fade(pt.x) ),
            fade(pt.y) ),
		mix( 
            mix( 
                dot( grad( AA + 1, y ), pt + vec3( 0., 0., -1. )), 
                dot( grad( BA + 1, y ), pt + vec3( -1., 0., -1. ) ), 
                fade(pt.x) ),
            mix( 
                dot( grad( AB + 1, y ), pt + vec3( 0., -1., -1. ) ), 
                dot( grad( BB + 1, y ), pt + vec3( -1., -1., -1. ) ), 
                fade(pt.x) ),
            fade(pt.y) ),
        fade(pt.z) );
}

void main() {
    vec3 light = camera_position - vertex;
    
	float noise = clamp( noise3( 1, vertex * 0.05 ) + 
	    0.4 * noise3( 1, vertex * 0.5 ) +  0.15 * noise3( 1, vertex * 2.04 ) + .2, 0., 1. );
	
	vec4 color = mix( vec4( 0.2, 0.7, 0.1, 1. ),  vec4( 0.4, 0.25, 0.125, 1. ), noise );
    out_color = clamp( dot(normalize(light), normal) * 8. / length( light ), 0.2, 1. ) * color;
}
"""

class World:
    def __init__( self ):
        self.noise = Brownian( (2., 1., 0.25), (0.0501, 0.11, 0.53) )
        self.noise = Brownian( (2.,), (0.0501,) )
        self.chunks = [
                Chunk( (i*32.+0.1, j*32.-0.1, k*32.), self.noise.noise )
                for i, j, k in product(range(2), repeat=3)
            ]
        
        random = ( c_ubyte * 512**2 )()
        for i in range( 3 ):
            l = list( range(256) )
            shuffle( l )
            for j in range(512):
                random[ i*256 + j ] = l[ j % 256]
        
        self.random = Material( random,
                (512, 512), 
                precision = GL_RGBA8UI, 
                format = GL_RED_INTEGER, 
                type = GL_UNSIGNED_BYTE,
                filter = GL_NEAREST
            )

        self.block = [Block(0., 0., 0.)]
        self.batch = Batch( self.block )
        self.batch_draw = Batch.DrawData.instanced(32**3)

        self.program = Program.create( src, "out_color" )
        self.program.set_matrices_from_gl( "modelview", "projection" )
        self.program.variables.block_size = 1.0
        self.program.variables.chunk_size = 32
        #self.program.variables.block_tex_size = 32. / 256.
		
        self.random.apply( 2 )
        self.program.variables.random = 2

        self.program.variables.v = Program.Vertex
        self.program.variables.n = Program.Normal
        #self.program.variables.t = Program.TexCoord0
        
    def draw( self, cam_pos ):
        self.program.apply()
        
        self.program.set_matrices_from_gl( "modelview", "projection" )
        self.program.variables.camera_position = cam_pos
        self.random.apply( 2 )
        
        for c in self.chunks:
            c.apply( self.program )
            self.batch.draw( self.batch_draw, self.program )
    
