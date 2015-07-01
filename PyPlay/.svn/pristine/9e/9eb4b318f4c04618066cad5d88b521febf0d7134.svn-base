
from OpenGL.GL import *
from pygame.locals import *

from vector3 import *
import constants, event_handler, action

class draw_window:
    def __init__( self ):
        self.state = event_handler.state()
        self.state.mouse_click = self.mouse_click
        self.state.mouse_move = self.mouse_move
        
        self.state.key_handlers[ K_c ] = self.create_color_window

        self.down = False
        self.down_pos = vector3()

        self.code = action.LINE
        self.color = vector3()
        self.pending_actions = []

        self.color_window = None

    def draw( self ):
        
        if self.color_window is not None:
            self.color_window.draw()

    def push( self, handler ):
        self.handler = handler
        handler.add_state( self.state )

    def pop( self, handler ):
        handler.rem_state()

    def create_color_window( self, key, down ):
        if (self.color_window is None) and down:
            self.color_window = color_window( self.color )
            self.color_window.push( self.handler )

            glReadBuffer( GL_BACK )
            self.window = glReadPixelsub( 0, 0, constants.width,
                                          constants.height, GL_RGB )

        elif down:
            glDisable( GL_DEPTH_TEST )
            glRasterPos2i( 0, constants.height )
            glDrawPixelsub( GL_RGB, self.window )
            glEnable( GL_DEPTH_TEST )
            
            self.color = self.color_window.color
            self.color_window.pop( self.handler )
            self.color_window = None
            
        return True

    def mouse_click( self, pos, button, down ):
        if down:
            self.down = True
            self.down_pos = pos
        else:
            self.down = False
            self.build_action( self.down_pos, pos )
        return True

    def mouse_move( self, pos, rel, buttons ):
        if self.down:
            self.build_action( self.down_pos, pos )
            self.down_pos = pos
        return True

    def build_action( self, down, up ):
        s = vector3( down[0], down[1] )
        e = vector3( up[0], up[1] )
        
        act = action.action.create( self.code, self.color )
        act.set_positions( s, e )

        self.pending_actions.append( act )

class color_window:
    def __init__( self, cur_color ):
        self.state = event_handler.state()
        self.state.mouse_move = self.mouse_move
        self.state.mouse_click = self.mouse_click

        self.color = cur_color
        self.r = cur_color.x
        self.g = cur_color.y
        self.b = cur_color.z

    def draw_quad( self, ul, lr, l_color, r_color ):

        glColor3f( l_color.x, l_color.y, l_color.z )
        glVertex3f( ul.x, lr.y, 0.5 )

        glColor3f( r_color.x, r_color.y, r_color.z )
        glVertex3f( lr.x, lr.y, 0.5 )

        glColor3f( r_color.x, r_color.y, r_color.z )
        glVertex3f( lr.x, ul.y, 0.5 )

        glColor3f( l_color.x, l_color.y, l_color.z )
        glVertex3f( ul.x, ul.y, 0.5 )

    def draw( self ):

        glBegin( GL_QUADS )
        self.draw_quad( vector3(249, 149), vector3(551, 451),
                        vector3(0.2, 0.2, 0.2), vector3(0.1, 0.1, 0.1) )
        self.draw_quad( vector3(250, 150), vector3(550, 450),
                        vector3(), vector3() )
        self.draw_quad( vector3(349, 174), vector3(451, 276),
                        vector3(0.2, 0.2, 0.2), vector3(0.1, 0.1, 0.1) )
        self.draw_quad( vector3(350, 175), vector3(450, 275),
                        self.color, self.color )
        self.draw_quad( vector3(275, 305), vector3(525, 345),
                        vector3(0.0, self.g, self.b), vector3(1.0, self.g, self.b) )
        self.draw_quad( vector3(275, 355), vector3(525, 395),
                        vector3(self.r, 0.0, self.b), vector3(self.r, 1.0, self.b) )
        self.draw_quad( vector3(275, 405), vector3(525, 445),
                        vector3(self.r, self.g, 0.0), vector3(self.r, self.g, 1.0) )
        glEnd()

    def push( self, handler ):
        self.handler = handler
        handler.add_state( self.state )

    def pop( self, handler ):
        handler.rem_state()

    def mouse_click( self, pos, button, down ):
        self.handle_mouse_position( pos )
        return True

    def mouse_move( self, pos, rel, down ):
        if down[0]:    self.handle_mouse_position( pos )
        return True

    def handle_mouse_position( self, pos ):
        x = pos[0]; y = pos[1]
        if y >= 305 and y <= 345 and x >= 275 and x <= 525:
            self.r = float(x-275) / 250
            self.color = vector3( self.r, self.g, self.b )

        if y >= 355 and y <= 395 and x >= 275 and x <= 525:
            self.g = float(x-275) / 250
            self.color = vector3( self.r, self.g, self.b )

        if y >= 405 and y <= 445 and x >= 275 and x <= 525:
            self.b = float(x-275) / 250
            self.color = vector3( self.r, self.g, self.b )
        
        
        
        
    
        
        
        
