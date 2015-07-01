
from pygame.locals import *

import struct
from collections import defaultdict

from weapons import TrackedEntity
from simulation import State, CollGeometry

class PlayerEventHandler( State ):
	def __init__( self, char ):
		super( PlayerEventHandler, self ).__init__()

		self.character = char
		self.trans = [0, 0]
		self.rotate = [0, 0]
		self.past_rotation = [ self.rotate ]*5
		self.firing = self.fired = False

		self.keys = defaultdict( lambda: False )

		self.handler = {}
		self.handler[ KEYDOWN ] = lambda ev: self.key( ev, True )
		self.handler[ KEYUP ] = lambda ev: self.key( ev, False )

		self.handler[ MOUSEMOTION ] = self.mouse_motion
		self.handler[ MOUSEBUTTONDOWN ] = lambda ev: self.mouse( ev, True )
		self.handler[ MOUSEBUTTONUP ] = lambda ev: self.mouse( ev, False )

	def handle_event( self, event ):
		if event.type in self.handler:
			return self.handler[ event.type ]( event )
		return False

	def update( self ):
		forward, strafe = 0., 0.
		forward += 2.5 if self.keys[ K_w ] else 0.
		forward -= 2.5 if self.keys[ K_s ] else 0.
		strafe -= 2.5 if self.keys[ K_a ] else 0.
		strafe += 2.5 if self.keys[ K_d ] else 0.

		self.past_rotation = self.past_rotation[:4]
		self.past_rotation.append( self.rotate )
		self.rotate, cur_rot = [0, 0], self.rotate

		if not self.character:
			return

		self.character.move( forward, strafe )
		if self.keys[ K_SPACE ]:
			self.character.jump()

		self.angles = \
			self.character.look( cur_rot[1]*0.01, -cur_rot[0]*0.01 )[:2]

		if self.firing:
			spinx, spiny = 0., 0.
			for x, y in self.past_rotation:
				spinx, spiny = spinx + x, spiny + y
			self.character.fire( (spiny / 5., -spinx / 5.) )

	def serialize( self ):
		data, buttons = '', 0
		data += struct.pack( '!ff', *self.angles )
		
		if self.firing:		buttons |= 1
		for (i, k) in enumerate( (K_w, K_s, K_a, K_d, K_SPACE) ):
			if self.keys[ k ]:
				buttons |= 1 << i

		if self.firing or self.fired:
			buttons |= 1 << 5
		self.fired = False

		data += struct.pack( '!B', buttons )
		return data

	def deserialize( self, data ):
		self.angles = struct.unpack( '!ff', data[:8] )
		self.rotate = (self.angles - self.character.cstate.look[:2]) / 0.01
		self.rotate[0], self.rotate[1] = -self.rotate[1], self.rotate[0]
		keys, = struct.unpack( '!B', data[8] )

		for (k, v) in enumerate( (K_w, K_s, K_a, K_d, K_SPACE) ):
			self.keys[ v ] = bool( keys & (1 << k) ) 
		self.firing = keys & (1 << 5)
		return data[9:]

	def key( self, event, down ):
		if event.key == K_ESCAPE:
			raise ValueError( "Escape key pressed." )

		self.keys[ event.key ] = down
		return True

	def mouse_motion( self, event ):
		self.rotate = event.rel
		return True
		
	def mouse( self, event, down ):
		self.firing = down
		if down:
			self.fired = True
		return True

class Player( TrackedEntity ):
	client_sendable = updatable = True
	def __init__( self, char, handler ):
		super( Player, self ).__init__()
		self.ev_state = PlayerEventHandler( char )
		self.coll = CollGeometry()

		self.char = char
		if handler:
			handler.push( self.ev_state )

	def update( self, dt ):
		self.ev_state.update()

	def collision_geometry( self ):
		return self.coll

	def state( self ):
		return self.ev_state

