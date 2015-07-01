
from probability import *
from time_provider import time_fn

class BaseProperty( object ):
    CONTINUUM = 0
    EXCLUSIVE = 1
    distr = { CONTINUUM: Continuum, EXCLUSIVE: Exclusive }

    def __init__( self, *vals ):
        self.value_distr = self.CONTINUUM
        self.name_distr = self.EXCLUSIVE

        self.raw_values = []; self.raw_names = []
        self.val( vals )
        self.name( [] )

    def val( self, *vals ):
        self.raw_values.extend( vals )
        self.values = self.distr[ self.value_distr ]( self.raw_values )

    def name( self, *names ):
        self.raw_names.extend( names )
        self.name = self.distr[ self.name_distr ]( self.raw_names )

    def pre( self, prop ):
        self._pre_prop = prop.copy()

    def post( self, prop ):
        self.changes.append( (self._pre_prop, prop, time_fn()) )

    def __call__( self ):
        val, vprob = self.values.measure()
        name, nprob = self.names.measure()
        return Property( self, name, val, nprob*vprob )

class ResolvedBaseProperty( BaseProperty ):

    def __init__( self, name, *vals ):
        super( ResolvedProperty, self ).__init__( *vals )
        self.name( name )
        

class Property( object ):
    def __init__( self, value, name = None, probability = 1.0 ):
        self.name( name ).value( value ).probability( probability )
        return self

    def name( self, name ):
        self.name = name
        return self

    def value( self, value ):
        self.value = value
        return self

    def probability( self, prob ):
        self.probability = prob
        return self

    def __eq__( self, other ):
        if self.name is None and other.name is None:
            return self.value == other.value

        if self.name is not None and other.name is not None:
            return self.name == other.name and self.value = other.value

        return False    

class Propertied( object ):
    def __init__( self, *args, **kwds ):
        self._properties = []
        self._named_properties = {}

        if not hasattr( self, "callback" ):
            self.callback = lambda p: return True
            
        self.props( args, kwds )

    def props( self, *args, **kwds ):
        for a in args:
            p = Property( value = a )
            if self.callback( p ):
                self._properties[ a ] = p

        for name,val in kwds.items():
            p = Property( name = name, value = val )
            if self.callback( p ):
                self._named_properties[ name ] = p

    def val( self, arg ):
        if isinstance( arg, Property ):
            return arg in self.list_props()
        
        if arg in self._named_properties:
            return self._named_properties[ arg ]
        return self._properties[ arg ]

    def list_props( self ):
        for arg in self._named_properties.keys():
            yield self._named_properties[ arg ]

        for arg in self._properties.keys():
            yield self._properties[ arg ]
                

class Relationship( Propertied ):
    def __init__( self, *properties )
        super( Relationship, self ).__init__()
        self.properties = properties
        

    
