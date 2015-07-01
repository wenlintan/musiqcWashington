
from scipy import cos, sin, arange, pi


from itertools import combinations

#Debug utilities, unnecessary after debugging complete
import pdb
from scipy import random

from mpl_toolkits.mplot3d import axes3d
from matplotlib.pyplot import *
from matplotlib.collections import PolyCollection

from vector import *

class Delaunay:
    def __init__( self, points ):
        self.original_points = points
        p = sorted([ (point, i) for i, point in enumerate(points) ])
        
        self.mapping = dict([(i, point[1]) for i, point in enumerate(p)])
        self.points = [Point2(*point[0]) for point in p]
        
        self.n = len(points)
        edges, _, _ = self.divide( 0, self.n )
##        print edges

        self.edges = {}
        transform = lambda x: self.mapping[ x ]
        for k, v in edges.items():
            self.edges[ transform(k) ] = map( transform, v )

    def in_cirumcircle( self, a, b, c, test ):
        ax, ay = self.points[a].data;     bx, by = self.points[b].data
        cx, cy = self.points[c].data;     dx, dy = self.points[test].data

        m00, m01, m02 = [ ax-dx, ay-dy, (ax**2-dx**2) + (ay**2-dy**2) ]
        m10, m11, m12 = [ bx-dx, by-dy, (bx**2-dx**2) + (by**2-dy**2) ]
        m20, m21, m22 = [ cx-dx, cy-dy, (cx**2-dx**2) + (cy**2-dy**2) ]
##        self.inc = ( m00 * (m11*m22 - m12*m21) -
##                 m01 * (m10*m22 - m12*m20) +
##                 m02 * (m10*m21 - m11*m20) )
        return ( m00 * (m11*m22 - m12*m21) -
                 m01 * (m10*m22 - m12*m20) +
                 m02 * (m10*m21 - m11*m20) ) >= 0

    def opp( self, edge, v ):
        if edge[0] == v:    return edge[1]
        if edge[1] == v:    return edge[0]
        raise ValueError( "v not element of edge" )

    def ray( self, edge ):
        return self.points[ edge[1] ] - self.points[ edge[0] ]

    def lower_tangent( self, ledges, r_cw_l, redges, l_ccw_r ):
        def skip( edges, e, fn ):
            base = e[ 1 ]
            base_edges = edges[ base ]
            e_index = base_edges.index( e[ 0 ] )
            new_index = fn(e_index) % len( base_edges )
            return base, base_edges[ new_index ]
        
        while True:
            connect = self.ray( (r_cw_l[0], l_ccw_r[0]) )
            if self.ray( r_cw_l ).cross( connect ) > 0:
                r_cw_l = skip( ledges, r_cw_l, lambda x: x+1 )
                
            elif self.ray( l_ccw_r ).cross( -connect ) < 0:
                l_ccw_r = skip( redges, l_ccw_r, lambda x: x-1 )
                
            else:   break

        return r_cw_l, l_ccw_r

    def find_candid( self, edges, base_edge, base, off ):
        base_edges = edges[ base ]
        opp = self.opp( base_edge, base )
        l = len( base_edges )

        i = base_edges.index( opp )
        def next_cand( index ):
            l = len( base_edges )
            return base_edges[ (index+off) % l ], (index+off) % l
        
        cand, i = next_cand( i )
        if self.ray( base_edge ).cross( self.ray((base, cand)) ) <= 0:
            return -1
        
        ncand, i = next_cand( i )
        left, right = base_edge
        while all([ cand != ncand,
                    self.in_cirumcircle( left, right, cand, ncand ),
                    self.ray( base_edge ).cross( self.ray((base, ncand)) ) > 0
                    ]):
                  
            cand_edges = edges[ cand ]
            del cand_edges[ cand_edges.index( base ) ]
            base_index = base_edges.index( cand )
            del base_edges[ base_index ]

            if i > base_index:
##                i -= off
                i -= 1
            cand = ncand
            ncand, i = next_cand( i )

        if opp in edges[ cand ]:
            pdb.set_trace()
        return cand

    def insert_edge( self, ledges, redges, edge, l_next_cw, r_next_ccw ):
        l, r = edge
        insert_index = ledges[ l ].index( l_next_cw )
        ledges[ l ].insert( insert_index, r )

        insert_index = redges[ r ].index( r_next_ccw )
        redges[ r ].insert( insert_index+1, l )
                                    
    def divide( self, l, r, check = False ):
        n = r - l
        if n == 2:
            r = r-1
            return {l:[r], r:[l]}, (l,r), (r, l)

        if n == 3:
            a, b, c = self.points[l:r]
            r = r-1
            
            cp = (b-a).cross(c-a)
            if cp > 0:
                return {l:[r, l+1], l+1:[l, r], r:[l+1, l]}, (l,l+1), (r,l+1)
            elif cp < 0:
                return {l:[l+1, r], l+1:[r, l], r:[l, l+1]}, (l,r), (r,l)
            else:
                return {l:[l+1], l+1:[r, l], r:[l+1]}, (l,l+1), (r,l+1)

        split = (l + r) / 2
        ledges, l_ccw_l, r_cw_l = self.divide( l, split )
        redges, l_ccw_r, r_cw_r = self.divide( split, r )
