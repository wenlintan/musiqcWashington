
from math import log
from random import random

from renderer import *
from vector import *

class Tiles:
    UNKNOWN = -1
    GRASS = 0
    BERRIES = 1

    colors = { UNKNOWN: (0, 0, 0, 255),
               GRASS: (0, 255, 0, 255),
               BERRIES: (255, 0, 0, 255) }

class World:
    width, height = 20, 20
    def __init__( self ):
        self.blocks = [ Tiles.UNKNOWN
                        for x in range( self.width )
                        for y in range( self.height ) ]
        
        self.tiles = [ Tile( x, y, Tiles.colors[ self.blocks[x*self.width+y] ] )
                       for x in range( self.width )
                       for y in range( self.height ) ]
        
        self.batch = Batch( self.tiles )
        self.dirty = False

    def set_block( self, pos, t ):
        i = pos.y*self.width + pos.x
        self.blocks[i] = t
        self.tiles[i].color = Tiles.colors[ t ]
        self.dirty = True

    @staticmethod
    def generate_random():
        w = World()
        spawn = [ 0.95, 1.0 ]
        for x in range( w.width ):
            for y in range( w.height ):
                t, r = 0, random()
                while r > spawn[t]:
                    t += 1

                w.set_block( Point2(x,y), t )
        return w

    def render( self, renderer ):
        if self.dirty:
            self.dirty = False
            self.batch.rebuild()
            
        renderer.begin_frame()
        self.batch.draw()
        renderer.end_frame()

class Planner:
    def plan( self, agent ):
        return []

class Action:
    WORKING = 0
    IMPOSSIBLE = 1
    COMPLETE = 2

class Move( Action ):
    def __init__( self, start, end ):
        self.start, self.end = start, end
        diff = self.end - self.start

        sign = lambda x: x / abs(x)
        self.path = [ (sign(diff.x), 0) for i in range(abs(diff.x)) ]
        self.path.append( (0, sign(diff.y)) for i in range(abs(diff.y)) )

    def apply_state( self, state ):
        state.knowledge

    def tick( self, state ):
        state.position += Vector2( *self.path.pop(0) )
        if not self.path:
            return Action.COMPLETE
        return Action.WORKING

class MoveTo( Action ):
    def __init__( self, start, entity ):
        self.goal = entity
        self.move = Move( start, entity.state.position )

    def apply_state( self, state ):
        state.knowledge 

    def tick( self, state ):
        if self.move.tick( state ) == Action.COMPLETE:
            if state.position == self.entity.state.position:
                self.move = Move( state, entity.state.position )
                return Action.WORKING
            return Action.COMPLETE
        return Action.WORKING

class Trade( Action ):
    def __init__( self, item, quantity, trader ):
        self.item, self.quantity = item, quantity
        self.trader = trader

    def tick( self, entity ):
        if entity.position != trader.position:
            return Action.IMPOSSIBLE

        if entity.inventory[item] < quantity:
            return Action.IMPOSSIBLE

        if not trader.trade( entity, item, quantity, goal, goal_quantity ):
            return Action.IMPOSSIBLE

        return Action.COMPLETE
            
class AgentState:
    def __init__( self ):
        self.position = Vector2()
        self.inventory = {}
        self.skills = {}

    def utility( self, entity ):
        weights = entity.weights
        scores = (weights[j] * log(self.inventory[j]) for j in self.inventory)
        return sum( scores )
        
class Agent:
    def __init__( self ):
        self.state = AgentState()
        
        self.plan = []
        self.planner = Planner()

    def tick( self ):
        if not self.plan:
            self.plan = self.planner.plan( self )
            
        action = self.plan[0]
        

handle_key = {}
handle_event = {}
handle_event[ KEYDOWN ] = lambda ev: handle_key[ ev.key ]( ev.key, True )
handle_event[ KEYUP ] = lambda ev: handle_key[ ev.key ]( ev.key, False )

r = Renderer(640, 640)
w = World.generate_random()

event = pygame.event.poll()
while event.type != QUIT:

    event = pygame.event.poll()
    while event.type not in ( NOEVENT, QUIT ):
        if event.type in handle_event:
            handle_event[ event.type ]( event )
        event = pygame.event.poll()

    w.render( r )

