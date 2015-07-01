
import pygame
from pygame.locals import *

import OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *

try:
	from advanced_renderer import *
	shaders_enabled = True
except ImportError:
	class Program:
		Vertex = 0
		Normal = 1
		Color = 2
		TexCoord0 = 3
	shaders_enabled = False

#from OpenGL.arrays import ArrayDatatype as ADT

from itertools import *
from ctypes import *
import pdb
import numpy
from numpy import sin, cos, sqrt

class Renderer:
	def __init__( self, width, height ):
		self.width, self.height = width, height
		
		pygame.init()
		flags =  pygame.OPENGL | pygame.DOUBLEBUF
		screen = pygame.display.set_mode( (width, height), flags )#, 32 )

		print glGetString( GL_VERSION )

		glClearColor( 0.0, 0.0, 0.0, 1.0 )
		glClearDepth( 1.0 )
		glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

		glEnable( GL_DEPTH_TEST )
		glEnable( GL_CULL_FACE )

		glViewport( 0, 0, width, height )

		self.ortho()
		self.origin()
		pygame.display.flip()

	def __del__( self ):
		pygame.quit()

	def begin_frame( self ):
		glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

	def end_frame( self ):
		pygame.display.flip()

	def reset_target( self ):
		glBindFramebufferEXT( GL_FRAMEBUFFER_EXT, 0 )
		glViewport( 0, 0, self.width, self.height )
		
	def origin( self ):
		"""Set modelview matrix to identity."""
		glMatrixMode( GL_MODELVIEW )
		glLoadIdentity()

	def world( self, pos, look, up ):
		"""Set modelview matrix to current camera orientation."""
		glMatrixMode( GL_MODELVIEW )
		glLoadIdentity()

		gluLookAt(
				pos[0], pos[1], pos[2],
				look[0] + pos[0], look[1] + pos[1], look[2] + pos[2],
				up[0], up[1], up[2],
			)

	def perspective( self, fov, nearz, farz ):
		"""Setup projection matrix using internal parameters."""
		glMatrixMode( GL_PROJECTION )
		glLoadIdentity()
		aspect = float(self.width) / self.height
		gluPerspective( fov, aspect, nearz, farz )

	def ortho( self ):
		"""Setup projection matrix for orthographic projection."""
		glMatrixMode( GL_PROJECTION )
		glLoadIdentity()
		glOrtho( 0.0, self.width, 0.0, self.height, -1.0, 1.0 )
		
class Camera:
	def __init__( self, position, look, up ):
		self.position = numpy.array(position)
		self.look = numpy.array(look)
		self.up = numpy.array(up)

		self.rotation = numpy.array((0., 0.))
		self.translation = numpy.array((0., 0.))

	@staticmethod
	def _cross_product_matrix( x ):
		 return numpy.array((
			 (0., -x[2], x[1]), 
			 (x[2], 0., -x[0]), 
			 (-x[1], x[0], 0.)
		 ))

	def rotate( self, x, y ):
		sx, cx = sin(x), cos(x)
		sy, cy = sin(y), cos(y)

		right = numpy.cross( self.look, numpy.array((0., 1., 0.)) )
		right = right / numpy.linalg.norm( right )

		rotx = (
			cx * numpy.identity( 3 ) +
			sx * self._cross_product_matrix( right ) +
			(1. - cx) * numpy.outer( right, right )
		)
		roty = numpy.array(((cy, 0., sy), (0., 1., 0.), (-sy, 0., cy)))

		self.look = numpy.dot( rotx, numpy.dot( roty, self.look ) )
		if self.look[1] > 0.9 or self.look[1] < -0.9:
			scale = sqrt(.19 / (self.look[0]**2 + self.look[2]**2))
			y = 0.9 if self.look[1] > 0.9 else -0.9
			self.look = numpy.array((scale*self.look[0], y, scale*self.look[2]))
		self.look = self.look / numpy.linalg.norm(self.look)
	
		right = numpy.cross( self.look, numpy.array((0., 1., 0.)) )
		self.up = numpy.cross( right, self.look ) 
		self.up = self.up / numpy.linalg.norm(self.up)
	
	def translate( self, dx, dz ):
		right = numpy.cross( self.look, numpy.array((0., 1., 0.)) )
		self.position += right*dx + self.look*dz
	
	def set_translation( self, x = None, z = None ):
		if x is not None: self.translation[0] = x
		if z is not None: self.translation[1] = z
	
	def set_rotation( self, x = None, y = None ):
		if x is not None: self.rotation[0] = x
		if y is not None: self.rotation[1] = y

	def update( self, renderer ):
		self.rotate( self.rotation[0], self.rotation[1] )
		self.translate( self.translation[0], self.translation[1] )
		renderer.world( self.position, self.look, self.up )

