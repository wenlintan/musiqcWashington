
import pygame
from pygame.locals import *

from scipy import *
from scipy.ndimage import map_coordinates

try:
	from itertools import product
except ImportError:
	def product( *args, **kwds ):
		pools = map(tuple, args) * kwds.get('repeat', 1)
		result = [[]]
		for pool in pools:
			result = [x+[y] for x in result for y in pool]
		for prod in result:
			yield tuple(prod)

class Grid:
	grid_dim = 100
	P, U, V = 0, 1, 2

	def __init__( self ):
		shape = ( self.grid_dim+2, self.grid_dim+2 )
		self.u, self.v = zeros( shape ), zeros( shape )
		self.u_prev, self.v_prev = zeros( shape ), zeros( shape )
		self.p, self.p_prev = zeros( shape ), zeros( shape )
		self.p_src = zeros( shape )

		self.u = 5*ones( (self.grid_dim+2, self.grid_dim+2) )
		#self.fake_flow()

	def fake_flow( self ):
		r = arange( 0, self.grid_dim+2, 1 )
		x, y = meshgrid( r, r )
		d = float( self.grid_dim )
		self.u = -3. * sin( x * 3.14 / d ) * cos( y * 3.14 / d )
		self.v = 3. *cos( x * 3.14 / d ) * sin( y * 3.14 / d )

	def diffuse( self, t, x, x_prev, diff, dt ):
		a = dt*diff*self.grid_dim*self.grid_dim
		for i in range(50):
			d = a*(x[0:-2, 1:-1] + x[2:, 1:-1] + x[1:-1, 0:-2] + x[1:-1, 2:])
			x[1:-1, 1:-1] = (x_prev[1:-1, 1:-1] + d) / (1 + 4*a)
			self.boundaries( t, x )

	def advect( self, typ, p, p_prev, u, v, dt ):
		dt = dt*self.grid_dim
		r = arange( 1, self.grid_dim+1, 1 )
		y, x = meshgrid( r, r )
		x = (x - dt*u[1:-1, 1:-1]).clip( 0.5, self.grid_dim+0.5 )
		y = (y - dt*v[1:-1, 1:-1]).clip( 0.5, self.grid_dim+0.5 )

		i, j = x.astype( int32 ), y.astype( int32 )
		s, t = x - i, y - j
		u, v = 1 - s, 1 - t

		p[1:-1, 1:-1] = \
			u*( v*p_prev[i,j] + s*p_prev[1+i,j] ) + \
			t*( v*p_prev[i,1+j] + s*p_prev[1+i,1+j] )

		self.boundaries( typ, p )

	def boundaries( self, t, p ):
		sign_x = -1 if t == self.U else 1
		sign_y = -1 if t == self.V else 1

		rx, ry = 40, 20
		dx, dy = 10, 4
		p[rx-dx, ry-dy:ry+dy] = sign_x * p[rx-dx-1, ry-dy:ry+dy]
		p[rx+dx, ry-dy:ry+dy] = sign_x * p[rx+dx+1, ry-dy:ry+dy]
		p[rx-dx:rx+dx, ry-dy] = sign_y * p[rx-dx:rx+dx, ry-dy-1]
		p[rx-dx:rx+dx, ry+dy] = sign_y * p[rx-dx:rx+dx, ry+dy+1]

		p[rx-dx, ry-dy] = 0.5*( p[rx-dx, ry-dy+1] + p[rx-dx+1, ry-dy] )
		p[rx-dx, ry+dy] = 0.5*( p[rx-dx, ry+dy-1] + p[rx-dx+1, ry+dy] )
		p[rx+dx, ry-dy] = 0.5*( p[rx+dx, ry-dy+1] + p[rx+dx-1, ry-dy] )
		p[rx+dx, ry+dy] = 0.5*( p[rx+dx, ry+dy-1] + p[rx+dx-1, ry+dy] )
		p[rx-dx+1:rx+dx-1, ry-dy+1:ry+dy-1] = 0

		d = self.grid_dim
		p[0, 1:-1] = sign_x * p[1, 1:-1]
		p[self.grid_dim+1, 1:-1] = sign_x * p[self.grid_dim, 1:-1]
		if t == self.U:
			p[0, 1:-1] = 5*ones(self.grid_dim)
			p[self.grid_dim+1, 1:-1] = 5*ones(self.grid_dim)

		p[1:-1, 0] = sign_y * p[1:-1, 1]
		p[1:-1, self.grid_dim+1] = sign_y * p[1:-1, self.grid_dim]

		p[0, 0] = 0.5*(p[1, 0] + p[0, 1])
		p[0, d+1] = 0.5*(p[1, d+1] + p[0, d])
		p[d+1, 0] = 0.5*(p[d, 0] + p[d+1, 1])
		p[d+1, d+1] = 0.5*(p[d, d+1] + p[d+1, d])

	def project( self, u, v ):
		p = zeros( (self.grid_dim+2, self.grid_dim+2) )
		div = zeros( (self.grid_dim+2, self.grid_dim+2) )
		h = 1. / self.grid_dim

		div[1:-1, 1:-1] = -0.5*h*(u[2:, 1:-1] - u[:-2, 1:-1] + \
				v[1:-1, 2:] - v[1:-1, :-2])
		self.boundaries( self.P, div )

		for i in range( 20 ):
			p[1:-1, 1:-1] = ( div[1:-1, 1:-1] + p[:-2, 1:-1] + p[2:, 1:-1] + \
					p[1:-1, :-2] + p[1:-1, 2:] ) / 4
			self.boundaries( self.P, p )

		u[1:-1, 1:-1] -= 0.5*( p[2:, 1:-1] - p[:-2, 1:-1] ) / h
		v[1:-1, 1:-1] -= 0.5*( p[1:-1, 2:] - p[1:-1, :-2] ) / h
		self.boundaries( self.U, u )
		self.boundaries( self.V, v )

	def p_step( self, dt ):
		self.p += self.p_src
		self.p, self.p_prev = self.p_prev, self.p
		self.diffuse( self.P, self.p, self.p_prev, 0.001, dt )

		self.p, self.p_prev = self.p_prev, self.p
		self.advect( self.P, self.p, self.p_prev, self.u, self.v, dt )

	def vel_step( self, dt ):
		self.u, self.u_prev = self.u_prev, self.u
		self.v, self.v_prev = self.v_prev, self.v
		self.diffuse( self.U, self.u, self.u_prev, 5, dt )
		self.diffuse( self.V, self.v, self.v_prev, 5, dt )
		self.project( self.u, self.v )

		self.u, self.u_prev = self.u_prev, self.u
		self.v, self.v_prev = self.v_prev, self.v
		self.advect( self.U, self.u, self.u_prev, self.u_prev, self.v_prev, dt )
		self.advect( self.V, self.v, self.v_prev, self.u_prev, self.v_prev, dt )
		self.project( self.u, self.v )

	def step( self, dt ):
		self.p_step( dt )
		self.vel_step( dt )

	def add_source( self, x, y ):
		self.p_src[ int(x)+1, int(y)+1 ] += 500.

