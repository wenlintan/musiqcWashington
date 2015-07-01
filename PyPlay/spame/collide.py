

class collider:
    def __init__( self, one, two, dt, others ):
        self.one = one
        self.two = two
        
        self.full_time = dt
        self.others = others

    def update( self, dt ):
        pass

    def rectify_function( self, shape, obj, oshape, other ):
        
        def rectify( stage, t, pos, vel, others ):
            
            f = af( stage, vel, pos )
            

            for obj in others:
                info = obj.intersection_info( pos )
                
        return accel

    def integrate_rk4_multibody( self, bodies, accel_fn, dt ):

        xs = [ x for b in bodies for x in b.verts ]
        k1 = [ v for b in bodies for v in b.vels ]
        n = len( xs )

        accels = [ accel_fn( 0, k1[i], xs[i] ) for i in range( n ) ]
        

        
        

    def intersect( self ):

        oxs = self.one.verts
        onxs = self.one.newverts
        onvs = self.one.newvels

        #actually need to back up segment that vertex is colliding with too
        hits = [ i for (i,v) in enumerate(onxs) if self.two.contains( v ) ]
        ts = [ self.two.intersection( ons[i], onxs[i] )[1] for i in hits ]

        # have found t where objects first intersect
        # revert back to this time
        t = min( ts )
        self.one.step( t )
        self.two.step( t )

        self.time_left = self.full_time - t
        
            

    resolve_epsilon_sq = 0.0000000001
    def resolve( self, other, vert ):
        print "resolve"
        direct = self.vels[ vert ].norm()

        end = self.verts[ vert ]
        start = end - direct

        while other.contains( start, True ):
            end = start
            start = start - direct

        if not other.contains( end ) or other.contains( start ):
            return self.verts[ vert ]

        while ( end - start ).mag_squared() > collider.resolve_epsilon_sq:
            #print "loop"
            mid = start + ( end - start ) / 2.
            if other.contains( mid ):   end = mid
            else:                       start = mid

        t, v1, v2 = other.intersection( start )
        if t == -1.0:
            print "ERROR: Collision found, but no incident point calculated."
            sys.exit(-1)
        
        n = ( other.verts[ v2 ] - other.verts[ v1 ] ).crossp().norm()
        if n.dp( other.ave ) > 0.0: n = -n
        
        response = n * self.forces[ vert ].dp( n )
        self.forces[ vert ] += response

        other.apply_force( -response, t, v1, v2 )
        return start
