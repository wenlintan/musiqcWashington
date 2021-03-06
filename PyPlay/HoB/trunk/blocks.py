#!/usr/bin/env python

import pdb

from renderer import *
from draws import Block

from world import *
from weapons import *
from system import *
from event_handler import *

r = Renderer( 800, 600 )
r.perspective( 75., .1, 1000. )

system = ClientEntitySystem()
TrackedEntity.tracker = system

#world = World()
#system.append( world )

char = Character( numpy.array((0., .1, 0.)), numpy.array((0., 0., 0.)) )
w = TestWeapon( TestProjectile )
char.equip( w )

handler = MainEventHandler()
player = Player( char, handler ) # Player( char, handler )

event = pygame.event.poll()
while event.type not in ( NOEVENT, QUIT ):
	event = pygame.event.poll()

last_time = pygame.time.get_ticks()
while event.type != QUIT:
	event = pygame.event.poll()
	while event.type not in ( NOEVENT, QUIT ):
		handler.handle_event( event )
		event = pygame.event.poll()

	t = pygame.time.get_ticks()
	dt, last_time = t - last_time, t

	r.begin_frame()
	system.update( dt / 1000. )

	c = char.follow_camera( Camera )
	c.update( r )
	system.draw()
	r.end_frame()