if __name__ == "__main__":
	pygame.init()
	width, height = 1000, 1000
	screen = pygame.display.set_mode( (width,height), 0, 24 )
	screen.fill( (0,0,0) )

	g = Grid()
	running = True
	mouse_down = False
	while running:
		g.step( 0.01 )
		if mouse_down:
			x, y = pygame.mouse.get_pos()
			x, y = float( x ), float( y )
			g.add_source( x * g.grid_dim / width, y * g.grid_dim / height )
		#poll input
		event = pygame.event.poll()
		while event.type != pygame.NOEVENT:
			if event.type == pygame.QUIT:
				running = False
			elif event.type == MOUSEBUTTONDOWN:
				mouse_down = True
			elif event.type == MOUSEBUTTONUP:
				mouse_down = False
			elif event.type == KEYDOWN:
				pass
			event = pygame.event.poll()

		screen.fill( (0,0,0) )
		for i, j in product( range(1, g.grid_dim+1), repeat=2 ):
			x, y = (i-0.5) * width / g.grid_dim, (j-0.5) * height / g.grid_dim
			d = float(width) / g.grid_dim / 2
			r = Rect( x - d, y - d, d*2, d*2 )
			c = g.p[ i, j ] / 40.
			c = max( 0., min( 1., c ) )
			pygame.draw.rect( screen, (0, int(255 * c), 0), r )

		for i, j in product( range(1, g.grid_dim+1), repeat=2 ):
			u, v = g.u[ i, j ]*8, g.v[ i, j ]*8
			x, y = (i-0.5) * width / g.grid_dim , (j-0.5) * height / g.grid_dim
			pygame.draw.line( screen, (255,0,0), (x, y), (x+u, y+v) )

		pygame.display.flip()
