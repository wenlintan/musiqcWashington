import pygame, math
from pygame.locals import *

class vector2:

    def __init__( self, x=0.0, y=0.0 ):
        self.x = float(x)
        self.y = float(y)

    def __neg__( self ):
        return vector2( -self.x, -self.y )

    def __add__( self, other ):
        return vector2( self.x + other.x, self.y + other.y )

    def __sub__( self, other ):
        return vector2( self.x - other.x, self.y - other.y )

    def __mul__( self, scalar ):
        return vector2( self.x * scalar, self.y * scalar )

    def __div__( self, scalar ):
        newscal = 1.0 / scalar
        return self * newscal

    def __eq__( self, other ):
        return ( abs( self.x - other.x ) < 0.0001 and
                 abs( self.y - other.y ) < 0.0001 )

    def __repr__( self ):
        return "[%f, %f]" % (self.x, self.y)

    def dp( self, other ):
        return self.x * other.x + self.y * other.y

    def crossp( self ):
        return vector2( -self.y, self.x )

    def cos( self, other ):
        return self.dp( other ) / ( self.mag() * other.mag() )

    def theta( self, other ):
        return math.acos( self.cos( other ) )

    def norm( self ):
        mag = self.mag()

        if abs(mag) < 0.000001:
            return self
        
        return self / mag

    def mag( self ):
        return math.sqrt( self.x**2 + self.y**2 )

    def mag_squared( self ):
        return self.x**2 + self.y**2

    def _raw( self ):
        return ( self.x, self.y )
    raw = property( _raw )

    
def debug_line( screen, start, end, color=(0,0,255) ):
    pygame.draw.aaline( screen, color, start.raw, end.raw )

def debug_line_pause( *args ):
    debug_line( *args )
    pygame.display.flip()
    s = raw_input("Waiting for you ... <3 -->")

def debug_point( screen, pos, color=(0,0,255) ):
    r = Rect( (pos.x-2, pos.y-2), (4, 4) )
    screen.fill( color, r )

def debug_point_pause( *args ):
    debug_point( *args )
    pygame.display.flip()
    s = raw_input("Waiting for you ... <3 -->")

def debug_pause( ):
    pygame.display.flip()
    s = raw_input("Waiting for you ... <3 -->")
    
    

class point:

    cur_debug_id = 0
    color = (0, 255, 0)
    
    def __init__( self, pos ):
        self.p = pos
        self.divs = []

        self.id = point.cur_debug_id
        point.cur_debug_id += 1

    def _x( self ):
        return self.p.x
    x = property( _x )

    def _y( self ):
        return self.p.y
    y = property( _y )

    def add_dividor( self, div ):
        self.divs.append( div )

    def add_point( self, pt, screen ):

        print "\nAdding id %s from id %s" % (str(pt.id), str(self.id))
        
        newdivs = []
        def make_div( other ):
            to = ray( other.p, pt.p )
            newdiv = dividor( pt, to.bisector(), other )

            newdiv.clipped = False
            pt.add_dividor( newdiv )
            newdivs.append( newdiv )

        print " ".join( [str(x.other(self).id) for x in self.divs] )
        for div in self.divs:
            other = div.other( self )
            make_div( other )
        make_div( self )

        pt.divs = newdivs
        pt.order_dividors()
        newdivs = pt.divs

        if len(newdivs) > 1:
            print " ".join( [ str(x.other(pt).id) for x in newdivs ] )
            for i in range( len(newdivs) ):

                one = newdivs[i]
                two = newdivs[i-1]

                first = one.other( pt )
                second = two.other( pt )

                print "Starting one: %s and two: %s" % (first.id, second.id)

                orig = first.get_div_to( second )
                if orig is None:
                    print "Failed, no original"
                    continue

                inter1 = one.r.inter( orig.r )
                inter2 = two.r.inter( orig.r )

                if (not inter1[0]) or (not inter2[0]) or (not (inter1 == inter2)):
                    print "Intersection failed %s and %s" % (inter1[1], inter2[1])

                    debug_line( screen, one.r.s, one.r.e )
                    debug_line( screen, two.r.s, two.r.e )

                    continue

                inter = inter1[1]

                def notin( div ):
                    if (div.s is first or div.e is first) and (div.s is second or div.e is second):
                        return pt
                    if (div.s is second or div.e is second) and (div.s is pt or div.e is pt):
                        return first
                    return second
    

                for div, third in [ (one,notin(one)), (two,notin(two)), (orig,notin(orig)) ]:

                    print "%s - > %s with %s inbetween" % (div.s.id, div.e.id, third.id)

                    if (div.between - third.p).mag_squared() < (div.between - div.s.p).mag_squared():
                        tothird = third.p - inter
                        if tothird.dp( div.r.d ) > 0:   div.r.e = inter
                        else:                           div.r.s = inter

                    else:
                        tomid = div.between - inter
                        if tomid.dp( div.r.d ) > 0:     div.r.s = inter
                        else:                           div.r.e = inter

                one.clipped = True
                two.clipped = True

                

            newdivs = [ x for x in newdivs if x.clipped ]

        debug_pause()
        pt.divs = newdivs
        
        for div in newdivs:
            div.other( pt ).add_dividor( div )

                

    def process_dividors( self ):

        for i in range( len(self.divs) ):

            pass 
            

    def order_dividors( self ):

        moddiv = [ (self.angle_to_div( div ), div) for div in self.divs ]
        moddiv.sort()
        self.divs = [ div[1] for div in moddiv ]

    def angle_to_div( self, div ):
        other = div.other( self )
        
        to = other.p - self.p
        theta = vector2( 1, 0 ).theta( to )

        #take into account domain of acos
        if other.p.y < self.p.y:
            theta += math.pi

        return theta

    def get_div_to( self, other ):
        for div in self.divs:

            if div.other( self ) is other:
                return div

    def dist_to_sq( self, other ):
        return ( self.p - other.p ).mag_squared()
        

    def draw( self, screen, font ):
        r = Rect( (self.p.x-2, self.p.y-2),  (4, 4) )
        screen.fill( self.color, r )

        for div in self.divs:
            div.draw( screen )

        name = font.render( str(self.id), 1, self.color )
        r = Rect( (self.p.x+2, self.p.y+2), name.get_size() )
        screen.blit( name, r )

