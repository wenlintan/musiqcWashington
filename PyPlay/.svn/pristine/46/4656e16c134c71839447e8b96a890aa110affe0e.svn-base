
import struct
from OpenGL.GL import *

from vector3 import *
import constants

names = {}
SYNC = 0; names[ SYNC ] = "Sync"
LINE = 1; names[ LINE ] = "Line"
NAME = 2; names[ NAME ] = "Name"

class action:
    header_format = '!iifff'
    header_length = struct.calcsize( header_format )

    actions = {}    
    default_values = {}
    default_values["raw_data"] = [0.0]
    default_values["name"] = "nobody"
    default_values["start_x"] = 0.0
    default_values["start_y"] = 0.0
    default_values["end_x"] = 0.0
    default_values["end_y"] = 0.0
    default_values["line_width"] = 2.0
    
    def pack( self ):
        length = action.header_length

        data = self._internal_pack()
        length += len( data )

        header = struct.pack( action.header_format, length, self.code,
                              self.color.x, self.color.y, self.color.z )
        
        return header+data

    @staticmethod
    def unpack( data ):

        l = len( data )
        s = struct.calcsize( '!i' )
        if s > l:
            return None, data
        
        length, = struct.unpack( '!i', data[:s] )
        if length > l:
            return None, data


        header_data = data[:action.header_length]
        l,code,r,g,b = struct.unpack( action.header_format, header_data )
        try:
            act = action.actions[ code ]( code, vector3(r,g,b) )
        except KeyError, e:
            print "Unknown action code, error: ", e

        act.load_defaults()
        act_data = data[action.header_length:length]
        act._internal_unpack( act_data )
        

        return act, data[length:]

    @staticmethod
    def create( code, color ):
        try:
            act = action.actions[ code ]( code, color )
        except KeyError, e:
            print "Unknown action code, error: ", e

        act.load_defaults()
        return act

    def load_defaults( self ):
        
        for val in self.__class__.values:
            if not hasattr( self, val ):
                setattr( self, val, action.default_values[ val ] )

    def set_positions( self, start, end ):
        self.start_x, self.start_y = start.x, start.y
        self.end_x, self.end_y = end.x, end.y
        

class action_sync( action ):

    values = [ "raw_data" ]
    def __init__( self, code, color ):

        if code != SYNC:
            raise AttributeError( "code must be SYNC" )

        self.code = code
        self.color = color

        self.fmt = "B" * constants.width * constants.height * 3
        self.fmt = "!%s" % self.fmt
            
    def _internal_pack( self ):
        glReadBuffer( GL_BACK )
        d = glReadPixelsub( 0, 0, constants.width, constants.height, GL_RGB )

        self.raw_data = []
        for i in range( constants.height ):
            for j in range( constants.width ):
                self.raw_data.extend( d[j][i] )
                
        return struct.pack( self.fmt, *self.raw_data )

    def _internal_unpack( self, data ):
        self.raw_data = struct.unpack( self.fmt, data )

    def apply( self ):
        
        glDisable( GL_DEPTH_TEST )
        glRasterPos2i( 0, constants.height )
        glDrawPixelsub( GL_RGB, self.raw_data )
        glEnable( GL_DEPTH_TEST )
action.actions[SYNC] = action_sync

class action_name( action ):

    values = [ "name" ]
    def __init__( self, code, color ):

        if code != NAME:
            raise AttributeError( "code must be NAME" )

        self.code = code
        self.color = color
        self.fmt = "!h"

    def _internal_pack( self ):
        l = len( self.name ) % 655365
        return struct.pack( self.fmt, l ) + self.name[:l]

    def _internal_unpack( self, data ):
        head_size = struct.calcsize("!h")
        l, = struct.unpack( "!h", data[:head_size] )
        self.name = data[ head_size:l+head_size ]

    def apply( self ):
        print "User %s has connected." % self.name
action.actions[NAME] = action_name
        
        

class action_line( action ):

    values = [ "start_x", "start_y", "end_x", "end_y", "line_width" ]    
    def __init__( self, code, color ):
        
        if code != LINE:
            raise AttributeError( "code must be LINE" )
        
        self.fmt = '!fffff'
        self.code = code
        self.color = color
        

    def _internal_pack( self ):
        
        return struct.pack( self.fmt, self.start_x, self.start_y,
                            self.end_x, self.end_y, self.line_width )

    def _internal_unpack( self, data ):

        self.start_x, self.start_y, self.end_x, self.end_y, self.line_width = \
                      struct.unpack( self.fmt, data )

    def apply( self ):

        glDisable( GL_TEXTURE_2D )
        glLineWidth( self.line_width )
        glColor( self.color.x, self.color.y, self.color.z )

        glBegin( GL_LINES )
        glVertex3f( self.start_x, self.start_y, 0.5 )
        glVertex3f( self.end_x, self.end_y, 0.5 )
        glEnd()
action.actions[LINE] = action_line


        


        
        
    


