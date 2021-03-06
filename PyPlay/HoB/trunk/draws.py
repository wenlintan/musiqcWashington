
from itertools import chain
from renderer import Batch

class Tile:
	width, height = 32, 32
	offsets = ( (0,0), (width, 0), (0, height), (width, height) )
	index_data = ( 0, 1, 2, 1, 3, 2 )
	
	batch_data = {
			Batch.Vertex: Batch.F3,
			#Batch.Color: Batch.UB4,
			Batch.Index: Batch.US1
		}
	
	def __init__( self, x, y, color = None ):
		self.x, self.y = x * 32, y * 32
		self.color = color
		
		if color is None:
			cmap = lambda v: min( int(v * .255), 255 )
			self.color = cmap(self.x), cmap(self.y), 0, 255
		
		self.dirty = False

	def set_offsets( self, vertex_off, index_off ):
		self.vertex_offset, self.index_offset = vertex_off, index_off

	nvertices = 4
	def vertices( self ):
		return ((self.x + x, self.y + y, 0.) for x, y in self.offsets)

	def colors( self ):
		return (self.color for _ in range(self.nvertices))

	nindices = 6
	def indices( self ):
		return (i + self.vertex_offset for i in self.index_data)

class Block:
	size, tex_size = 1., 31. / 256.
	
	batch_data = {
			Batch.Vertex: Batch.F3,
			Batch.Normal: Batch.F3
			#Batch.TexCoord0: Batch.F2
		}
	
	def __init__( self, x, y, z, size = 0, tex_size = 0 ):
		self.x, self.y, self.z = x, y, z

		if not size:
			size = Block.size
		if not tex_size:
			tex_size = Block.tex_size
		
		self.offsets = (
				(0,0,0), (size,size,0), (size,0,0), 
				(0,0,0), (0,size,0), (size,size,0),

				(size,0,0), (size,size,size), (size,0,size),   
				(size,0,0), (size,size,0), (size,size,size),  

				(size,0,size), (0,size,size), (0,0,size), 
				(size,0,size), (size,size,size), (0,size,size),

				(0,0,size), (0,size,0), (0,0,0), 
				(0,0,size), (0,size,size), (0,size,0), 

				(0,size,0), (size,size,size), (size,size,0), 
				(0,size,0), (0,size,size), (size,size,size),

				(0,0,size), (size,0,0), (size,0,size),
				(0,0,size), (0,0,0), (size,0,0)
			)

		self._normals = (
				(0.,0.,-1.), (0.,0.,-1.), (0.,0.,-1.),
				(0.,0.,-1.), (0.,0.,-1.), (0.,0.,-1.),

				(1.,0.,0.), (1.,0.,0.), (1.,0.,0.),
				(1.,0.,0.), (1.,0.,0.), (1.,0.,0.),

				(0.,0.,1.), (0.,0.,1.), (0.,0.,1.),
				(0.,0.,1.), (0.,0.,1.), (0.,0.,1.),

				(-1.,0.,0.), (-1.,0.,0.), (-1.,0.,0.),
				(-1.,0.,0.), (-1.,0.,0.), (-1.,0.,0.),

				(0.,1.,0.), (0.,1.,0.), (0.,1.,0.),
				(0.,1.,0.), (0.,1.,0.), (0.,1.,0.),

				(0.,-1.,0.), (0.,-1.,0.), (0.,-1.,0.),
				(0.,-1.,0.), (0.,-1.,0.), (0.,-1.,0.)
			)
		
		self._tcoords = (
				(0., 0.), (tex_size, tex_size), (tex_size, 0.), 
				(0., 0.), (0., tex_size), (tex_size, tex_size), 
				
				(0., 0.), (tex_size, tex_size), (0., tex_size), 
				(0., 0.), (tex_size, 0.), (tex_size, tex_size), 
				
				(tex_size, 0.), (0., tex_size), (0., 0.), 
				(tex_size, 0.), (tex_size, tex_size), (0., tex_size), 
				
				(0., tex_size), (tex_size, 0.), (0., 0.), 
				(0., tex_size), (tex_size, tex_size), (tex_size, 0.), 
				
				(0., 0.), (tex_size, tex_size), (tex_size, 0.), 
				(0., 0.), (0., tex_size), (tex_size, tex_size), 
				
				(0., tex_size), (tex_size, 0.), (tex_size, tex_size), 
				(0., tex_size), (0., 0.), (tex_size, 0.)
			)
		
	def set_offsets( self, vertex_off, index_off ):
		self.vertex_offset, self.index_offset = vertex_off, index_off

	def set_color( self, color ):
		self.color = color
		if Batch.Color not in self.batch_data:
			self.batch_data[ Batch.Color ] = Batch.UB4

	nvertices = 36
	nindices = 0
	def vertices( self ):
		return ( (self.x+x, self.y+y, self.z+z) for x,y,z in self.offsets )

	def normals( self ):
		return iter(self._normals)

	def colors( self ):
		return ( self.color for i in range(36) )

	def texcoord0( self ):
		return iter(self._tcoords)

