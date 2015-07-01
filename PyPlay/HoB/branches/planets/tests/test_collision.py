
from simulation import *
from collision import *
from tilemap import *

import unittest
import logging, sys

class TriggerCollisionTests( unittest.TestCase ):
	def setUp( self ):
		logging.basicConfig( stream=sys.stdout, level=logging.DEBUG )
		self.world = World()
		self.world.add_system( CollisionSystem2D(timestep = 1.0) )

		tilemapent = Entity()
		tilemapent.add_component( Tilemap( 30, 30, 16. / 272, 16. / 192 ) )
		self.world.add_entity( tilemapent )

	def _create_physics( self, pos, rot, vel, ang_vel,
		aabb_min, aabb_dim, mass, rot_inertia, **kwargs ):

		ent = Entity()
		ent.add_component( Transform( pos, [0, 0, rot] ) )
		ent.add_component( Physics( mass, rot_inertia ) )
		ent.get_component( ComponentType.Physics ).velocity = \
			Vector3f( vel )
		ent.get_component( ComponentType.Physics ).angular_velocity = ang_vel

		collmesh = CollisionMesh()
		collmesh.add_geometry( CollAABB( aabb_min, aabb_dim ) )
		ent.add_component( collmesh )

		if kwargs['add']:
			self.world.add_entity( ent )
		return ent

	def _assert_vector_equal( self, v1, v2 ):
		for i in range(3): 
			self.assertAlmostEqual( v1[i], v2[i] )

	def _assert_physics( self, ent, vel, ang_vel ):
		p = ent.get_component( ComponentType.Physics )
		self._assert_vector_equal( p.velocity, vel )
		self.assertAlmostEqual( p.angular_velocity, ang_vel )

	def test_simple_edge_line_collision( self ):
		o1 = self._create_physics( [90, 100, 0], 0., 
			[5.5, 0, 0], 0, [-5, -5, 0], [10, 10, 0], 10, 100, add=True)

		o2 = self._create_physics( [110, 100, 0], 3.141592654/4, 
			[-5.5, 0, 0], 0, [-5, -5, 0], [10, 10, 0], 10, 100, add=True )

		self.world.update()
		self._assert_physics( o1, [-5.5, 0, 0], 0. )
		self._assert_physics( o2, [5.5, 0, 0], 0. )

	def test_simple_line_line_collision( self ):
		o1 = self._create_physics( [90, 100, 0], 0., 
			[5.5, 0, 0], 0, [-5, -5, 0], [10, 10, 0], 10, 100, add=True)

		o2 = self._create_physics( [110, 100, 0], 0., 
			[-5.5, 0, 0], 0, [-5, -5, 0], [10, 10, 0], 10, 100, add=True )

		self.world.update()
		self._assert_physics( o1, [-5.5, 0, 0], 0. )
		self._assert_physics( o2, [5.5, 0, 0], 0. )

	def test_large_overlap_collision( self ):
		o1 = self._create_physics( [90, 100, 0], 0., 
			[10, 0, 0], 0, [-5, -5, 0], [10, 10, 0], 10, 100, add=True)

		o2 = self._create_physics( [110, 100, 0], 3.141592654/4, 
			[-10, 0, 0], 0, [-5, -5, 0], [10, 10, 0], 10, 100, add=True )

		self.world.update()
		self._assert_physics( o1, [-10, 0, 0], 0. )
		self._assert_physics( o2, [10, 0, 0], 0. )

