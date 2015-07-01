
from properties import *
from objects import *
from time_provider import time_fn

class Rule( Propertied ):
    def __init__( self, base_state, new_state, *args, **kwds ):
        super( Rule, self ).__init__( args, kwds )
        self.base, self.goal = base_state, new_state

    def __call__( self, obj ):
        pass

class TimeDecay( Rule ):
    def time_constant( self, const ):
        self.rate = const

    def __call__( self, obj ):
        pass
        
                  
class Perception( Propertied ):
    def __init__( self, *args, **kwds ):
        super( Perception, self ).__init__( args, kwds )
