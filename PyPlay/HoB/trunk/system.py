
import struct
from collections import defaultdict

from renderer import Batch
from weapons import Character, TestWeapon, TestProjectile
from event_handler import Player
from world import World
from simulation import NewEntityData, Entity, State, Client, Server

class ClientEntitySystem:
	def __init__( self ):
		self.entities = []

		self.client = Client( 0.1, self.new_entity )
		self.client.connect( "localhost", "1324", "1325", self.on_connection )
		self.client.run()

	def on_connection( self, player_id ):
		print "Connected", player_id
		return self.connection

	def new_entity( self, data ):
		l, = struct.unpack( "!H", data[:2] )
		cls = data[2: 2+l]
		print "new_ent", cls

		if cls == "BlockWorldState":
			w = World()
			self.append( w )
			state = w.state()
		elif cls == "CharacterState":
			c = Character( (0., .1, 0.), (0., 0., 0.) )
			w = TestWeapon( TestProjectile )
			c.equip( w )
			state = c.state()
		else:
			print "Unknown entity type"
			raise ValueError( "Unknown entity type" )

		if state:
			data = state.deserialize( data[2+l:] )
		return NewEntityData( data, state )

	def append( self, ent ):
		self.entities.append( ent )
		
	def draw( self ):
		for i in filter( lambda x: x.drawable, self.entities ):
			i.draw()

		batchable = list( filter( lambda x: x.batchable, self.entities ) )
		batches = defaultdict( list )
		for b in batchable:
			batches[ b.__class__ ].append( b )

		for b in batches.values():
			Batch( b, False ).draw()

	def update( self, dt ):
		self.input_entity = \
			filter( lambda x: x.client_sendable, self.entities )[0]
		self.client.input( self.input_entity.state() )

		for i in filter( lambda x: x.updatable, self.entities ):
			i.update( dt )

		colls = list( filter( lambda x: x.collidable, self.entities ) )
		for i, e in enumerate( colls[:] ):
			for o in colls[:][i+1:]: 
				self.collide( e, o )
					
	def collide( self, e1, e2 ):
		cg1 = e1.collision_geometry()
		cg2 = e2.collision_geometry()
		coll = cg1.collide( cg2 )
		if coll.collided:
			e1.resolve( e2, coll )

class ServerEntitySystem:
	def __init__( self, world ):
		self.entities = [ world ]
		world.state().entity_id = 10000

		self.clients = []
		self.conn_no = 0

		self.server = Server( 0.1, self.new_connection, self.new_entity )
		self.server.run()

	def new_connection( self, client ):
		print "Newconn"
		self.clients.append( client )

		pos, angles = (0., 1., 0.), (0., 0., 0.)
		new_char = Character( pos, angles )
		new_player = Player( new_char, None )
		new_weapon = TestWeapon( TestProjectile )
		new_char.equip( new_weapon )

		client.network_id = 2*self.conn_no
		new_char.state().entity_id = 2*self.conn_no
		new_player.state().entity_id = 2*self.conn_no + 1
		self.conn_no += 1

		print "Newconn!"
		return new_player.state()

	def new_entity( self, ent ):
		l = struct.pack( "!H", len( ent.__class__.__name__ ) )
		type_id = ent.__class__.__name__
		print "new ent", type_id
		return l + type_id + ent.serialize()

	def append( self, ent ):
		self.entities.append( ent )
		
	def draw( self ):
		for i in filter( lambda x: x.drawable, self.entities ):
			i.draw()

		batchable = list( filter( lambda x: x.batchable, self.entities ) )
		batches = defaultdict( list )
		for b in batchable:
			batches[ b.__class__ ].append( b )

		for b in batches.values():
			Batch( b, False ).draw()

	def update( self, dt ):
		self.output_entities = \
			filter( lambda x: x.server_sendable, self.entities )
		for e in self.output_entities:
			self.server.update( e.state() )

		for i in filter( lambda x: x.updatable, self.entities ):
			i.update( dt )

		colls = list( filter( lambda x: x.collidable, self.entities ) )
		for i, e in enumerate( colls[:] ):
			for o in colls[:][i+1:]: 
				self.collide( e, o )
					
	def collide( self, e1, e2 ):
		cg1 = e1.collision_geometry()
		cg2 = e2.collision_geometry()
		coll = cg1.collide( cg2 )
		if coll.collided:
			e1.resolve( e2, coll )

