import pygame
from pygame.locals import *

class state:
    def __init__( self ):
        self.key_handlers = {}
        self.mouse_move = None
        self.mouse_click = None

    def __call__( self, event ):

        if (event.type == KEYDOWN or event.type == KEYUP) and self.key_handlers.has_key( event.key ):
            return self.key_handlers[ event.key ]( event.key, event.type == KEYDOWN )
        elif event.type == MOUSEMOTION and self.mouse_move:
            return self.mouse_move( event.pos, event.rel, event.buttons )
        elif (event.type == MOUSEBUTTONUP or event.type == MOUSEBUTTONDOWN) and self.mouse_click:
            return self.mouse_click( event.pos, event.button, event.type == MOUSEBUTTONDOWN )

        return False
        

class handler:

    def __init__( self ):
        self.states = []

    def add_state( self, state ):
        self.states.insert( 0, state )

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

            
