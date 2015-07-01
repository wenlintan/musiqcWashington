
from collections import defaultdict
from itertools import chain
from math import sqrt
import logging

from flags import *
from simulation import *
from tilemap import Tilemap

class Physics( Component ):
	Trigger = 0
	Normal = 1
	Swept = 2

	def __init__( self, mass, rot_inertia, restitution=1.0, friction=0.3 ):
		super( Physics, self ).__init__( ComponentType.Physics )
		self.coll_type = Physics.Normal
		self.mass = mass
		self.rotational_inertia = rot_inertia
		
		self.inv_mass, self.inv_rotational_inertia = 0., 0.
		if mass > 0.:			self.inv_mass = 1. / mass
		if rot_inertia > 0.:	self.inv_rotational_inertia = 1. / rot_inertia	

		self.restitution = restitution
		self.friction = friction

		self.velocity = Vector3f(0., 0., 0.)
		self.angular_velocity = 0.

		self.acceleration = Vector3f(0., 0., 0.)
		self.angular_acceleration = 0.

class Trigger( Component ):
	def __init__( self ):
		super( Trigger, self ).__init__( ComponentType.Trigger )
		self.triggered = False
		self.entity = None

class Contact2D:
	def __init__( self ):
		self.ents = [ None, None ]
		self.axes = [ None, None ]
		self.pts = [ None, None ]

	@staticmethod
	def entity_contact( ent1, ent2 ):
		c = Contact2D()
		c.set_data( 0, ent1 )
		c.set_data( 1, ent2 )
		c.key = (ent1, ent2)
		return c

	@staticmethod
	def tile_contact( ent, tile ):
		c = Contact2D()
		c.set_data( 0, ent )
		c.set_data( 1, tile, tilemap=True )
		c.key = (ent, tile[0], tile[1])
		return c

	def set_data( self, index, data, tilemap = False ):
		if tilemap:
			self.axes[ index ], self.pts[ index ] = self._tile_data( data )
		else:
			self.ents[ index ] = data
			self.axes[ index ], self.pts[ index ] = self._entity_data( data )

	def update( self ):
		for i, e in enumerate( self.ents ):
			if e is not None: 
				self.axes[i], self.pts[i] = self._entity_data( e )

	def _entity_data( self, ent ):
		cmesh = ent.get_component( ComponentType.CollisionMesh )
		cmesh = cmesh.get_geometry()
		right, up = ent.transform().right(), ent.transform().up()

		pos = ent.transform().transform( cmesh.pos )
		pts = [ pos, pos + right*cmesh.dim[0], pos + up*cmesh.dim[1], 
			pos + right*cmesh.dim[0] + up*cmesh.dim[1] ]
		return (right, up), pts

	def _tile_data( self, tile ):
		self.tx, self.ty = tx, ty = tile
		tsize = 16.

		axes = ( Vector3f( -1., 0., 0. ), Vector3f( 0., -1., 0. ) )
		tpts = [ Vector3f(tx*tsize, ty*tsize, 0), 
			Vector3f((tx+1)*tsize, ty*tsize, 0),
			Vector3f(tx*tsize, (ty+1)*tsize, 0), 
			Vector3f((tx+1)*tsize, (ty+1)*tsize, 0) ]
		return axes, tpts

	def trigger_only( self ):
		ents = [ e for e in self.ents if e is not None ]
		if any( not e.has_component( ComponentType.Physics ) for e in ents ):
			return True

		phys = [ e.get_component( ComponentType.Physics ) for e in ents ]
		if any( p.coll_type == Physics.Trigger for p in phys ):
			return True
		return False

