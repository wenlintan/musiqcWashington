import pygame
from pygame.locals import *

import pickle

import faction

class genetic:
    def __init__( self, factions ):
        self.factions = factions

    def save( self ):
        f = file( ".\info.txt", "w" )
        pickle.dump( self.factions, f )
        f.close()

    def load( self ):
        f = file( ".\info.txt", "r" )
        self.factions = pickle.load( f )
        f.close()
