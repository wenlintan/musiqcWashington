import pygame
from pygame.locals import *

import sys

import base

class maximum:
    pass
class minimum:
    pass

class decision(base.base):
    maximum = maximum
    minimum = minimum
    def __init__( self, lst, attr, value, weight = 1.0 ):
        self.lst = lst
        self.attr = attr
        self.value = value
        self.weight = weight

        self.obj_type = lst[0]

        super(decision, self).__init__()

    def __add__( self, other ):
        "Addition overloaded to return a composite decision."
        return composite_decision( self, other )

    def __mul__( self, weight ):
        "Multiplication overloaded to set decision's weight."
        self.weight = weight

    def __call__( self ):
        "Calling overloaded to call decide."
        return self.decide()

    def decide( self ):
        "Returns the best choice from the list given."
        factors = self.get_factors()

        #factors are the distance from attribute to ideal value
        #therefore best choice has the lowest factor
        minfactor = min( factors )

        index = factors.index( minfactor )
        return lst[index]
        

    def get_factors( self ):
        """Returns a list of factors [0, self.weight] with smaller being
           closer to ideal value."""

        #handle minimaztion and maximization cases
        value = self.value
        if isinstance( self.value, self.maximum ):
            value = sys.maxint
        elif isinstance( self.value, self.minimum ):
            value = -sys.maxint

        #factors is the absolute value of the difference
        factors = [ abs(x.attr[ self.attr ] - value) for x in self.lst ]

        #renormalize factors to be in range [0, weight]
        maxfactor = max( factors )
        factors = [ (float(x)/maxfactor) * self.weight for x in factors ]


class composite_decision( decision ):
    def __init__( self, d1, d2, weight = 1.0 ):
        self.first = d1
        self.second = d2
        self.weight = weight

        super(composite_decision, self).__init__([], '', 0, weight)

    def decide( self ):
        firsts = self.first.get_factors()
        seconds = self.second.get_factors()

        #really, they should be the same length ...
        length = min( len(firsts), len(seconds) )
        factors = [ firsts[i] + seconds[i] for i in range( length ) ]

        minfactor = min( factors )
        index = factors.index( minfactor )
        return firsts[index]
        
