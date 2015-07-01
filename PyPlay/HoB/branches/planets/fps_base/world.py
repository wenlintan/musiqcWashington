
import struct
from random import random

from renderer import Batch
from draws import Block

from simulation import Vector3f, Entity, State, CollGeometry, CollAABB

class BlockWorldState( State ):
	def __init__( self ):
		super( BlockWorldState, self ).__init__()

		self.blocks = []
		self.dirty = False
		self.deser = False
	
	def append( self, block ):
		self.blocks.append( block )
		self.dirty = True

	def random( self, n ):
		self.blocks = []
		self.dirty = True

		for i in range( n ):
			minx, minz = random()*50. - 25., random()*50. - 25.
			c = int( random() * 150. )
			self.blocks.append( (minx, minz, c) )

	def serialize( self ):
		data = struct.pack( "!B", len(self.blocks) )
		data += ''.join( struct.pack( "!ffB", *b ) for b in self.blocks )
		return data 

	def deserialize( self, data ):
		self.dirty = True
		if self.deser:
			self.dirty = False

		self.deser = True
		self.blocks = []

		l, = struct.unpack( "!B", data[0] )
		for i in range( l ):
			self.blocks.append( struct.unpack( "!ffB", data[1+i*9: 10+i*9] ) )
		return data[ 1+l*9: ]

class World( Entity ):
	drawable = collidable = updatable = True
	server_sendable = True
	client_sendable = batchable = False
	def __init__( self ):
		self.bstate = BlockWorldState()
		self.bstate.random( 10 )
		self.batch = None
		self.coll = CollGeometry()

	def update( self, dt ):
		if not self.bstate.dirty:
			return

		self.coll = CollGeometry()
		self.bstate.dirty = False

		self.ground = Block( -50., -100., -50., 100. )
		self.ground.set_color( (100, 0, 0, 0) )
		self.coll.add_geometry( CollAABB(
			Vector3f( -50., -100., -50. ), Vector3f( 50., 0., 50. ) ) )

		self.blocks = [ self.ground ]
		for b in self.bstate.blocks:
			minx, minz, c = b
			b = Block( minx, 0., minz, 5. )
			b.set_color( (0, 100, c, 0) )

			self.coll.add_geometry( CollAABB(
				Vector3f( minx, 0., minz ), Vector3f( minx+5., 5, minz+5. ) ) )
			self.blocks.append( b )

		self.batch = Batch( self.blocks )

	def collision_geometry( self ):
		return self.coll

	def resolve( self, other, coll ):
		return other.resolve( self, coll )

	def state( self ):
		return self.bstate

	def draw( self ):
		if self.batch:
			self.batch.draw()
		


