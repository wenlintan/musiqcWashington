
from simulation import *
from flags import *

from knowledge import *
from bayes import *

class LogicAIComponent( Component ):
	def __init__( self ):
		super( LogicAIComponent, self ).__init__( ComponentType.LogicAI )
		self.knowledge = Knowledge()

		self.dectree = TemporalModel()

class LogicAISystem( System ):
	def __init__( self, tiles ):
		super( LogicAISystem, self ).__init__()
		self.tiles = tiles

	def update( self, ent ):
		if not ent.has_component( ComponentType.LogicAI ):
			return
		ai = ent.get_component( ComponentType.LogicAI )

		time = self.tiles.time
		tile = ArgumentNode( "Tile", time, 2, None, lambda x, y: tuple(), None )
		action = Node( "Action", time, None, tuple(), None )
		health = Node( "Health", time, None, tuple(), None )

		seen = ArgumentNode( "Seen", time, 1, None, 
			lambda x: tuple(x), (0.0, 1.0) )

		initial = tuple( tile(x, y) 
			for x, y in product( TileSystem.dim, repeat=2 ) ),
		state = tuple( x.advance() for x in initial )
		evidence = 
		ai.dectree = TemporalModel( 
			tuple( tile(x, y) for x, y in product( TileSystem.dim, repeat=2 ) ),



		

class Tile( Component ):
	Dirt = 0
	Crop = 1
	
	def __init__( self ):
		super( Tile, self ).__init__( ComponentType.Tile )

class DirtTile( Tile ):
	def __init__( self ):
		super( DirtTile, self ).__init__()

class TileSystem( System ):
	dim = 200
	def __init__( self ):
		super( TileSystem, self ).__init__()
		self.knowledge = Knowledge()

		tile = self.tile = Predicate( "Tile" )
		action = self.action = Predicate( "Action" )
		position = self.position= Predicate( "Position" )
		health = self.health = Predicate( "Health" )
		
		self.knowledge.tell(

			All( 'x', 'y', 'e', 't' )(
				tile( 'x', 'y', Tile.Plant, Variable('t')+1 ) <=
				tile( 'x', 'y', Tile.Crop, 't' ) &
				action( 'e', Action.Plant, 't' )  &
				position( 'e', 'x', 'y', 't' ) )

			)


		self.time = 0
		for x, y in product( range( dim ), repeat=2 ):
			self.knowledge.tell( self.tile( x, y, Tile.Dirt, 0 ) )

	def update( self, ent ):
		if ent.has_component( ComponentType.Tile ):
			tile = ent.get_component( ComponentType.Tile )
			tile.t = self.knowledge.ask( Exists( 'x' )( 
				self.time( tile.x, tile.y, 'x', self.time ) ) )
		if ent.has_component( ComponentType.LogicAI ):
			ai = ent.get_component( ComponentType.LogicAI )
			px, py = ent.position
			for dx, dy in product( range( -2, 3 ), repeat = 2 ):
				x, y = (px + x) % self.dim, (py + y) % self.dim
				t = self.knowledge.ask( Exists( 'x' )(
					self.tile( x, y, 'x', self.time ) ) )
				ai.knowledge.tell( self.tile( x, y, t, self.time ) )

	def end( self ):
		self.time += 1

class Action( Component ):
	Move = 0

	Plant = 100
	Harvest = 101

	def __init__( self ):
		super( Action, self ).__init__( ComponentType.Action )

class MoveAction( Action ):
	def __init__( self, dest ):
		super( MoveAction, self ).__init__()
		self.dest = dest

	def apply( self, ent ):
		x, y = int( random()*200 )*0.01 - 1, int( random()*200 )*0.01 - 1
		ent.transform().position = [x, y, 0]

class PlantAction( Action ):
	def __init__( self ):
		super( PlantAction, self ).__init__()

class HarvestAction( Action ):
	def __init__( self ):
		super( HarvestAction, self ).__init__()

class ActionSystem( System ):
	def __init__( self ):
		super( ActionSystem, self ).__init__()
		self.entities = []

	def update( self, ent ):
		if not ent.has_component( ComponentType.Action ):
			return
		action = ent.get_component( ComponentType.Action )
		action.apply( ent )

if __name__ == "__main__":
	from event import PyEventSystem
	from random import random

	world = World()
	screen_system = ScreenSystem( 800, 600 )
	world.add_system( screen_system )
	world.add_system( MeshRendererSystem() )
	world.add_system( ActionSystem() )

	event_system = PyEventSystem()
	world.add_system( event_system )

	camera = Entity()
	camera.add_component( Transform( [0., 0., -1.2], [-3.14, 0., 0.] ) )
	camera.add_component( Camera( 70., 800. / 600., 0.001, 10. ) )
	camera.add_component( Component( ComponentType.MouseControlled ) )
	world.add_entity( camera )

	worldmap = Entity()
	worldmap.add_component( AABBMesh( [-1, -1, -1], [2, 2, 2] ) )
	worldmap.add_component( MeshRenderer( 0xFF ) )
	world.add_entity( worldmap )

	ai_ents = []
	for i in range( 5 ):
		e = Entity()
		e.add_component( AABBMesh( [0, 0, -1.01], [0.01, 0.01, 0.01] ) )
		e.add_component( Transform( [0, 0, 0], [0, 0, 0] ) )
		e.add_component( MeshRenderer( 0xFF ) )
		e.add_component( Color( [1, 0, 0] ) )
		e.add_component( MoveAction( None ) )
		world.add_entity( e )

	food_ents = []
	for i in range( 5 ):
		e = Entity()
		x, y = int( random()*200 )*0.01 - 1, int( random()*200 )*0.01 - 1
		e.add_component( AABBMesh( [0, 0, -1.01], [0.01, 0.01, 0.01] ) )
		e.add_component( Transform( [x, y, 0], [0, 0, 0] ) )
		e.add_component( MeshRenderer( 0xFF ) )
		e.add_component( Color( [0, 1, 0] ) )
		world.add_entity( e )

	while event_system.running:
		world.update()

