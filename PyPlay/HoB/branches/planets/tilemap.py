
import struct 
from flags import *
from simulation import *

class Tilemap( Component ):
	Collidable = 1<<0
	Pedestrian = 1<<1
	Roadway = 1<<2

	def __init__( self, map_width, map_height, tile_width, tile_height ):
		super( Tilemap, self ).__init__( ComponentType.Tilemap )
		self.tiles = [ 
			[0 for i in range(map_width)] 
			for j in range(map_height)
			]

		self.draw_flags = True
		self.flags = [
			[0 for i in range(map_width)]
			for j in range(map_height) 
			]
		self.flags[4][8] = Tilemap.Collidable
		self.flags[4][4] = Tilemap.Pedestrian

		self.map_width, self.map_height = map_width, map_height
		self.tile_width, self.tile_height = tile_width, tile_height
		self.tile_names = { 0: (1,1), 1: (2,2), 2: (3,3) }

	def save( self, filename ):
		def pack_tile( tile ):
			if tile in self.tile_names:
				tile = self.tile_names[ tile ]
			return (tile[0] & 255) | (tile[1] & 255) << 8

		with open( filename, 'wb' ) as f:
			f.write( struct.pack( "!hh", self.map_width, self.map_height ) )
			f.write( struct.pack( "!ff", self.tile_width, self.tile_height ) )
			for x in range( self.map_width ):
				d = [ self.tiles[x][y] for y in range( self.map_height ) ]
				fl = [ self.flags[x][y] for y in range( self.map_height ) ]
				f.write( struct.pack( "!" + "h"*len(d), *map( pack_tile, d ) ) )
				f.write( struct.pack( "!" + "h"*len(d), *fl ) )

	def load( self, filename ):
		def unpack_tile( val ):
			return ( val & 255, (val >> 8) & 255 )

		with open( filename, 'rb' ) as f:
			hsize = struct.calcsize( "!hh" )
			self.map_width, self.map_height = struct.unpack( "!hh",
				f.read( hsize ) )

			hsize = struct.calcsize( "!ff" )
			self.tile_width, self.tile_height = struct.unpack( "!ff",
				f.read( hsize ) )

			self.tiles, self.flags = [], []
			for x in range( self.map_width ):
				size = struct.calcsize( "!" + "h"*self.map_height )
				self.tiles.append( list( map( unpack_tile, struct.unpack( 
					"!" + "h"*self.map_height, f.read( size ) ) ) ) )
				self.flags.append( list( struct.unpack(
					"!" + "h"*self.map_height, f.read( size ) ) ) )

class TilemapSystem( System ):
	def __init__( self ):
		super( TilemapSystem, self ).__init__()

	def set_tile( self, tile, tile_width, tile_height, data, index ):
		x, y = tile
		x, y = x * tile_width, y * tile_height

		data[ index*4 +0 ] = [ x, y ]
		data[ index*4 +1 ] = [ x + tile_width, y ]
		data[ index*4 +2 ] = [ x + tile_width, y + tile_height ]
		data[ index*4 +3 ] = [ x, y + tile_height ]

	def update( self, ent ):
		if not ent.has_component( ComponentType.Tilemap ):
			return
		tmap = ent.get_component( ComponentType.Tilemap )
		mesh = ent.get_component( ComponentType.Mesh )
		program = ent.get_component( ComponentType.Program )

		program.set_variable( "draw_colors", 
			ProgramVariable.int1( int( tmap.draw_flags ) ) )

		tcoords = mesh[ MeshAttributeType.TEX_COORD0 ]
		colors = mesh[ MeshAttributeType.COLOR ]

		for index in range( tmap.map_width * tmap.map_height ):
			xoff, yoff = index % tmap.map_width, int(index / tmap.map_width)
			tile = tmap.tiles[ xoff ][ yoff ]
			if tile in tmap.tile_names:
				tile = tmap.tile_names[ tile ]
			self.set_tile( tile, tmap.tile_width, tmap.tile_height, 
				tcoords, index )

			flags = tmap.flags[ xoff ][ yoff ]
			color = [ 100, 0, 0, 150 ] if flags & Tilemap.Collidable else \
				[ 0, 0, 100, 150 ] if flags & Tilemap.Pedestrian else \
				[ 0, 100, 0, 150 ]

			colors[ index*4 +0 ] = color
			colors[ index*4 +1 ] = color
			colors[ index*4 +2 ] = color
			colors[ index*4 +3 ] = color