##        print "Combining:", ledges, redges
##        print "Edges:", l_ccw_l, r_cw_l, l_ccw_r, r_cw_r

##        if 18 in range(l, r):
##            pdb.set_trace()
        l_lower, r_lower = self.lower_tangent( ledges, r_cw_l, redges, l_ccw_r )
        base = (l_lower[0], r_lower[0])

        if l_lower[0] == l:
            l_ccw_l = (l_lower[0], r_lower[0])
        if r_lower[0] == r-1:
            r_cw_r = (r_lower[0], l_lower[0])

##        print l_lower, r_lower
        self.insert_edge( ledges, redges, base, l_lower[1], r_lower[1] )
        lbase, rbase = base
        
        while True:
            base = (lbase, rbase)
##            print "Base:", base
##            print "New Edges:", ledges, redges
            
            lcand = self.find_candid( ledges, base, lbase, -1 )
##            inc = self.inc
            rcand = self.find_candid( redges, base, rbase, +1 )
##            print "Next Candidates:", lcand, inc, rcand, self.inc

            if lcand == -1 and rcand == -1:
                break

            inc = self.in_cirumcircle( lbase, rbase, lcand, rcand )
            if lcand == -1 or (lcand != -1 and rcand != -1 and inc):
                self.insert_edge( ledges, redges, (lbase, rcand), rbase, rbase )
                rbase = rcand
                
            else:
                self.insert_edge( ledges, redges, (lcand, rbase), lbase, lbase )
                lbase = lcand

        ledges.update( redges )
        if check:
            valid, errors = self._valid( ledges, l, r )
            if not valid and [ e[-1] > 1e-15 for e in errors ]:
                print "BAD Errors:", errors
                self.plot( ledges )
                pdb.set_trace()
                print "Edges:", ledges
            
        return ledges, l_ccw_l, r_cw_r

    def _valid( self, edges, test_min, test_max ):
        p = self.points
        n = test_max - test_min
        errors = []
        for i, neigh in edges.items():
            for j, k in zip( range(-1, len(neigh)-1), range(len(neigh)) ):
                u, v = neigh[j], neigh[k]
                if i > u or i > v:
                    continue
                
                pi, pu, pv = p[i], p[u], p[v]
                if (pv - pi).cross(pu - pi) <0:
                    continue
                
                for j in range( test_min, test_max ):
                    if j not in (i, u, v):
                        if self.in_cirumcircle( i, v, u, j ):
                            errors.append( (i, v, u, j, self.inc) )

        if len(errors):
            return False, errors
        return True, None

    def plot( self, neighbors ):
        edges = []
        for k, lst in neighbors.items():
            edges.extend([ (k, val) for val in lst ])
        
        polygons = [(self.points[i].data, self.points[j].data) for i, j in edges]
        coll = PolyCollection( polygons )

        fig = figure()
        ax = fig.gca()
        ax.add_collection(coll)
##        for i, pt in enumerate(self.points):
##            ax.text( self.points[i].x, self.points[i].y, str(i) )
        axis([-1.2, 1.2, -1.2, 1.2])
        show()
##        fig.close()

if __name__ == "__main__":
##    points = [
##            (0., 1.),
##            (1., 1.),
##            (0.2, 0.8),
##            (0.8, 0.8),
##            (0.5, 0.2),
##            (0.48, 0.18),
##            (0.52, 0.22)
##        ]

##    points = [
##            (-1., -1.),
##            (-1., .75),
##            (-0.75, 1.),
##            (1., 1.),
##            (1., -1.),
##            (-0.25, -0.5),
##            (0.5, -0.75)
##        ]

##    points = [(-0.5,-0.5), (0.5, -0.5), (-0.5, 0.5), (0.5, 0.5), (0.,0.)]
##    points = [(0.,0.), (0., 1.), (-0.5, -0.5), (0.5, -0.5)]

##    rs = [ 0.2, 0.4, 0.6, 0.8, 1.0 ]
##    tstep = [ pi/8, pi/12, pi/16, pi/24, pi/32 ]
##    points = [(r*cos(t), r*sin(t))
##              for i, r in enumerate(rs)
##              for t in arange(0., 2*pi-0.001, tstep[i])]
##    points.append((0., 0.))

    def timeme(n):
        p = [(random.rand()*1.8-0.9, random.rand()*1.8-0.9) for i in range(n)]
        d = Delaunay( p )
    
    import timeit
    print "10 in", timeit.timeit( lambda: timeme(10), number=100 )/100, "s"
    print "100 in", timeit.timeit( lambda: timeme(100), number=100 )/100, "s"
    print "1000 in", timeit.timeit( lambda: timeme(1000), number=100 )/100, "s"
    print "10000 in", timeit.timeit( lambda: timeme(10000), number=100 )/100, "s"
    
    points = [(random.rand()*1.8-0.9, random.rand()*1.8-0.9) for i in range(2000)]
    d = Delaunay( points )
    neighbors = d.edges

    edges = []
    for k, lst in neighbors.items():
        edges.extend([ (k, val) for val in lst ])
    
    polygons = [(points[i], points[j]) for i, j in edges]
    coll = PolyCollection( polygons )

    fig = figure()
    ax = fig.gca()
    ax.add_collection(coll)
    axis([-1.2, 1.2, -1.2, 1.2])
    show()
