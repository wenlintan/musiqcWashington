import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

from vector import *

class renderer:

    def __init__( self, screen_dim ):

        self.dim = screen_dim
        
        self.pos = vector3()
        self.look = vector3( 0., 0., -1. )
        self.up = vector3( 0., 1., 0. )
        
        self.fov = 70.0
        self.nearz = 0.1
        self.farz = 100.0

        self.render_start = pygame.time.get_ticks()

        d = pygame.display
        self.screen = d.set_mode( ( int(self.dim.x), int(self.dim.y) ),
                                  pygame.OPENGL | pygame.DOUBLEBUF, 24 )
        
        self.default_settings()
        self.perspective()
        self.world()

    def begin_frame( self ):

        rs = pygame.time.get_ticks()
        self.frame_time = rs - self.render_start
        self.render_start = rs
        
        glClear( self.clear_mode )
        self.world()

    def end_frame( self ):

        self.render_time = pygame.time.get_ticks() - self.render_start
        pygame.display.flip()

    def default_settings( self ):
        glShadeModel( GL_SMOOTH )
        glClearColor( 1.0, 1.0, 1.0, 1.0 )

        glClearDepth( 1.0 )
	glEnable( GL_DEPTH_TEST )
	glDepthFunc( GL_LEQUAL )

        glDisable( GL_BLEND )
        glDisable( GL_ALPHA_TEST )
	glHint( GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST )

	self.clear_mode = GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT
	glClear( self.clear_mode )

	glViewport( 0, 0, int(self.dim.x), int(self.dim.y) )

    def world( self ):
        glMatrixMode( GL_MODELVIEW )
        glLoadIdentity()

        gluLookAt( self.pos.x, self.pos.y, self.pos.z,
                   self.look.x, self.look.y, self.look.z,
                   self.up.x, self.up.y, self.up.z )

    def origin( self ):
        glMatrixMode( GL_MODELVIEW )
        glLoadIdentity()

    def perspective( self ):
        "Setup projection matrix using internal parameters."
        glMatrixMode( GL_PROJECTION )
        glLoadIdentity()
        
        gluPerspective( self.fov, float(self.dim.x) / self.dim.y,
                        self.nearz, self.farz )

    def ortho( self ):
        "Setup projection matrix for orthographic projection."
        glMatrixMode( GL_PROJECTION )
        glLoadIdentity()

        glOrtho( 0.0, self.dim.x, self.dim.y, 0.0, -1.0, 1.0 )

        
        
