#!/usr/bin/env python
import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo

import numpy as np
import sys

if len(sys.argv) < 3:
	print( "usage: ", sys.argv[0], " <datafile> <trifile>" )
	sys.exit(0)

data = np.genfromtxt( sys.argv[1], delimiter=' ', dtype=np.float32 )
tris = np.genfromtxt( sys.argv[2], delimiter=' ', dtype=np.uint32 )

pygame.display.init()
screen = pygame.display.set_mode( (500, 500), HWSURFACE|OPENGL|DOUBLEBUF )

verts = data[:, :3]
min_charge, max_charge = -0.03, 0.03 
#min_charge, max_charge = min( data[:,3] ), max( data[:,3] )*0.5

print( "Building colors." )
colors = np.zeros( (len(verts), 3), dtype=np.uint8 )
for i in range( len(verts) ):
	if data[i,3] < 0.:	
		colors[i,2] = min( 255, int(255*data[i,3]/min_charge) )
	elif data[i,3] == 0:
		colors[i,1] = 255
	else: 
		colors[i,0] = min( 255, int(255*data[i,3]/max_charge) )

indices = tris.flatten()

glDisable( GL_CULL_FACE )
glEnable( GL_DEPTH_TEST )
glPolygonMode( GL_FRONT_AND_BACK, GL_LINE )

glMatrixMode( GL_PROJECTION )
gluPerspective( 90, 1., 1., 100000 )

#pos = [ 20000., 0., 20000. ]
pos = [ 0., 0., 200. ]
look = [ 0., 0., 0. ]
pos = [120*100/9., 100*100/9., 200.]
look = [120*100/9., 100*100/9., 0.]
move_step = [ 1., 0., 1. ]
while True:
	for event in pygame.event.get():
		if event.type == QUIT:
			sys.exit(0)

	glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

	glMatrixMode( GL_MODELVIEW )
	glLoadIdentity()
	gluLookAt( pos[0], pos[1], pos[2], look[0], look[1], look[2], 0., 1., 0. )

	pressed = pygame.key.get_pressed()
	if pressed[K_LEFT]:		pos[0] += move_step[0]
	if pressed[K_RIGHT]:	pos[0] += -move_step[0]
	if pressed[K_UP]:		pos[2] += move_step[2]
	if pressed[K_DOWN]:		pos[2] += -move_step[2]
	look[0] = pos[0]
	look[2] = pos[2] - 200.

	glEnableClientState( GL_VERTEX_ARRAY )
	glVertexPointer( 3, GL_FLOAT, 0, verts )

	glEnableClientState( GL_COLOR_ARRAY )
	glColorPointer( 3, GL_UNSIGNED_BYTE, 0, colors )

	glDrawElements( GL_TRIANGLES, len(indices), 
		GL_UNSIGNED_INT, indices )

	pygame.display.flip()
