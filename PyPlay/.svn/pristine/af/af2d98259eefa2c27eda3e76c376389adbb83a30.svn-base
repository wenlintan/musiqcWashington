
import numpy, struct

from simulation import State, Entity
from simulation import CollGeometry, CollAABB, CollState, Vector3f

from draws import Block

class TrackedEntity( Entity ):
	server_sendable = client_sendable = drawable = \
		batchable = collidable = updatable = False
	
	def __init__( self ):
		self.tracker.append( self )

class TestProjectile( Block, TrackedEntity ):
	collidable = batchable = updatable = True

	muzzle_velocity = 10
	mass = 0.2
	curve_effect = 10

	def __init__( self, pos, look, spin, damage ):
		TrackedEntity.__init__( self )
		Block.__init__( self, pos[0], pos[1], pos[2], 0.2 )
		self.set_color( (150, 150, 0, 0) )

		self.pos, self.spin = pos, spin
		self.vel = look * self.muzzle_velocity
		self.damage = damage

		self.coll = CollGeometry()
		self.coll.add_geometry( CollAABB( Vector3f(), Vector3f(.1, .1, .1) ) )

	def update( self, dt ):
		self.pos += self.vel * dt
		self.vel += numpy.array((0., -9.8, 0.)) * self.mass * dt
		self.vel += self.spin * self.curve_effect * dt
		self.x, self.y, self.z = self.pos

	def collision_geometry( self ):
		return self.coll.state( CollState( Vector3f( *self.pos ) ) )
		
	def resolve( self, other, coll ):
		if False and hasattr( other, 'damage' ):
			other.damage( self.damage )
		self.vel = -self.vel

class TestWeapon( TrackedEntity ):
	updatable = True
	def __init__( self, proj ):
		super( TestWeapon, self ).__init__()
		self.projectile = proj
		self.coll = CollGeometry()

		self.reload_time = 0.4
		self.fire_time = 0.

	def collision_geometry( self ):
		return self.coll

	def resolve( self, other, coll ):
		pass

	def update( self, dt ):
		self.fire_time += dt

	def fire( self, pos, look, spin ):
		if self.fire_time > self.reload_time:
			p = self.projectile( pos, look, spin, 100 )
			self.fire_time = 0.

class CharacterState( State ):
	pos_bit = 		1 << 0
	look_bit = 		1 << 1
	health_bit = 	1 << 2
	weapon_bit = 	1 << 3
	flag_bits = 	(pos_bit, look_bit, health_bit, weapon_bit)

	def __init__( self, pos, look ):
		super( CharacterState, self ).__init__( )

		self.pos = pos
		self.look = look
		self.health = 100
		self.weapon = None

	def _data( self ):
		return (self.pos, self.look, self.health, self.weapon)

	def serialize( self, prev = None ):
		data, flags = '', 0

		if prev is None or self.pos != prev.pos:
			flags |= self.pos_bit
			data += struct.pack( '!fff', *self.pos )

		p = int(self.look[0] / numpy.pi * 250.) + 125
		y = int(self.look[1] / numpy.pi * 125.)
		if not prev or numpy.array((p, y)) != prev.look:
			flags |= self.look_bit
			data += struct.pack( '!BB', p, y )

		if not prev or self.health != prev.health:
			flags |= self.health_bit
			data += struct.pack( '!B', self.health )

		return struct.pack( '!B', flags ) + data

	def deserialize( self, data ):
		(flags, ), data = struct.unpack( '!B', data[:1] ), data[1:]
		if flags & self.pos_bit:
			self.pos, data = struct.unpack( '!fff', data[:12] ), data[12:]

		if flags & self.look_bit:
			l, data = struct.unpack( '!BB', data[:2] ), data[2:]
			p = (l[0] - 125) * numpy.pi / 250.
			y = l[1] * numpy.pi / 125.
			self.look = (p, y)

		if flags & self.health_bit:
			self.health, data = struct.unpack( '!B', data[:1] ), data[1:]
		return data

