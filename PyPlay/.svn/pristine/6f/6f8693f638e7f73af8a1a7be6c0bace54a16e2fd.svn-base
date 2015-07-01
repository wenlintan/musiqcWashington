
from hack import *
class Confusion:
    def __init__( self, ch ):
        t = Trigger_t.from_callable( self.on_move )
        ch.on_move.add_trigger( t, 0 )

    def on_move( self, act ):
        act.direction = Direction( dn( 8 ) - 1 )
        return act

status = []
def hack_init( ch ):
    status.append( Confusion( ch ) )
    print "Something"
    