class ray:

    color = (255, 0, 0)
    distance_to_extend = 500.0
    
    def __init__( self, start, end ):   
        self.s = start
        self.e = end

    def _length( self ):
        return ( self.e - self.s ).mag()
    l = property( _length )

    def _direct( self ):
        return ( self.e - self.s ).norm()
    d = property( _direct )

    def _unnormed_direct( self ):
        return ( self.e - self.s )
    unnorm_d = property( _unnormed_direct )

    def _mid( self ):
        return self.s + self.d * ( self.l / 2.0 )
    mid = property( _mid )

    def bisector( self ):
        mid = self.s + self.d * ( self.l / 2.0 )
        dir = self.d.crossp()
        return ray( mid + dir * -self.distance_to_extend,
                    mid + dir * self.distance_to_extend )

    def inter( self, other ):
        mydir = self.unnorm_d
        otherdir = other.unnorm_d

        diffy = self.s.y - other.s.y
        diffx = self.s.x - other.s.x

        d = otherdir.y * mydir.x - otherdir.x * mydir.y
        
        if abs(d) < 0.000000001:
            print "Intersection failed: parallel"
            return False, vector2()

        n1 = otherdir.x * ( diffy ) - otherdir.y * ( diffx )
        n2 = mydir.x * diffy - mydir.y * diffx

        s = n1 / d
        t = n2 / d

        if s < -0.001 or s > 1.001 or t < -0.001 or t > 1.001:
            print "Intersection failed: t=%s,  s=%s" % (t,s)
            print "--> %s" % (self.s + mydir * s)
            return False, vector2()

        print "Intersection success: t=%s,  s=%s" % (t,s)
        return True, self.s + mydir * s
        
        

    def draw( self, screen ):
        pygame.draw.aaline( screen, self.color, self.s.raw, self.e.raw )


class dividor:

    def __init__( self, point_start, ray_between, point_end ):
        self.s = point_start
        self.e = point_end
        self.r = ray_between

    def _between( self ):
        return ray( self.s.p, self.e.p ).mid
    between = property( _between )

    def other( self, one ):
        if self.s is one:
            return self.e
        elif self.e is one:
            return self.s
        raise ValueError

    def draw( self, screen ):
        self.r.draw( screen )

class diagram:

    def __init__( self, screen ):
        self.screen = screen
        self.font = pygame.font.Font( None, 14 )
        
        self.divs = []
        self.pts = []

    def add_point( self, position ):

        pt = point( position )
                     
        if self.pts:
            get_dist = lambda x,y: x.dist_to_sq( y )
            dist = [ (get_dist(pt, oldpt), oldpt) for oldpt in self.pts ]

            dist.sort()

            nearest = dist[0][1]
            nearest.add_point( pt, self.screen )
            
        self.pts.append( pt )

    def draw( self ):
        
        for div in self.divs:
            div.draw( self.screen )

        for pt in self.pts:
            pt.draw( self.screen, self.font )

        mousepos = pygame.mouse.get_pos()
        text = self.font.render( "(%s, %s)" % (mousepos[0], mousepos[1]), 1, (255,255,255) )
        self.screen.blit( text, Rect( (0,590), text.get_size() ) )
        