class Character( Block, TrackedEntity ):
	server_sendable = True
	collidable = updatable = batchable = True
	def __init__( self, pos, angles ):
		TrackedEntity.__init__( self )
		Block.__init__( self, pos[0], pos[1], pos[2], 0.1 )
		self.set_color( (0, 0, 100, 0) )

		pos, angles = numpy.array(pos), numpy.array(angles)
		self.vel = numpy.array((0., 0., 0.))
		self.grounded = False

		self.cstate = CharacterState( pos, angles )

		self.coll = CollGeometry()
		self.coll.add_geometry( CollAABB( Vector3f(), Vector3f(.1, .1, .1) ) )

	def _build_view_frame( self ):
		v = numpy.array((0., 0., 1.))
		pitch, yaw, roll = self.cstate.look

		sy, cy = numpy.sin( yaw ), numpy.cos( yaw )
		roty = numpy.array(((cy, 0., sy), (0., 1., 0.), (-sy, 0., cy)))

		sx, cx = numpy.sin( pitch ), numpy.cos( pitch )
		rotx = numpy.array(((1., 0., 0.), (0., cx, -sx), (0., sx, cx)))
		
		look = numpy.dot( roty, numpy.dot( rotx, v ) )
		up = numpy.array((0., 1., 0.))
		right = numpy.cross( look, up )
		up = numpy.cross( right, look )

		right = right / numpy.linalg.norm( right )
		up = up / numpy.linalg.norm( up )
		return look, up, right

	def update( self, dt ):
		self.cstate.pos += self.vel * dt
		if not self.grounded:
			self.vel += numpy.array((0., -9.8, 0.)) * dt
		self.x, self.y, self.z = self.cstate.pos

	def equip( self, w ):
		self.cstate.weapon = w

	def jump( self ):
		if self.grounded:
			self.vel += numpy.array((0., 12., 0.))
			self.grounded = False

	def fire( self, spin ):
		look, up, right = self._build_view_frame()
		spin = -right * spin[1] - up * spin[0]
		self.cstate.weapon.fire( self.cstate.pos.copy(), look, spin )

	def move( self, forward, strafe ):
		pitch, yaw, roll = self.cstate.look
		sy, cy = numpy.sin( yaw ), numpy.cos( yaw )
		roty = numpy.array(((cy, 0., sy), (0., 1., 0.), (-sy, 0., cy)))

		look = numpy.dot( roty, numpy.array((0., 0., 1.)) )
		right = numpy.dot( roty, numpy.array((-1., 0., 0.)) )
		horiz = forward * look + strafe * right

		up = numpy.array((0., 1., 0.))
		vert = up * numpy.dot( self.vel, up )
		self.vel = horiz + vert
		return self.vel

	def look( self, pitch, yaw ):
		angles = self.cstate.look + numpy.array((pitch, yaw, 0.))
		angles[0] = max( -numpy.pi/2.4, min( numpy.pi/2.4, angles[0] ) )
		
		if angles[1] > 2*numpy.pi:
			angles[1] -= 2*numpy.pi
		elif angles[1] < 0.:
			angles[1] += 2*numpy.pi

		self.cstate.look = angles
		return angles

	def follow_camera( self, camera ):
		look, up, right = self._build_view_frame()
		return camera( self.cstate.pos - look, look, up )

	def state( self ):
		return self.cstate

	def collision_geometry( self ):
		return self.coll.state( CollState( Vector3f( *self.cstate.pos ) ) )

	def resolve( self, other, coll ):
		if coll.normal.dot( Vector3f(*self.vel) ) > 0.:
			coll.normal = -coll.normal
			coll.offset = -coll.offset

		#coll.offset *= 1.0001
		self.cstate.pos += numpy.array((coll.offset[0], coll.offset[1], 
			coll.offset[2]));

		if abs(coll.normal[1]) > 0.99:
			self.vel[1] = 0.
			self.cstate.pos[1] += 0.001
			self.grounded = True
		else:
			dv = coll.normal * -2. * coll.normal.dot( Vector3f(*self.vel) )
			self.vel += numpy.array((dv[0], dv[1], dv[2])) 


