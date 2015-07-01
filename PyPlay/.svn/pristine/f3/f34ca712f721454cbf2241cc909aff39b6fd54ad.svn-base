
import math
import numpy
from xml.dom.minidom import parse
from collections import defaultdict

from renderer import Batch

class ColladaSource:
	def __init__( self, ident, data, technique_common = None ):
		self.ident = ident
		self.data = data
		self.technique_common = technique_common

class ColladaInput:
	def __init__( self, offset, semantic, source, input_set = 0 ):
		self.offset = offset
		self.semantic = semantic
		self.source = source
		self.input_set = input_set

class ColladaNode:
	def __init__( self, ident, parent = None ):
		self.parent = parent
		self.children = []
		self.instances = []

		self.ident = ident
		self.transform = numpy.array((
			(1., 0., 0., 0.), (0., 1., 0., 0.),
			(0., 0., 1., 0.), (0., 0., 0., 1.) ))

	def add_child( self, node ):
		self.children.append( node )
		node.parent = self

	def add_instance( self, instance ):
		self.instances.append( instance )

	def translate( self, float_array ):
		self.transform[:][3] += numpy.array(float_array)

	def scale( self, scale ):
		mat = numpy.array((
			(scale[0], 0., 0., 0.), (0., scale[1], 0., 0.),
			(0., 0., scale[2], 0.), (0., 0., 0., 1.) ))
		self.transform = numpy.dot( self.transform, mat )

	def matrix( self, mat ):
		mat = numpy.array( mat[i:i+4] for i in range(0, 16, 4) )
		self.transform = numpy.dot( self.transform, mat )

	def rotate( self, float_array ):
		pass

class ColladaGeometry:
	semantic_map = {
			"POSITION": ( Batch.Vertex, Batch.F3 ),
			"NORMAL": ( Batch.Normal, Batch.F3 )
		}

	def __init__( self, inputs, vcount, polydata ):
		"""Initialize a new ColladaGeometry object from data 
		loaded from a collada file.

		Parameters:
			inputs: dictionary mapping source to offset in polydata
			polydata: list of indices into sources as determined
				by inputs
		"""

		self.batch_data = { Batch.Index: Batch.US1 }
		self.batch_data[ Batch.Color ] = Batch.F3

		for semantic in inputs.keys():
			if semantic in self.semantic_map:
				t, d = self.semantic_map[ semantic ]
				self.batch_data[ t ] = d

		self.added_verts = {}
		self.vertex_offset = inputs[ "POSITION" ].offset

		self.data = defaultdict(list)
		self.ind = []

		nvertices, i = 0, 0
		for nv in vcount:
			p = polydata[ i: i+nv*len(inputs) ]
			i += nv*len(inputs)

			index = []
			for j in range( 0, nv*len(inputs), len(inputs) ):
				v = p[j: j+len(inputs)]
				if tuple(v) not in self.added_verts:
					self.added_verts[ tuple(v) ] = nvertices
					nvertices += 1

					for sem, input in inputs.items():
						off = input.offset
						data = input.source.data[ v[off]*3: v[off]*3+3 ]
						self.data[ sem ].append( data )
				index.append( self.added_verts[tuple(v)] )

			if nv > 4:
				raise ValueError( "Ngons not supported.")
			elif nv == 4:
				for j in (0, 1, 2, 0, 2, 3):
					self.ind.append( index[j] )
			elif nv == 3:
				self.ind.extend( index )

		light = numpy.array((1. / math.sqrt(2), 1. / math.sqrt(2), 0.))
		for n in self.data[ "NORMAL" ]:
			dp = numpy.dot( light, n )
			self.data[ "COLOR" ].append( (0.3, 0.7*dp, 0.) )

		self.nvertices = nvertices
		self.nindices = len( self.ind )
		self.voffset = 0

	def load_controller( self, bsm, inputs, vcount, jointdata ):
		vert_map = defaultdict(list)
		for data, v in self.added_verts:
			vert_map[ data[self.vertex_offset] ].append( v )

		self.joints = defaultdict(list)
		nvertices, i = 0, 0
		for nv in vcount:
			data = joint_data[ i: i + nv*len(inputs) ]
			i += nv

			index = inputs[ "JOINT" ].offset
			joint = inputs[ "JOINT" ].source[ data[index] ]
			self.joints[ joint ].extend( vert_map[ nvertices ] )
			nvertices += 1

		self.bind_shape_mat = bsm

		ident = lambda : numpy.array(
			(1., 0., 0., 0.), (0., 1., 0., 0.), (0., 0., 1., 0.),
			(0., 0., 0., 1.) )

		self.inv_bind_mat = defaultdict( ident )
		if "INV_BIND_MATRIX" in inputs:
			joints = inputs["JOINT"].source
			ibms = inputs["INV_BIND_MATRIX"].source
			ibms = [ ibms[i:i+16] for i in range(0, len(ibms), 16) ]
			for joint, ibm in zip( joints, ibms ):
				na = numpy.array
				ibm = na( [ibm[i:i+4] for i in range(0, len(ibm), 4) ] )
				self.inv_bind_mat[ joint ] = ibm

	def set_offsets( self, voff, ioff ):
		self.voffset = voff

	def indices( self ):
		return (i + self.voffset for i in self.ind)

	def vertices( self ):
		return self.data[ "POSITION" ]

	def normals( self ):
		return self.data[ "NORMAL" ]

	def colors( self ):
		return self.data[ "COLOR" ]

