
from math import sqrt, cos, sin, pi
from random import random

from ctypes import *
import numpy
from itertools import product

from renderer import Batch
from planet_c.planet import Perlin, Brownian
#from noise import Perlin, Brownian
from planet_c.roam import SphericalROAM as SphericalROAM2

class Color:
	def __init__( self, r, g, b ):
		self.r, self.g, self.b = r, g, b
	def __add__( self, other ):
		return Color( self.r+other.r, self.g+other.g, self.b+other.b )
	def __mul__( self, other ):
		return Color( self.r*other, self.g*other, self.b*other )
	def color( self ):
		return ( c_ubyte*4 )( int(self.r), int(self.g), int(self.b), 0 )

class SphericalROAM:

	update = True
	batch_data = {
		Batch.Vertex: 	Batch.F3,
		Batch.Color:	Batch.UB4,
		Batch.Index:	Batch.US1
		}

	def __init__( self, position, noise ):
		self.p = position
		self.noise = noise

		self.nvertices = 5000
		self._vertices = ( c_float * 3 * 5000 )()
		self._colors = ( c_ubyte * 4 * 5000 )()

		self.nindices = 30000
		self._indices = ( c_short * 30000 )()
		self._neighbors = ( c_short * 30000 )()

		self._diamonds = set()
		self._diamond_parents = {}

		self._free_verts = list( range(5000) )
		self._free_indices = list( range(10000) )

		self._used_verts = 0
		self._used_indices = 0
		self._initial_geometry()

		return

		for i in range( 4 ):
			for i in range( 1000 ):
				print self._used_verts 
				index = int( random() * (self._used_indices-1) ) 
				if self._indices[ index*3 + 1 ] != 0:
					self._split( index )

			for  i in range( 500 ):
				d = self._diamonds.pop()
				self._merge( d )

	def _priority( self, tri, pos, look ):
		x1, y1, z1 = self._vertices[ self._indices[ tri*3 + 0 ] ]
		x2, y2, z2 = self._vertices[ self._indices[ tri*3 + 2 ] ]

		x, y, z = (x1 + x2) / 2., (y1 + y2) / 2., (z1 + z2) / 2.
		pos, color = self._get_point( x, y, z )

		l = sqrt( x*x + y*y + z*z )
		new_l = sqrt( pos[0]*pos[0] + pos[1]*pos[1] + pos[2]*pos[2] )
		diff = abs( l - new_l )

		return -( look[0] * x + look[1] * y + look[2] * z ) / l * diff

	def dynamic_update( self, data, camera_data ):
		pos, look = camera_data

		ti, tv, tc = self._indices, self._vertices, self._colors
		self._indices = cast( data[ Batch.Index ], POINTER( c_short ) )
		self._vertices = cast( data[ Batch.Vertex ], POINTER( c_float*3 ) )
		self._colors = cast( data[ Batch.Color ], POINTER( c_ubyte*4 ) )

		temp_diamonds = set( self._diamonds )
		for d in temp_diamonds:
			if self._priority( d[0], pos, look ) < 0.3:
				self._merge( d )

		for tri in range( 10000 ):
			if tri not in self._free_indices:
				pri = self._priority( tri, pos, look )
				if pri > 0.4:
					self._split( tri )

		#index = int( random() * (self._used_indices-1) )
		#if self._indices[ index*3 + 1 ] != 0:
		#	self._split( index )

		self._indices, self._vertices, self._colors = ti, tv, tc

	def _initial_geometry( self ):
		for x, y, z in product( (-1., 1.), repeat=3 ):
			self._add_point( x, y, z )

		l1 = self._add_tri( 0, 1, 3 )
		l2 = self._add_tri( 3, 2, 0 )

		t1 = self._add_tri( 2, 3, 7 )
		t2 = self._add_tri( 7, 6, 2 )

		b1 = self._add_tri( 1, 0, 4 )
		b2 = self._add_tri( 4, 5, 1 )

		f1 = self._add_tri( 3, 1, 5 )
		f2 = self._add_tri( 5, 7, 3 )

		ba1 = self._add_tri( 4, 0, 2 )
		ba2 = self._add_tri( 2, 6, 4 )

		r1 = self._add_tri( 7, 5, 4 )
		r2 = self._add_tri( 4, 6, 7 )

		self._set_neighbors( l1, b1, f1, l2 )
		self._set_neighbors( l2, t1, ba1, l1 )

		self._set_neighbors( t1, l2, f2, t2 )
		self._set_neighbors( t2, r2, ba2, t1 )

		self._set_neighbors( b1, l1, ba1, b2 )
		self._set_neighbors( b2, r1, f1, b1 )

		self._set_neighbors( f1, l1, b2, f2 )
		self._set_neighbors( f2, r1, t1, f1 )

		self._set_neighbors( ba1, b1, l2, ba2 )
		self._set_neighbors( ba2, t2, r2, ba1 )

		self._set_neighbors( r1, f2, b2, r2 )
		self._set_neighbors( r2, ba2, t2, r1 )

	cmap_pts = [ (0, Color(0, 0, 255)), 
			(50, Color(100, 100, 255)),
			(100, Color(100, 200, 100)),
			(175, Color(0, 200, 0)),
			(255, Color(255, 255, 255)) ]
	cmap = []
	index, cur, next = 0, cmap_pts[0], cmap_pts[1]
	for i in range( 255 ):
		t = (i - cur[0]) / float(next[0] - cur[0])
		cmap.append( (cur[1]*t + next[1]*(1.-t)).color() )
		if i > next[0]:
			index += 1
			cur, next = next, cmap_pts[ index + 1 ]

	def _get_point( self, x, y, z ):
		l = sqrt( x*x + y*y + z*z )
		off = self.noise( 1. + x / l,  1. + y / l, 1. + z / l )

		h = off + 10.
		pos = ( c_float * 3 )( x*h/l, y*h/l, z*h/l )
		color = self.cmap[ int((off + 3.01) / 6.02 * 255) ]
		return pos, color

	def _add_point( self, x, y, z ):
		if not self._free_verts:
			return -1

		pos, color = self._get_point( x, y, z )
		index = self._free_verts.pop( 0 )
		self._vertices[ index ] = pos
		self._colors[ index ] = color
		temp = ( c_ubyte * 4 )(
				int(random()*250), int(random()*250),
				int(random()*250), 0 )
		self._used_verts += 1
		return index

	def _remove_point( self, pt ):
		self._free_verts.append( pt )
		self._used_verts -= 1

	def _add_tri( self, i, j, k ):
		if not self._free_indices:
			return -1

		index = self._free_indices.pop( 0 )
		self._indices[ 3*index + 0 ] = i
		self._indices[ 3*index + 1 ] = j
		self._indices[ 3*index + 2 ] = k
		self._used_indices += 1
		return index

	def _remove_tri( self, tri ):
		for i in range( 3 ):
			self._indices[ 3*tri + i ] = 0
		self._free_indices.append( tri )
		self._used_indices -= 1

	def _set_neighbors( self, t, i, j, k ):
		self._neighbors[ t*3 + 0 ] = i
		self._neighbors[ t*3 + 1 ] = j
		self._neighbors[ t*3 + 2 ] = k
	
	def _build_diamond( self, tri ):
		l = [ tri ]
		pos = tri

		for i in range( 3 ):
			pos = self._neighbors[ pos*3 + 0 ]
			l.append( pos )

		if self._neighbors[ pos*3 + 0 ] == tri:
			return tuple( sorted(l) )
		return None

	def _add_diamond( self, tri ):
		if self._indices[ tri*3 + 1 ] < 8:
			return 

		l = self._build_diamond( tri )
		if l:	self._diamonds.add( l )

	def _remove_diamond( self, tri ):
		if self._indices[ tri*3 + 1 ] < 8:
			return 

		l = self._build_diamond( tri )
		if l:	self._diamonds.remove( l )

	def _split( self, tri ):
		long_edge = self._neighbors[ tri*3 + 2 ]
		if self._neighbors[ long_edge*3 + 2 ] != tri:
			self._split( long_edge )
			long_edge = self._neighbors[ tri*3 + 2 ]

		x1, y1, z1 = self._vertices[ self._indices[ tri*3 + 0 ] ]
		x2, y2, z2 = self._vertices[ self._indices[ tri*3 + 2 ] ]

		x, y, z = (x1 + x2) / 2., (y1 + y2) / 2., (z1 + z2) / 2.
		l = 1.5 / sqrt( x*x + y*y + z*z )
		new_pt = self._add_point( x*l, y*l, z*l )

		if new_pt == -1:
			return

		i = self._indices[ tri*3 + 2 ]
		j = self._indices[ long_edge*3 + 2 ]

		t1 = self._add_tri( i, new_pt, self._indices[ tri*3 + 1 ] )
		t2 = self._add_tri( j, new_pt, self._indices[ long_edge*3 + 1 ] )

		if t1 == -1 or t2 == -1:
			return

		self._remove_diamond( tri )
		self._remove_diamond( long_edge )

		i2 = self._indices[ tri*3 + 0 ]
		self._indices[ tri*3 + 0 ] = self._indices[ tri*3 + 1 ]
		self._indices[ tri*3 + 1 ] = new_pt
		self._indices[ tri*3 + 2 ] = i2

		j2 = self._indices[ long_edge*3 + 0 ]
		self._indices[ long_edge*3 + 0 ] = self._indices[ long_edge*3 + 1 ]
		self._indices[ long_edge*3 + 1 ] = new_pt
		self._indices[ long_edge*3 + 2 ] = j2

		n1, n2 = self._neighbors[ tri*3 + 0 ], self._neighbors[ tri*3 + 1 ]
		self._set_neighbors( tri, t1, t2, n1 )
		self._set_neighbors( t1, long_edge, tri, n2 )

		def do_it( i, eq, new ):
			for j in range(3):
				if self._neighbors[ i*3 + j ] == eq:
					self._neighbors[ i*3 + j ] = new

		do_it( n2, tri, t1 )

		n1, n2 = self._neighbors[ long_edge*3 + 0 ], \
				self._neighbors[ long_edge*3 + 1 ]
		self._set_neighbors( long_edge, t2, t1, n1 )
		self._set_neighbors( t2, tri, long_edge, n2 )

		do_it( n2, long_edge, t2 )

		l = [ tri, long_edge, t1, t2 ]
		d = tuple( sorted(l) )
		self._diamonds.add( d )
		self._diamond_parents[ d ] = ( tri, long_edge, t1, t2 )

	def _merge( self, diamond ):
		pt = self._indices[ diamond[ 0 ]*3 + 1 ]
		self._remove_point( pt )

		p1, p2, c1, c2 = self._diamond_parents[ diamond ]

		self._indices[ p1*3 + 0 ] = self._indices[ p1*3 + 2 ]
		self._indices[ p1*3 + 1 ] = self._indices[ c1*3 + 2 ]
		self._indices[ p1*3 + 2 ] = self._indices[ c1*3 + 0 ]

		self._indices[ p2*3 + 0 ] = self._indices[ p2*3 + 2 ]
		self._indices[ p2*3 + 1 ] = self._indices[ c2*3 + 2 ]
		self._indices[ p2*3 + 2 ] = self._indices[ c2*3 + 0 ]

		self._remove_tri( c1 )
		self._remove_tri( c2 )

		n1, n2 = self._neighbors[ p1*3 + 2 ], self._neighbors[ c1*3 + 2 ]
		self._set_neighbors( p1, n1, n2, p2 )

		def do_it( i, eq, new ):
			for j in range(3):
				if self._neighbors[ i*3 + j ] == eq:
					self._neighbors[ i*3 + j ] = new

		do_it( n2, c1, p1 )

		n1, n2 = self._neighbors[ p2*3 + 2 ], self._neighbors[ c2*3 + 2 ]
		self._set_neighbors( p2, n1, n2, p1 )

		do_it( n2, c2, p2 )

		self._diamonds.discard( diamond )
		self._add_diamond( p1 )
		self._add_diamond( p2 )

	def set_offsets( self, vertex_off, index_off ):
		self.voff, self.ioff = vertex_off, index_off

	def vertices( self ):
		return self._vertices

	def colors( self ):
		return self._colors

	def indices( self ):
		return (i + self.voff for i in self._indices)

