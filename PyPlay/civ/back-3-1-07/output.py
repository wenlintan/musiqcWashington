import pygame
from pygame.locals import *

import base

class output(base.base):
    INFO = 0
    SUCCESS = 1
    WARNING = 2
    ERROR = 3
    
    def __init__(self, screen, font_size):

        #avoid our attribute management system
        self.recurse_attributes = False
        
        self.screen = screen

        #load default font
        self.font = pygame.font.Font( None, font_size )
        self.file = open("log.html", "w")

        #write html header
        self.file.write( """<html><head><title>Python Log</title></head>
                            <body bgcolor="black">""" )

        #create output templates for different log types
        self.info = '<font color="grey">%s</font><br>'
        self.succ = '<font color="blue">%s</font><br>'
        self.warn = '<font color="orange">%s</font><br>'
        self.err = '<font color="red">ERROR: %s</font><br>'

        #use an array for quick access
        self.outputs = [ self.info, self.succ, self.warn, self.err ]

    def write( self, text, x, y, color=(255,100,0), logged = False ):
        "Print to screen using font, optionally logging as well"

        #font render returns a new surface ready to be blitted
        surf = self.font.render( text, True, color )

        drawloc = Rect( (x,y), surf.get_size() )
        self.screen.blit( surf, drawloc )

        if logged:
            self.log( text, self.INFO )

    def log( self, text, typ = INFO ):
        "Logs information to stdout and to our log file"
        print text

        #replace newlines with <br>s for html logging
        text.replace( '\n', "<br>" )
        
        output = self.outputs[typ] % (text)
        self.file.write( output )

    def __del__(self):
        self.file.write( "</body></html>" )
        self.file.close()