class Texture:
	glTexImageFn = { 1: glTexImage1D, 2: glTexImage2D, 3: glTexImage3D }
	glTarget = { 1: GL_TEXTURE_1D, 2: GL_TEXTURE_2D, 3: GL_TEXTURE_3D }

	def __init__( self, data, data_dimensions,
				data_type = GL_UNSIGNED_BYTE, 
				data_format = GL_RGB, 
				gl_precision = GL_RGB,
				min_filter = GL_LINEAR, 
				mag_filter = GL_LINEAR, 
				wrap_s = GL_REPEAT,
				wrap_t = GL_REPEAT
			):
		
		ndimensions = len( data_dimensions )
		self.target = self.glTarget[ ndimensions ]

		self.texture = glGenTextures( 1 )
		glBindTexture( self.target, self.texture )

		glTexParameter( self.target, GL_TEXTURE_MIN_FILTER, min_filter )
		glTexParameter( self.target, GL_TEXTURE_MAG_FILTER, mag_filter )
		glTexParameter( self.target, GL_TEXTURE_WRAP_S, wrap_s )
		glTexParameter( self.target, GL_TEXTURE_WRAP_T, wrap_t )
		
		args = [ self.target, 0, gl_precision, ]
		args.extend( data_dimensions )
		args.extend( [0, data_format, data_type, data] )
		#print args
		self.glTexImageFn[ ndimensions ] ( *args )
		print "Loaded."

	def apply( self, active_texture = 0 ):
		glEnable( self.target )
		glActiveTexture( GL_TEXTURE0 + active_texture )
		glBindTexture( self.target, self.texture )

	def __del__( self ):
		glDeleteTextures( self.texture )

class Color:
	def __init__( self, *data ):
		self.r, self.g, self.b = data

class Material:
	cache = {}

	@staticmethod
	def load( filename ):
		if filename not in Material.cache:
			image = pygame.image.load( filename )
			data = pygame.image.tostring( image, "RGB", 1 )
			width, height = image.get_width(), image.get_height()
			print width, height
			Material.cache[ filename ] = Material( data, (width, height), filename )
		return Material.cache[ filename ]

	def __init__( self, data, dims, filename = None, 
	              precision = GL_RGB, format = GL_RGB, type = GL_UNSIGNED_BYTE,
				  filter = GL_LINEAR
			):
		self.filename = filename
		self.texture = Texture( data, dims, type, format, precision, filter, filter )

	def apply( self, active_texture = 0 ):
		self.texture.apply(active_texture)


