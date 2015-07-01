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
        return ( abs( self.x - other.x ) < 0.000001 and
                 abs( self.y - other.y ) < 0.000001 )

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

    def add_dividor( self, div ):
        self.divs.append( div )

    def rem_dividor( self, div ):
        self.divs.remove( div )

    def get_div_to( self, other ):
        for div in self.divs:

            if div.other( self ) is other:
                return div 

    def insert( self, otherpts ):
    
        for other in otherpts:
            to = ray( other.p, self.p )
            newdiv = dividor( self, to.bisector(), other )

            newdiv.clipped = False
            self.add_dividor( newdiv )
        newdivs = self.divs

        if len(newdivs) > 1:
            origs = []

            l = len( newdivs )
            for i,j in [(i,j) for i in range(l) for j in range(l) if i < j]:

                one = newdivs[i]
                two = newdivs[j]

                first = one.other( self )
                second = two.other( self )

                orig = first.get_div_to( second )
                if orig is None:
                    continue
                origs.append( orig )

                inter1 = one.r.inter( orig.r )
                inter2 = two.r.inter( orig.r )

                if (not inter1[0]) or (not inter2[0]) or (not (inter1 == inter2)):
                    continue

                inter = inter1[1]
                for div, third in [ (one,second), (two,first), (orig,self) ]:

                    if ( (div.between - third.p).mag_squared() <
                         (div.between - div.s.p).mag_squared() ):
                        
                        tothird = third.p - inter
                        if tothird.dp( div.r.d ) > 0:   div.r.e = inter
                        else:                           div.r.s = inter

                    else:
                        tomid = div.between - inter
                        if tomid.dp( div.r.d ) > 0:     div.r.s = inter
                        else:                           div.r.e = inter

                # mark these as important
                one.clipped = True
                two.clipped = True
        
            newdivs = [ x for x in newdivs if x.clipped ]

            #check if orig has been made unnecessary
            for orig in origs:

                found = False
                for div in newdivs:

                    ray_to_middle = self.p - div.between
                    ray_to_orig1 = orig.r.s - div.r.s
                    ray_to_orig2 = orig.r.e - div.r.s

                    if ( ray_to_middle.dp( ray_to_orig1 ) < 0 or
                         ray_to_middle.dp( ray_to_orig2 ) < 0 ):

                        found = True
                        break

                if not found:
                    orig.s.rem_dividor( orig )
                    orig.e.rem_dividor( orig )

        
        self.divs = newdivs
        for div in newdivs:
            div.other( self ).add_dividor( div )       

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
    distance_to_extend = 1000.0
    
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
        mid = self.s + self.unnorm_d * ( 1 / 2.0 )
        dir = self.d.crossp()
        return ray( mid + dir * -self.distance_to_extend,
                    mid + dir * self.distance_to_extend )

    def inter( self, other ):
        mydir = self.unnorm_d
        otherdir = other.unnorm_d

        d = otherdir.y * mydir.x - otherdir.x * mydir.y
        
        if abs(d) < 0.000000001:
            return False, vector2()

        diffy = self.s.y - other.s.y
        diffx = self.s.x - other.s.x

        n1 = otherdir.x * ( diffy ) - otherdir.y * ( diffx )
        s = n1 / d

        if s < 0 or s > 1:
            return False, vector2()

        n2 = mydir.x * diffy - mydir.y * diffx
        t = n2 / d

        if t < 0 or t > 1:
            return False, vector2()

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
        return self.s

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
        pt.insert( self.pts )           
        self.pts.append( pt )

    def draw( self ):
        
        for div in self.divs:
            div.draw( self.screen )

        for pt in self.pts:
            pt.draw( self.screen, self.font )

        mousepos = pygame.mouse.get_pos()
        text = self.font.render( "(%s, %s)" % (mousepos[0], mousepos[1]), 1, (255,255,255) )
        self.screen.blit( text, Rect( (0,590), text.get_size() ) )
        
