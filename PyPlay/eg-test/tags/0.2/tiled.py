
class Entity:
    pass

class Order:
    def act( self, state, entity ):
        pass

class MoveOrder( Order ):
    flow_map = {}
    def _update_flow_map( self, state ):
        pass

class Tile:
    pass

class State:
    def __init__( self ):
        self.tiles = []
        self.entities = []

    def _initial_state( self ):
        pass
