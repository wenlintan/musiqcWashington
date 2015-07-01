
import numpy
from random import shuffle, random
from itertools import product
from ctypes import *

from renderer import *
from draws import Block, Tile
from shaders import src, update_src
from OpenGL.GL import *
from time import sleep

from noise import Perlin, Brownian

class Chunk:
    chunk_size = 32
    def __init__( self, position, sampler ):
        self.data = ( c_float * (4 * 32**3) )()
        x, y, z = self.position = position
        for i, j, k in product( range(32), repeat=3 ):
            if sampler( x + i, y + j, z + k ) > 0.0 and abs(z+k-6.) < 0.1:
                self.data[ (k*32*32 + j*32 + i)*4+3 ] = 0.
            else:
                self.data[ (k*32*32 + j*32 + i)*4+3 ] = 4.
        
        self.material = Material(
                self.data,
                (32, 32, 32), 
                precision = GL_RGBA32F, 
                format = GL_RGBA, 
                type = GL_FLOAT,
                filter = GL_NEAREST			
            )

    def apply( self, program ):
        program.variables.chunk_position = self.position
        self.material.apply( 0 )
        program.variables.blocks = 0

class World:
    def __init__( self, renderer ):        
        self.block = [Block(0., 0., 0.)]
        self.batch = Batch( self.block )
        self.batch_draw = Batch.DrawData.instanced(32**3)

        self.program = Program.create( src, "out_color" )
        self.program.set_matrices_from_gl( "modelview", "projection" )
        self.program.variables.block_size = 1.0
        self.program.variables.chunk_size = 32
        #self.program.variables.block_tex_size = 32. / 256.
		
        self.random = self._create_random()
        self.random.apply( 2 )
        self.program.variables.random = 2

        self.program.variables.v = Program.Vertex
        self.program.variables.n = Program.Normal
        #self.program.variables.t = Program.TexCoord0

        self._create_world( renderer )

    def _create_random( self ):
        random = ( c_ubyte * 512**2 )()
        for i in range( 3 ):
            l = list( range(256) )
            shuffle( l )
            for j in range(512):
                random[ i*256 + j ] = l[ j % 256]
        
        return Material( random,
                (512, 512), 
                precision = GL_RGBA8UI, 
                format = GL_RED_INTEGER, 
                type = GL_UNSIGNED_BYTE,
                filter = GL_NEAREST
            )

    def _create_random_world( self, renderer ):
        self.noise = Brownian( (2., 1., 0.25), (0.0501, 0.11, 0.53) )
        self.noise = Brownian( (2.,), (0.0501,) )
        self.chunks = [
                Chunk( (i*32.+0.1, j*32.-0.1, k*32.), self.noise.noise )
                for i, j, k in product(range(2), repeat=3)
            ]

    def _create_world( self, renderer ):
        def r( min, max ):
            return int(random() * (max-min) + min)
        pts = [ (r(1, 30), r(1, 30)) for i in range( 10 ) ]
        def sampler( x, y, z ):
            #if abs(x-16.) < 0.1 and abs(y-1.) < 0.1 and abs(z-6.) < 0.1:
            #    return 1.
            if any([abs(x-px)<0.1 and abs(y-py)<0.1 for px, py in pts]) and abs(z-6.) < 0.1:
                return 1.
            return -1.
        def sampler2( x, y, z ):
            return 1.

        s = [sampler, sampler2]
        self.update_chunks = [		
                [ Chunk( (0., 0., 0.), s[j] ) for i in range( 2 ) ]
                for j in range( 2 )
            ]
        self.chunks = [self.update_chunks[0][0]]

        self.fbos = [
                FBO( (32, 32), [ c.material for c in chunks ], [6, 6] )
                for chunks in self.update_chunks
            ]
        self.fbos[0], self.fbos[1] = self.fbos[1], self.fbos[0]
        renderer.reset_target()
        self.tile = [Tile(0., 0.)]
        self.tile_batch = Batch( self.tile )

        self.update_program = Program.create(
                update_src, "blocks_out", "velocity_out"
            )
        self.update_program.variables.blocks = 0
        self.update_program.variables.velocity_blocks = 1
        self.update_program.variables.v = Program.Vertex
        self.flag = True

    def update( self, renderer ):
        sleep(0.1)
        renderer.reset_target()
        self.update_program.apply()
        for i, d in enumerate( self.update_chunks[0] ):
            d.material.apply( i )
        self.fbos[0].apply()
		
        renderer.origin()
        self.fbos[0].ortho()
        self.update_program.set_matrices_from_gl( "modelview", "projection" )

        self.fbos[0], self.fbos[1] = self.fbos[1], self.fbos[0]
        self.update_chunks[0], self.update_chunks[1] = (
            self.update_chunks[1], self.update_chunks[0] )
        
        self.tile_batch.draw( shader = self.update_program )
        renderer.reset_target()
        self.chunks = [self.update_chunks[0][0]]
    
    def draw( self, renderer, c ):
        self.update( renderer )
        renderer.reset_target()
        renderer.perspective( 75., 0.01, 1000. )
        c.update( renderer )
        
        self.program.apply()
        
        self.program.set_matrices_from_gl( "modelview", "projection" )
        self.program.variables.camera_position = (c.position[0], c.position[1], c.position[2])
        self.random.apply( 2 )
        
        for c in self.chunks:
            c.apply( self.program )
            self.batch.draw( self.batch_draw, self.program )
        