class CollisionSystem2D( System ):
	def __init__( self, timestep = 1./30 ):
		super( CollisionSystem2D, self ).__init__()
		self.entities = []
		self.tilemap = None
		self.timestep = timestep

		self.overlaps = {}

	def update( self, ent ):
		if ent.has_component( ComponentType.Tilemap ):
			self.tilemap = ent.get_component( ComponentType.Tilemap )
		if ent.has_component( ComponentType.CollisionMesh ):
			self.entities.append( ent )

	def broad_collide( self, ent ):
		tsize = 16
		cmesh = ent.get_component( ComponentType.CollisionMesh )
		cmesh = cmesh.get_geometry()
		right, up = ent.transform().right(), ent.transform().up()

		pos = ent.transform().transform( cmesh.pos )
		pts = [ pos, pos + right*cmesh.dim[0], pos + up*cmesh.dim[1], 
			pos + right*cmesh.dim[0] + up*cmesh.dim[1] ]

		xs = [ int(pt[0]) for pt in pts ]
		ys = [ int(pt[1]) for pt in pts ]

		tiles = []
		for tx in range( min(xs)//tsize, max(xs)//tsize + 1 ):
			for ty in range( min(ys)//tsize, max(ys)//tsize + 1 ):
				for other in self.entity_positions[ (tx, ty) ]:
					if other is ent:	continue
					self.overlaps[(ent,other)] = \
						Contact2D.entity_contact(ent, other)
				self.entity_positions[ (tx, ty) ].add( ent )

				if self.tilemap is None: continue
				if self.tilemap.flags[ tx ][ ty ] & Tilemap.Collidable:
					self.overlaps[(ent,tx,ty)] = \
						Contact2D.tile_contact(ent, (tx, ty))

	def collide( self, overlap ):
		overlap.update()
		overlap.overlap = 1e100
		for i, axis_set in enumerate(overlap.axes):
			for j, axis in enumerate( axis_set ):
				pts0 = [ axis.dot( p ) for p in overlap.pts[0] ]
				pts1 = [ axis.dot( p ) for p in overlap.pts[1] ]

				if max( pts0 ) < min( pts1 ) or max( pts1 ) < min( pts0 ):
					return False

				if max( pts0 ) - min( pts1 ) < overlap.overlap:
					overlap.overlap = max( pts0 ) - min( pts1 )
					overlap.normal = axis
					overlap.axis_index = (i, j)
				if max( pts1 ) - min( pts0 ) < overlap.overlap:
					overlap.overlap = max( pts1 ) - min( pts0 )
					overlap.normal = -axis
					overlap.axis_index = (i, j)
		return True

	def toi( self, overlap ):
		ents = [ e for e in overlap.ents if e is not None ]
		if any( not e.has_component( ComponentType.Physics ) for e in ents ):
			return 1.0

		start, stop, safety = 0., 1.0, 0
		i, j = overlap.axis_index
		axis = overlap.axes[i][j]

		while safety < 100:
			test = ( stop + start ) / 2. 
			for e in ents:
				self.advance_physics( e, test )
			overlap.update()
			#self.collide( overlap )

			pts0 = [ axis.dot(pt) for pt in overlap.pts[0] ]
			pts1 = [ axis.dot(pt) for pt in overlap.pts[1] ]

			o = min( max( pts0 ) - min( pts1 ), max( pts1 ) - min( pts0 ) )
			if o < 0. and o > -0.05:
				break
	
			if o > 0.:		stop = test
			else:			start = test

			safety += 1

		if max( pts0 ) - min( pts1 ) < max( pts1 ) - min( pts0 ):
			target0 = max( pts0 )
			target1 = min( pts1 )
		else:
			target0 = min( pts0 )
			target1 = max( pts1 )

		pts0 = [ pt for pt in overlap.pts[0] \
			if abs( axis.dot(pt) - target0 ) < 0.05 ]
		pts1 = [ pt for pt in overlap.pts[1] \
			if abs( axis.dot(pt) - target1 ) < 0.05 ]

		if len( pts0 ) == 1:
			overlap.cpts = pts0
		elif len( pts1 ) == 1:
			overlap.cpts = pts1
		else:
			#TODO find 2 collision points
			normal = axis.cross( [0., 0., 1.] )
			dist0 = sorted( (normal.dot( pt ), pt) for pt in pts0 )
			dist1 = sorted( (normal.dot( pt ), pt) for pt in pts1 )
			if dist0[0][0] < dist1[0][0]:
				overlap.cpts = (dist0[1][1], dist1[0][1])
			else:
				overlap.cpts = (dist1[1][1], dist0[0][1])
			print( overlap.cpts[0], overlap.cpts[1] )

		if safety == 100:
			logging.info( "TOI did not converge, safety reached." )

		logging.debug( "Overlapping {0} along {1[0]}, {1[1]}".format(
			overlap.overlap, overlap.normal ) )
		return test

	def resolve( self, overlap ):
		ents = [ e for e in overlap.ents if e is not None ]
		tile_phys = Physics( 0., 0., restitution = 0. )
		phys0 = overlap.ents[0].get_component( ComponentType.Physics )
		phys1 = overlap.ents[1].get_component( ComponentType.Physics ) \
			if overlap.ents[1] is not None else tile_phys

		logging.debug( 'Initial velocity 0: ({0[0]}, {0[1]}) rot {1}'.format(
			phys0.velocity, phys0.angular_velocity ) )
		logging.debug( 'Initial velocity 1: ({0[0]}, {0[1]}) rot {1}'.format(
			phys1.velocity, phys1.angular_velocity ) )

		friction = sqrt( phys0.friction * phys1.friction )
		restitution = max( phys0.restitution, phys1.restitution )

		dpts0 = [pt - overlap.ents[0].transform().position \
			for pt in overlap.cpts]
		dpts1 = [pt - (overlap.ents[1].transform().position \
			if overlap.ents[1] is not None else \
			Vector3f( overlap.tx*16. + 8., overlap.ty*16. + 8., 0. ))
			for pt in overlap.cpts]

		normal, tangent = -overlap.normal, -overlap.normal.cross([0., 0., 1.])
		dnorm0 = [pt.cross( normal )[2] for pt in dpts0]
		dnorm1 = [pt.cross( normal )[2] for pt in dpts1]
		dtan0 = [pt.cross( tangent )[2] for pt in dpts0]
		dtan1 = [pt.cross( tangent )[2] for pt in dpts1]

		rot0 = [pt.cross([0., 0., 1.]) for pt in dpts0]
		rot1 = [pt.cross([0., 0., 1.]) for pt in dpts1]
		dv = [phys1.velocity + r1 * phys1.angular_velocity -
			phys0.velocity - r0 * phys0.angular_velocity
			for r0, r1 in zip( rot0, rot1 )]

		if len( overlap.cpts ) == 1:
			dpts0 = dpts0[0]
			dpts1 = dpts1[0]

			dnorm0, dnorm1 = dnorm0[0], dnorm1[0]
			dtan0, dtan1 = dtan0[0], dtan1[0]

			normal_mass = (phys0.inv_mass + phys1.inv_mass + 
				phys0.inv_rotational_inertia * dnorm0 * dnorm0 +
				phys1.inv_rotational_inertia * dnorm1 * dnorm1)
			tangent_mass = (phys0.inv_mass + phys1.inv_mass + 
				phys0.inv_rotational_inertia * dtan0 * dtan0 +
				phys1.inv_rotational_inertia * dtan1 * dtan1)

			rot0, rot1 = dpts0.cross([0., 0., 1.]), dpts1.cross([0., 0., 1.])

			dv = dv[0]
			vfinal = 0.
			if dv.length_sq() > 0.05:
				vfinal = -dv.length() * restitution

			dnorm0 = [dnorm0]
			dnorm1 = [dnorm1]
			impulse = [max( ( dv.dot( normal ) - vfinal ) / normal_mass, 0. )]

		elif len( overlap.cpts ) == 2:

			k11 = (phys0.inv_mass + phys1.inv_mass + 
				phys0.inv_rotational_inertia * dnorm0[0] * dnorm0[0] +
				phys1.inv_rotational_inertia * dnorm1[0] * dnorm1[0])
			k22 = (phys0.inv_mass + phys1.inv_mass + 
				phys0.inv_rotational_inertia * dnorm0[1] * dnorm0[1] +
				phys1.inv_rotational_inertia * dnorm1[1] * dnorm1[1])
			k12 = (phys0.inv_mass + phys1.inv_mass + 
				phys0.inv_rotational_inertia * dnorm0[0] * dnorm0[1] +
				phys1.inv_rotational_inertia * dnorm1[0] * dnorm1[1])

			condition = (k11*k22 - k12*k12) 
			if condition / k11 / k11 < 1e-3:
				normal_mass = k11
				dpts0 = dpts0[0]
				dpts1 = dpts1[0]
			
			ik11 = 1. / condition * k22
			ik12 = -1. / condition * k12
			ik22 = 1. / condition * k11

			# For 2D case need to solve for dv - vfinal = k * <impulse>

			vfinal = [-v.length() * restitution if v.length_sq() > 0.5
				else 0. for v in dv]
			dv = [v.dot(normal) for v in dv]

			i0 = ik11 * (dv[0] - vfinal[0]) + ik12 * (dv[1] - vfinal[1])
			i1 = ik12 * (dv[0] - vfinal[0]) + ik22 * (dv[1] - vfinal[1])
			impulse = [i0, i1]

		for imp, dn0, dn1 in zip( impulse, dnorm0, dnorm1 ):
			phys0.velocity += normal * phys0.inv_mass * imp
			phys0.angular_velocity += phys0.inv_rotational_inertia * \
				dn0 * imp
			phys1.velocity -= normal * phys1.inv_mass * imp
			phys1.angular_velocity -= phys1.inv_rotational_inertia * \
				dn1 * imp

		logging.debug( 'Final velocity 0: ({0[0]}, {0[1]}) rot {1}'.format(
			phys0.velocity, phys0.angular_velocity ) )
		logging.debug( 'Final velocity 1: ({0[0]}, {0[1]}) rot {1}'.format(
			phys1.velocity, phys1.angular_velocity ) )


	def trigger( self, overlap ):
		ents = [ e for e in overlap.ents if e is not None ]
		for e in ents:
			if e.has_component( ComponentType.Trigger ):
				trigger = e.get_component( ComponentType.Trigger )
				trigger.triggered = True
				trigger.entity = ents[0] if e is ents[1] else ents[1]

	def end( self ):
		if self.tilemap is None:	
			self.entities = []
			return

		dt = self.timestep
		for e in self.entities:
			self.step_velocity_physics( e, dt )

		for c in self.overlaps.values():
			if not c.trigger_only():
				self.resolve( c )

		self.entity_positions = defaultdict(set)
		for e in self.entities:
			self.step_physics( e, dt )
			self.broad_collide( e )

		simtime, contact, safety = 0., 0, 0
		while contact is not None and safety < 10:
			#TODO store already calculated tois
			toi, contact = 1.0, None
			for o in list( self.overlaps.values() ):
				if not self.collide( o ):
					del self.overlaps[ o.key ]
					continue

				self.trigger( o )
				if not o.trigger_only():
					new_toi = self.toi( o ) 
					if new_toi < toi:
						toi, contact = new_toi, o
			
			if contact is not None:
				for e in contact.ents:
					if e is not None:
						self.advance_physics( e, toi )

				self.resolve( contact )
				for e in contact.ents:
					if e is not None:
						self.step_physics( e, (1.0 - toi)*dt )
						self.broad_collide( e )

			safety += 1

		if safety == 10:
			logging.info( "Too many TOI collisions, safety reached." )
			
		for e in self.entities:
			self.clear_physics( e )
		self.entities = []

	def step_velocity_physics( self, e, dt ):
		if not e.has_component( ComponentType.Physics ):
			return
		phys = e.get_component( ComponentType.Physics )
		phys.velocity += phys.acceleration * dt
		phys.angular_velocity += phys.angular_acceleration * dt

	def step_physics( self, e, dt ):
		if not e.has_component( ComponentType.Physics ):
			return
		transform = e.transform()
		phys = e.get_component( ComponentType.Physics )
		phys.initial_position = Vector3f( transform.position )
		phys.initial_rotation = transform.rotation[2]

		transform.translate( phys.velocity * dt )
		transform.rotate( [0., 0., phys.angular_velocity*dt] )
		phys.current_time = 1.0

		phys.final_position = Vector3f( transform.position )
		phys.final_rotation = transform.rotation[2]

	def advance_physics( self, ent, dt_fraction ):
		if not ent.has_component( ComponentType.Physics ):
			return
		transform = ent.transform()
		phys = ent.get_component( ComponentType.Physics )

		transform.position = (
			phys.initial_position * (1. - dt_fraction) +
			phys.final_position * dt_fraction )
		transform.rotation[2] = (
			phys.initial_rotation * (1. - dt_fraction) +
			phys.final_rotation * dt_fraction )

	def clear_physics( self, ent ):
		if not ent.has_component( ComponentType.Physics ):
			return
		phys = ent.get_component( ComponentType.Physics )
		phys.acceleration = Vector3f(0., 0., 0.)
		phys.angular_acceleration = 0.


