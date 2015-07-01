
from collections import defaultdict

from flags import *
from simulation import EventSystem, System, Component, Transform, Vector3f

class PyEventSystem( EventSystem ):
	mousex, mousey = 400, 300
	def __init__( self ):
		super( PyEventSystem, self ).__init__()
		self.running = True
		self.keys = defaultdict( bool )

		self.rot = [0., 0., 0.]
		self.trans = Vector3f(0., 0., -1.2)
		self.set_mouse_pos( self.mousex, self.mousey )

	def update( self, ent ):
		if not ent.has_component( ComponentType.MouseControlled ):
			return

		if ent.has_component( ComponentType.Transform ):
			dx, dz = 0., 0.
			move_speed = 0.001 # 0.00001
			if self.keys[ ord('a') ]:	dx = -move_speed
			if self.keys[ ord('d') ]:	dx = move_speed
			if self.keys[ ord('w') ]:	dz = -move_speed
			if self.keys[ ord('s') ]:	dz = move_speed

			t = ent.transform()
			t.translate_relative( Vector3f( dx, 0, dz ) )
			t.rotate( self.rot )

			self.rot = [0., 0., 0.]

			if self.keys[ ord('p') ]:
				t.print_transform()

	def handle_quit( self ):
		self.running = False

	def handle_keyboard( self, key, down ):
		if key == 27:	self.running = False
		self.keys[key] = down

	def handle_mouse_move( self, x, y, dx, dy ):
		# Ignore dx because setting mouse pos generates inverse movement
		self.rot[0] += -0.005 * (self.mousex - x)
		self.rot[1] += -0.005 * (self.mousey - y)
		self.set_mouse_pos( self.mousex, self.mousey )

class FollowComponent( Component ):
	def __init__( self, following, distance ):
		super( FollowComponent, self ).__init__( ComponentType.Follow )
		self.following = following
		self.distance = distance

class FollowSystem( System ):
	def __init__( self ):
		super( FollowSystem, self ).__init__()

	def update( self, ent ):
		if ent.has_component( ComponentType.Follow ):
			follow = ent.get_component( ComponentType.Follow )
			ent.transform().position = follow.following.transform().position
			ent.transform().rotation = follow.following.transform().rotation
			ent.transform().translate_relative( Vector3f( 0, 0, follow.distance ) )
			ent.transform().rotation = -ent.transform().rotation
