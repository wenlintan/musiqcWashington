
from vector import *
import renderer, event_handler, events, action

from OpenGL.GL import *

class world:
    def __init__( self, rend, handler, network ):

        self.rend = rend
        self.handler = handler
        self.net = network
        
        rend.clear_mode = GL_DEPTH_BUFFER_BIT
        rend.ortho()
        rend.origin()

        self.draw = events.draw_window()
        self.draw.push( handler )

    def __del__( self ):
        self.draw.pop( self.handler )

    def update( self ):

        self.rend.begin_frame()
        
        self.net.update()
        self.draw.draw()

        for act in self.draw.pending_actions:
            self.net.send_data( act.pack() )
            act.apply()

        act, self.net.recv = action.action.unpack( self.net.recv )
        while act is not None:
            act.apply()
            act, self.net.recv = action.action.unpack( self.net.recv )
            
        self.draw.pending_actions = []
        self.rend.end_frame()
