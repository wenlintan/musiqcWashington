import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

from vector import *
import draw

class renderer:

    def __init__( self, screen_dim ):

        self.dim = screen_dim
        
        self.pos = vector3()
        self.look = vector3( 0., 0., -1. )
        self.up = vector3( 0., 1., 0. )
        
        self.fov = 70.0
        self.nearz = 0.1
        self.farz = 100.

        self.draws = []
        self.draws_sorted = True

        self.render_start = pygame.time.get_ticks()

        d = pygame.display
        self.screen = d.set_mode( ( int(self.dim.x), int(self.dim.y) ),
                                  pygame.OPENGL | pygame.DOUBLEBUF, 24 )
        
        self.default_settings()
        self.perspective()
        self.world()

    def add_draw( self, draw ):
        self.draws.append( draw )
        draw.register( self )

        self.draws_sorted = False

    def rem_draw( self, draw ):
        self.draws.remove( draw )
        self.draws_sorted = False

    def render( self ):
        
        self.begin_frame()

        if not self.draws_sorted:
            self.draws.sort()
            self.draws_sorted = True

        current_state = None
        for d in self.draws:
            if d.state != current_state:
                d.state.apply()
                current_state = d.state

            d.draw( )
        
        self.end_frame()

    def begin_frame( self ):

        rs = pygame.time.get_ticks()
        self.frame_time = rs - self.render_start
        self.render_start = rs
        
        glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

    def end_frame( self ):

        self.render_time = pygame.time.get_ticks() - self.render_start
        pygame.display.flip()

    def default_settings( self ):
        glShadeModel( GL_SMOOTH )
        glClearColor( 0.0, 0.0, 0.0, 0.0 )

        glClearDepth( 1.0 )
	glEnable( GL_DEPTH_TEST )
	glDepthFunc( GL_LEQUAL )

        # glEnable( GL_LINE_SMOOTH )
	glHint( GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST )

	print "Vendor:", glGetString( GL_VENDOR )
	print "Renderer:", glGetString( GL_RENDERER )
	print "Version:", glGetString( GL_VERSION )
	print "Extensions:", glGetString( GL_EXTENSIONS )

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

        
        
