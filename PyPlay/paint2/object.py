import copy
from vector import *

class base:
    def __init__( self, vertices ):
        self.verts = vertices
        self.shape = copy.copy( vertices )
        
        self.restitution = 1.0
        self.elasticity = 1.0

    def collide( self, o ):
        for v in self.verts:
            
            if o.contains( v ):
                self.resolve( o, v )

    def step( self, others ):
        pass

    def unstep( self ):
        pass

    def resolve( self, other, vert ):
        pass

    def contains( self, vert ):
        
        def step( x ):
            if x < 0.0:     return -1.0
            if x > 0.0:     return 1.0
            return 0.0
        
        last_neg = 0
        for i in range( -1, len( self.verts )-1 ):
            seg = self.verts[i] - self.verts[ i+1 ]
            
            n = seg.crossp()
            d = -n.dotp( self.verts[i] )

            p = n.dotp( vert ) + d
            neg = step( p )
            if abs( last_neg - neg ):
                return False

            last_neg = neg

        return True
            
            
            

        