class Batch:
	Vertex = 0
	Normal = 1
	Color = 2
	TexCoord0 = 3
	Index = 100
	
	F2 = 0
	F3 = 1
	UB4 = 2
	US1 = 3
	UI1 = 4
	
	type_data = {
			F2: (GL_FLOAT, GLfloat, 2),
			F3: (GL_FLOAT, GLfloat, 3),
			UB4: (GL_UNSIGNED_BYTE, GLubyte, 4),
			US1: (GL_UNSIGNED_SHORT, GLushort, 1),
			UI1: (GL_UNSIGNED_INT, GLuint, 1)
		}
	
	data_function = {
			Vertex: (
				"vertices", GL_VERTEX_ARRAY, 
				 glVertexPointer, 
				 Program.Vertex),
			Normal: (
				"normals", GL_NORMAL_ARRAY, 
				lambda s, t, st, p: glNormalPointer( t, st, p ), 
				Program.Normal),
			Color: (
				"colors", GL_COLOR_ARRAY, 
				glColorPointer, 
				Program.Color),
			TexCoord0: (
				"texcoord0", GL_TEXTURE_COORD_ARRAY,
				lambda s, t, st, p: 
					(glClientActiveTexure(GL_TEXTURE0), 
					 glTexCoordPointer(s,t,st,p)),
				Program.TexCoord0
			),

			Index: ("indices", GL_INDEX_ARRAY, None, None)
		}

	class DrawData:
		BOUNDED = 0
		INSTANCED = 1

		@staticmethod
		def bounded( start, stop ):
			 return Batch.DrawData(data_type = Batch.DrawData.BOUNDED, bounds = (start,stop))

		@staticmethod
		def instanced( n ):
			 return Batch.DrawData(data_type = Batch.DrawData.INSTANCED, n = n)

		def __init__( self, **keys ):
			self.__dict__.update( keys )

	def __init__( self, draws, VBO = True ):
		self.draws = draws
		if not len( draws ):
			raise AttributeError( "Must have something." )

		if not glGenBuffers:
			raise AttributeError( "No VBOs." )
		
		self.vertex_buffer = None
		self.VBO = VBO
		self.rebuild( True )

	def rebuild( self, recreate = False ):
		nv, ni = 0, 0
		for d in self.draws:
			d.set_offsets( nv, ni )
			nv, ni = nv + d.nvertices, ni + d.nindices
		self.nvertices, self.nindices = nv, ni

		built_data = {}
		cls = self.draws[0].__class__
		dtypes = self.draws[0].batch_data
		for data, dtype in dtypes.iteritems():
			name, gl_state, gl_set, prog_set = self.data_function[ data ]
			fn = getattr( cls, name )
			built_data[data] = self._generate_data( dtype, fn, self.draws, data == self.Index )

		if self.Index in built_data:
			self.indices = built_data.pop( self.Index )

			if self.VBO:
				self.indices2 = glGenBuffers(1)
				glBindBuffer( GL_ELEMENT_ARRAY_BUFFER, self.indices2 )
				glBufferData( GL_ELEMENT_ARRAY_BUFFER, self.indices,
					GL_DYNAMIC_DRAW )

			self.index_gl_type = self.type_data[dtypes[ self.Index ]][0]
			self.draw = self._draw_indexed
		else:
			self.draw = self._draw

		self.buffers, self.data_types = {}, {}
		for data, bdata in built_data.items():
			self.data_types[ data ] = dtypes[ data ]
			if self.VBO:
				self.buffers[ data ] = glGenBuffers(1)
				glBindBuffer( GL_ARRAY_BUFFER_ARB, self.buffers[data] )
				glBufferData( GL_ARRAY_BUFFER_ARB, bdata, GL_DYNAMIC_DRAW )
				#glBufferData( GL_ARRAY_BUFFER_ARB, sizeof(bdata), bdata, GL_DYNAMIC_DRAW )
			else:
				self.buffers[ data ] = bdata

	def update( self, user_data = None ):
		if self.draws[0].update:
			glBindBuffer( GL_ELEMENT_ARRAY_BUFFER, self.indices2 )
			data = glMapBuffer( GL_ELEMENT_ARRAY_BUFFER, GL_READ_WRITE )

			bound = { self.Index: data }
			for data, dtype in self.data_types.items():
				glBindBuffer( GL_ARRAY_BUFFER, self.buffers[ data ] )
				bound[ data ] = glMapBuffer( 
						GL_ARRAY_BUFFER, GL_READ_WRITE )

			for d in self.draws:
				d.dynamic_update( bound, user_data )

			glUnmapBuffer( GL_ELEMENT_ARRAY_BUFFER )
			for data, dtype in self.data_types.items():
				glBindBuffer( GL_ARRAY_BUFFER, self.buffers[ data ] )
				glUnmapBuffer( GL_ARRAY_BUFFER )

	def _draw( self, draw_data = None, shader = None ):
		self._bind( shader )
		if draw_data is not None and draw_data.data_type == self.DrawData.INSTANCED:
			glDrawArraysInstanced( GL_TRIANGLES, 0, self.nvertices, draw_data.n )
			return

		start, stop = 0, self.nvertices
		if draw_data is not None and draw_data.data_type == self.DrawData.BOUNDED:
			start, stop = draw_data.bounds
		glDrawArrays( GL_TRIANGLES, start, stop )
		self._unbind( shader )

	def _draw_indexed( self, draw_data = None, shader = None ):
		self._bind( shader )
		start, stop = 0, self.nindices
		if draw_data is not None and draw_data.data_type == self.DrawData.BOUNDED:
			start, stop = draw_data.bounds

		glBindBuffer( GL_ELEMENT_ARRAY_BUFFER, self.indices2 )
		glDrawElements( GL_TRIANGLES, stop-start,
				self.index_gl_type, None ) #self.indices ) #byref(self.indices, start) )
		self._unbind( shader )
	
	def _bind( self, shader ):
		bind = self._bind_data
		if shader is not None:
			bind = self._bind_data_program
		
		for data, dtype in self.data_types.items():
			bind( self.buffers[data], data, dtype, shader )

	def _unbind( self, shader ):
		for data, dtype in self.data_types.items():
			name, gl_state, gl_set, prog_set = self.data_function[ data ]
			glDisableClientState( gl_state )
		if self.VBO:
			glBindBuffer( GL_ARRAY_BUFFER_ARB, 0 )

	def _bind_data_program( self, buffer, data, data_type, program ):
		name, gl_state, gl_set, prog_set = self.data_function[ data ]
		gl_type, c_type, n = self.type_data[ data_type ]
		
		glDisableClientState( gl_state )
		glBindBuffer( GL_ARRAY_BUFFER_ARB, buffer )
		program.bind( prog_set, gl_type, None )
	
	def _bind_data( self, buffer, data, data_type, program = None ):
		name, gl_state, gl_set, prog_set = self.data_function[ data ]
		gl_type, c_type, n = self.type_data[ data_type ]
		
		if self.VBO:
			glBindBuffer( GL_ARRAY_BUFFER_ARB, buffer )
			gl_set( n, gl_type, 0, None )
		else:
			gl_set( n, gl_type, 0, buffer )
		glEnableClientState( gl_state )

	def _generate_data( self, data_type, fn, draws, index = False ):
		nitems = self.nvertices
		if index:
			nitems = self.nindices
		
		def generator():
			for d in draws:
				arr = iter( fn(d) )
				for i in range(d.nindices if index else d.nvertices):
					yield arr.next()

		gl_type, c_type, n = self.type_data[ data_type ]
		iterator = generator()
		if n > 1:
			iterator = chain.from_iterable( iterator )
		arr_type = c_type * (nitems * n)
		data = arr_type( *iterator )
		print data
		return data

