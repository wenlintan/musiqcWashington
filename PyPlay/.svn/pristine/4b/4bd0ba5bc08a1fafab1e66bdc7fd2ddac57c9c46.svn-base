import pygame
from pygame.locals import *

class state:
    def __init__( self ):
        self.key_handlers = {}
        self.mouse_move = None
        self.mouse_click = None

    def __call__( self, event ):

        try:
            if event.type == KEYDOWN or event.type == KEYUP:
                return self.key_handlers[ event.key ]( event.key, event.type == KEYDOWN )
            elif event.type == MOUSEMOTION:
                return self.mouse_move( event.pos, event.rel, event.buttons )
            elif event.type == MOUSEBUTTONUP or event.type == MOUSEBUTTONDOWN:
                return self.mouse_click( event.pos, event.button, event.type == MOUSEBUTTONUP )
        except AttributeError, KeyError:
            return 0
        return 0

    def do_nothing( self ):
        pass
        

class handler:

    def __init__( self ):
        self.states = []

    def add_state( self, state ):
        self.states.insert( state )

    def rem_state( self ):
        self.states.pop( 0 )

    def process( self ):

        event = pygame.event.poll()
        while event.type != NOEVENT:
            if event.type == QUIT:
                return event
            
            for s in self.states:
                
                if s( event ) :
                    break
                
            event = pygame.event.poll()

            
