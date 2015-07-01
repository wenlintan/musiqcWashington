
from vector import *
from properties import *
from time_provider import time_fn

class State( Propertied ):
    def __init__( self, *args, **kwds ):
        self._weights = {}
        self.callback = self._prop_callback
        super( State, self ).__init__( *args, **kwds )

    def _prop_callback( self, prop ):
        self.weights[ prop ] = 1.0
        return True

    def match( self, obj ):
        val = 0.0
        for p in self.list_props:
            if obj.val( p ):    val += self.weights[ prop ]
            else:               val -= self.weights[ prop ]

       return val

    def __call__( self, obj ):
        for p in self.list_props:
            obj.props

class BaseObject( Propertied ):

    def __init__( self, name ):
        super( Template, self ).__init__()
        self.prop( _name = name ) 

    def __call__( self, *args, **kwds ):
        return Object( self, *args, **kwds )
    
class Object( Propertied ):
    def __init__( self, template, *args, **kwds ):
        super( Object, self ).__init__( *args, **kwds )

    def __call__( self, state ):
        pass
        
