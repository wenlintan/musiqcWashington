
from OpenGL.GL import *

import pygame
from pygame.locals import *

class mat:

    def __init__( self ):
        self.apply = self.do_nothing
        self.dealloc = self.do_nothing

    def __del__( self ):
        self.dealloc()

    def __lt__( self, o ):

        if self.apply < o.apply:    return True
        if o.apply < self.apply:    return False

        if self.apply == self.apply_texture:
            return self.texture < o.texture

        if self.apply == self.apply_color:
            return self.color < o.color
        return False

    def __eq__( self, o ):
        return NotImplemented

    def texture( self, filename ):

        self.dealloc()
        
        self.filename = filename
        self.img = pygame.image.load( filename )
        data = pygame.image.tostring( self.img, "RGB", 1 )
        

        self.texture = glGenTextures( 1 )
        glBindTexture( GL_TEXTURE_2D, self.texture )
        
        width = self.img.get_width()
        height = self.img.get_height()
        glTexImage2D( GL_TEXTURE_2D, 0, GL_RGB, width,
                      height, 0, GL_RGB, GL_UNSIGNED_BYTE, data )

        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)
	glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)

	self.apply = self.apply_texture
	self.dealloc = self.dealloc_texture

	return self

    def color( self, color ):

        self.dealloc()

        self.color = color
        self.apply = self.apply_color
        self.dealloc = self.do_nothing

        return self

    def apply_texture( self ):

        glEnable( GL_TEXTURE_2D )
        glColor3f( 1.0, 1.0, 1.0 )
        glBindTexture( GL_TEXTURE_2D, self.texture )

    def dealloc_texture( self ):

        glDeleteTextures( self.texture )

    def apply_color( self ):

        glDisable( GL_TEXTURE_2D )
        glColor3f( self.color.x, self.color.y, self.color.z )

    def do_nothing( self ):
        pass
    
