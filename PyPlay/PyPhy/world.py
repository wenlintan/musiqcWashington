
from vector import *
import obj, draw, material
import renderer
import event_handler

class world:
    
    def __init__( self, rend, event ):
        self.rend = rend
        self.event = event

        self.rend.ortho()
        self.rend.origin()

        self.updates = []

        yellow = material.mat().color( vector3( 1, 1, 0 ) )
        orange = material.mat().color( vector3( 1, 0.6, 0 ) )

        verts = [ vector2( 100, 320 ), vector2( 90,  310 ),
                  vector2( 100, 300 ), vector2( 110, 310 ) ]
        

        o = obj.base( verts )
        o.set_velocity( vector2( 4.0, 0, 0 ) )
        o.create_draw( False )
        o.draw.state.material = yellow

        self.updates.append( o )
        self.rend.add_draw( o.draw )

        verts = [ v + vector2( 30, 5 ) for v in verts ]
        o = obj.base( verts )
        o.set_velocity( vector2( 0.0, 0, 0 ) )
        o.create_draw( False )
        o.draw.state.material = orange

        self.updates.append( o )
        self.rend.add_draw( o.draw )

    def update( self ):

        for update in obj.base.update:
            [ update( u, self.updates ) for u in self.updates ]
            
        self.rend.render()