class ColladaGeometryInstance:
	def __init__( self, controller, skeleton ):
		self.controller = controller

	def bind_skeleton( self, node ):
		self.skeleton = node

	def load_animations( self, animations ):
		pass

class ColladaFile:
	def __init__( self, filename ):
		dom = parse( filename )

		self.geometries = {}
		geoms = dom.getElementsByTagName( 'geometry' )
		for geo in geoms:
			self.load_geometry( geo )

		self.controllers = {}
		controllers = dom.getElementsByTagName( 'controller' )
		for c in controllers:
			self.load_controller( c )

		animations = dom.getElementsByTagName( 'animation' )
		for a in animations:
			self.load_animation( a )

	def load_geometry( self, geo ):
		srcs = {}
		src_offs = {}

		geoid = geo.getAttribute( 'id' )
		mesh = geo.getElementsByTagName( 'mesh' )[0]
		srcs = self._load_sources( mesh )

		vertex = mesh.getElementsByTagName( 'vertices' )[0]
		vertex_inputs = self._load_inputs( vertex, False )

		plist = mesh.getElementsByTagName( 'polylist' )[0]
		plist_inputs = self._load_inputs( plist )

		if not "VERTEX" in plist_inputs:
			raise ValueError( "No vertex input in mesh." )

		plist_vertex = plist_inputs[ "VERTEX" ]
		del plist_inputs[ "VERTEX" ]

		# store offset for each sub-input of vertex input
		for vi in vertex_inputs.values():
			vi.offset = plist_vertex.offset
			plist_inputs[ vi.semantic ] = vi

		# match sources to inputs
		for i in plist_inputs.values():
			i.source = srcs[ i.source[1:] ]

		vcount = plist.getElementsByTagName( 'vcount' )[0]
		vcount = list( int(d) for d in vcount.firstChild.data.split() )

		p = plist.getElementsByTagName( 'p' )[0]
		p = list( int(d) for d in p.firstChild.data.split() )

		self.geometries[ geoid ] = \
			ColladaGeometry( plist_inputs, vcount, p )

	def load_controller( self, controller ):
		conid = controller.getAttribute( 'id' )
		skin = controller.getElementsByTagName( 'skin' )[0]
		srcid = skin.getAttribute( 'source' )

		geo = self.geometries[ srcid ] 
		self.controllers[ conid ] = geo

		bsm = numpy.array((
			(1., 0., 0., 0.), (0., 1., 0., 0.),
			(0., 0., 1., 0.), (0., 0., 0., 1.) ))

		if skin.getElementsByTagName( 'bind_shape_matrix' ):
			bsm = skin.getElementsByTagName( 'bind_shape_matrix' )[0]

		srcs = self._load_sources( skin )

		joint = skin.getElementsByTagName( 'joints' )[0]
		joint_inputs = self._load_inputs( joint, False )

		vweights = skin.getElementsByTagName( 'vertex_weights' )[0]
		vweights_inputs = self._load_inputs( vweights )

		if "JOINT" not in vweights_inputs:
			raise ValueError( "No joint input to skin." )

		vw_joint = vweights_inputs[ "JOINT" ]
		del vweights_inputs[ "JOINT" ]

		for ji in joint_inputs:
			ji.offset = vw_joint.offset
			vweights_inputs[ ji.semantic ] = ji

		for i in vweights_inputs:
			i.source = srcs[ i.source[1:] ]

		vcount = vweights.getElementsByTagName( 'vcount' )[0]
		vcount = [ int(d) for d in vcount.firstChild.data ]

		v = vweights.getElementsByTagName( 'v' )[0]
		v = [ int(d) for d in v.firstChild.data ]

		geo.load_controller( inputs, vcount, v )

	def load_animation( self, anim ):
		srcs = self._load_sources( anim )

		samplers = {}
		for s in anim.getElementsByTagName( 'sampler' ):
			id = s.getAttribute( 'id' )
			samplers[ id ] = self._load_inputs( s )

		channels = {}
		for c in anim.getElementsByTagName( 'channel' ):
			src = c.getAttribute( 'source' )
			target = c.getAttribute( 'target' )
			channels[ src ] = target

	def load_visual_scene( self, scene ):
		nodes = {}

		parent = None
		open_list = [ scene.getElementsByTagName( 'node' ) ]

		while open_list:
			parent = open_list.pop(0)
			#if 
		pass	

	def _load_sources( self, elem ):
		srcs = elem.getElementsByTagName( 'source' )
		src_data = {}

		for src in srcs:
			ident = src.getAttribute( 'id' )
			arrays = {
					'float_array': float,
					'Name_array': unicode,
					'int_array': int,
					'bool_array': bool 
				}

			for a in arrays:
				if src.getElementsByTagName(a):
					data = src.getElementsByTagName(a)[0].firstChild.data
					data = [ arrays[a](d) for d in data.split() ]
					src_data[ ident ] = ColladaSource( ident, data )
					break

			if src.getElementsByTagName( 'technique_common' ):
				tc = src.getElementsByTagName( 'technique_common' )[0]

		return src_data

	def _load_inputs( self, elem, shared = True ):
		inputs = elem.getElementsByTagName( 'input' )
		input_data = {}

		for input in inputs:
			offset = None
			if shared:
				offset = int( input.getAttribute( 'offset' ) )
			source = input.getAttribute( 'source' )
			semantic = input.getAttribute( 'semantic' )

			i = ColladaInput( offset, semantic, source )
			input_data[ semantic ] = i
		return input_data




