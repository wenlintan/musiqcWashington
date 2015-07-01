
from math import *
from random import *

from collections import defaultdict
from zope.interface import Interface, implements

class Distribution( Interface ):
    def value( self, val ):
        "Add value to the possible states."

    def weight( self, val ):
        "Get weight associated with value."

    def suggest( self, val, weight ):
        "Make given value more likely by factor weight."

    def collapse( self, val ):
        """Collapse probabilities to a certain value (and surrounding values
        in a continuum)."""

    def measure( self ):
        """Returns single value or range of probable values.  Each value is a
        tuple containing the actual value and its corresponding probability."""

class DistrBase( object ):
    def __init__( self, *vals ):
        self.values = vals
        self.weights = defaultdict( float )

    def value( self, val ):
        self.values.append( val )
        
    def _normalize( self ):
        "Renormalize so sum of all probabilities is 1.0"
        current_weight = sum( [self.weights[v] for v in self.values] )
        
        scale = 1. / current_weight
        self.weights = dict( [(v,self.weights[v]*scale) for v in self.values] )
    
class Exclusive( DistrBase ):
    implements( Distribution )
    def __init__( self, *vals ):
        super( Exclusive, self ).__init__( *vals )

class Continuum( DistrBase ):
    implements( Distribution )
    def __init__( self, *vals ):
        super( Continuum, self ).__init__( *vals )
        self.connections = defaultdict( set )
        
    def connect( self, *vals ):
        assert len( vals ) >= 2
        pairs = [ (vals[i], vals[i+1]) for i in range( len(vals)-1 ) ]
        for base, end in pairs:
            self.connections[ base ].add( end )
            self.connections[ end ].add( base )

    def measure( self ):
        weights = [ (self.weights[v],v) for v in self.values ]
        weights.sort()
        weights.reverse()
        
        return weights[ 0 ][ 1 ]        

    def suggest( self, val, weight ):
        "Add weight to val and in an exponential falloff around val."
        assert val in self.values
        assert 0.0 <= weight and weight <= 1.0

        self._apply_weight( val, 1, weight, set() )
        self._normalize()

    def collapse( self, val ):
        self.weights = defaultdict( float )
        self.suggest( val, 1.0 )

    def _apply_weight( self, val, depth, weight, visited ):
        if val in visited or depth > 3:
            return
        
        visited.add( val )
        self.weights[ val ] += weight
                            
        falloff = 1. / (3.*len( self.values ))
        for conn in self.connections[ val ]:
            self._apply_weight( conn, depth+1, weight*falloff, visited )


    
        
        

    