class Patch:
	verts_per_lod = 32
	theta_span = pi / 20.
	phi_span = 2 * pi / 20.

	batch_data = {
		Batch.Vertex: 	Batch.F3,
		Batch.Color:	Batch.UB4,
		Batch.Index:	Batch.UI1
		}

	def __init__( self, pos, noise, lod, lod_boundary = False ):
		self.theta, self.phi = pos

		self.lod = lod
		self.dim = self.verts_per_lod * lod

		self.nvertices = self.dim ** 2
		self.nindices = 6 * (self.dim - 1) ** 2

		self.lod_boundary = lod_boundary
		if lod_boundary:
			self.nvertices += self.dim - 1

		self._vertices = ( c_float * 3 * self.nvertices )()
		self._colors = ( c_ubyte * 4 * self.nvertices )()
		self._indices = ( c_uint * self.nindices )()
		self._calculate_heights( noise )


	def _calculate_heights( self, noise ):
		for j in range( self.dim ):
			for i in range( self.dim ):
				t = self.theta + i * self.theta_span / (self.dim - 1)
				p = self.phi + j * self.phi_span / (self.dim - 1)
				x, y, z = cos(p) * sin(t), sin(p) * sin(t), cos(t)
				r = 10. + noise( x + 1., y + 1., z + 1. ) ** 2

				off = i + j*self.dim
				self._vertices[ off ] = (c_float * 3) (
						r * cos(p) * sin(t), 
						r * sin(p) * sin(t),
						r * cos(t) )

				self._colors[ off ] = (c_ubyte * 4) (
						100 + int((r-10.) * 100), 10, 0, 0 )

				if i != self.dim - 1 and j != self.dim - 1:
					ioff = 6 * (i + j*(self.dim -1))
					self._indices[ ioff + 0 ] = off
					self._indices[ ioff + 1 ] = off + 1
					self._indices[ ioff + 2 ] = off + self.dim + 1
					self._indices[ ioff + 3 ] = off
					self._indices[ ioff + 4 ] = off + self.dim + 1
					self._indices[ ioff + 5 ] = off + self.dim

	def set_offsets( self, vertex_off, index_off ):
		self.voff, self.ioff = vertex_off, index_off

	def vertices( self ):
		return self._vertices

	def colors( self ):
		return self._colors

	def indices( self ):
		return (i + self.voff for i in self._indices)

	
class Planet:
	def __init__( self, renderer ):
		self.noise = Brownian()
		self.noise.add_component( 2., 3. )
		self.noise.add_component( 0.5, 15. )
		self.noise.add_component( 0.1, 30. )

		self.patches = [ SphericalROAM( None, self.noise.noise ) ]
		self.patches = [ SphericalROAM2( 50000, 100000, self.noise.noise ) ]

		self.batch = Batch( self.patches )

	def draw( self, renderer, camera ):
		camera.update( renderer )

		c_float_p = POINTER(c_float)
		pos = camera.position.astype(numpy.float32)
		look = camera.look.astype(numpy.float32)

		self.batch.update( 
			(	pos.ctypes.data_as(c_float_p), 
				look.ctypes.data_as(c_float_p) ) )

		self.batch.draw()

		
