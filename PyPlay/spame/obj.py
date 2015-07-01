import copy, sys, pdb

from vector import *

import draw
from collide import collider

class state:
    def __init__( self, n ):
        self.n = n

    def assign( self, verts, shape, vels, center, vel ):
        self.verts = copy.copy( verts )
        self.shape = copy.copy( shape )

        self.vels = copy.copy( vels )

        self.center = copy.copy( center )
        self.vel = copy.copy( vel )
        return self

class base:
    timestep = 1.0 / 30.0
    def __init__( self, vertices ):

        self.n = len( vertices )
        vels = [ vector2() ] * self.n
        center = sum( vertices, vector2() ) / self.n
        
        s = state( self.n )
        s.assign( vertices, vertices, vels, center, vector2() )
        self.states = [ s ]

        self.stages = 4
        self.forces = [ vector2() ] * self.stages
        
        self.restitution = 1.0
        self.elasticity = 1.0
        self.drag = 0.0

    verts = property( lambda s: s.states[ 0 ].verts )
    shape = property( lambda s: s.states[ 0 ].shape )
    vels = property( lambda s: s.states[ 0 ].vels )
    center = property( lambda s: s.states[ 0 ].center )
    vel = property( lambda s: s.states[ 0 ].vel )   

    def add_state( self, x, s, v, center, vel ):
        st = state( self.n )
        st.assign( x, s, v, center, vel )
        self.states.insert( 0, st )

    def average_vertices( self ):
        return sum( self.verts, vector2() ) / self.n
    ave = property( average_vertices )

    def create_draw( self, filled ):
        if filled:  self.draw = draw.filled_mesh( self.verts )
        else:       self.draw = draw.mesh( self.verts )

    def set_velocity( self, v ):
        self.states[0].vels = [ v ] * self.n
        self.states[0].vel = v

    def stage1( self, others ):
        # reset forces so they can accumulate correctly
        self.forces = [ vector2() ] * self.stages

    def stage2( self, others ):
        # step the simulation initally
        self.step( base.timestep )

    def stage3( self, others ):
        # handle any collisions, passing off to collider
        [ self.collide( o, others ) for o in others if o is not self ]

    def stage4( self, others ):
        # remove the old data
        self.states = self.states[ :1 ]
        self.draw.set_vertices( self.verts )
    update = [ stage1, stage2, stage3, stage4 ]

    def step( self, dt, integrate = None ):

        if integrate is None:
            integrate = self.integrate_rk4
            
        xs = self.verts
        ss = self.shape
        vs = self.vels
        af = self.accel_function
        
        data = [ integrate( xs[i], vs[i], af( ss[ i ] ), dt )
                 for i in range( self.n ) ]
        
        x = [ d[0] for d in data ]
        v = [ d[1] for d in data ]

        a_t = self.total_accel_function()
        s = [ integrate( ss[i], self.vel, a_t, dt )[0]
              for i in range( self.n ) ]

        center, vel = integrate( self.center, self.vel, a_t, dt )
        self.add_state( x, s, v, center, vel )

    def accel_function( self, goal ):

        def accel( stage, t, pos, vel ):
            restit = ( goal - pos ) * self.restitution
            damp = self.drag * vel.dp( vel )
            damp = -vel * damp

            self.forces[ stage ] += restit + damp
            return restit + damp
        return accel

    def total_accel_function( self ):

        def accel( stage, t, pos, vel ):
            return self.forces[ stage ] / self.n
        return accel

    def integrate_rk4( self, x, v, accel, dt ):

        # pdb.set_trace()
        hdt = dt / 2.0
        dx1, dv1 = v          , accel( 0, 0.0, x,           v           )
        dx2, dv2 = v + dv1*hdt, accel( 1, hdt, x + dx1*hdt, v + dv1*hdt )
        dx3, dv3 = v + dv2*hdt, accel( 2, hdt, x + dx2*hdt, v + dv2*hdt )
        dx4, dv4 = v + dv3* dt, accel( 3, dt , x + dx3* dt, v + dv3* dt )

        dx = ( dx1 + dx2*2 + dx3*2 + dx4 ) / 6.0
        dv = ( dv1 + dv2*2 + dv3*2 + dv4 ) / 6.0
        return x + dx * dt, v + dv * dt


    def collide( self, o, others ):
        if not self.basic_collide( o ):
            return
        
        for (i,v) in enumerate( self.verts ):
            
            if o.contains( v ):
                pass # c = collider( self, o, others )

    def basic_collide( self, o ):
        "Check for collisions between bounding circles to avoid complicated test."
        return True

    def normal( self, i ):

        xs = self.verts
        seg = xs[ i+1 ] - xs[ i ]

        if seg.crossp( self.center - xs[ i ] ) < 0.0:
            return -seg.crossz()
        return seg.crossz()

    def contains( self, vert, talk = False ):

        xs = self.verts
        for i in range( -1, len( self.verts )-1 ):
                
            seg = xs[ i+1 ] - xs[ i ]
            pt = vert - xs[ i ]

            if seg.crossp( pt ) < 0.0:
                return False

        print "contains"
        return True

    inter_epsilon = 0.0001
    def intersection( self, start, stop ):

        xs = self.verts
        r = ray2( start, stop )
        
        for i in range( -1, len( self.verts )-1 ):
            edge = ray2(  xs[i], xs[i+1] )
            
            hit, t, v = r.collide( edge )
            if hit: return True, t, v

        return False, 0.0, vector2()
    
    def intersection_info( self, vert ):

        xs = self.verts
        for i in range( -1, len( self.verts )-1 ):
                
            seg = xs[ i+1 ] - xs[ i ]
            pt = vert - xs[ i ]

            if abs( seg.crossp( pt ) ) < base.inter_epsilon:

                t = min( pt.component_div(-seg).raw )
                if t >= (0.0-base.inter_epsilon) and t <= (1.0+base.inter_epsilon):
                    return t, i, i+1
            
        return -1, 0, 0
    
        

    
        
    
    
            
            
            

        
