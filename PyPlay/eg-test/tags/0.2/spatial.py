
from scipy import *
from scipy import linalg, random

def Delaunay( points ):
    #print "Entering:", points

    def cp( a, b, c ):
        dx1 = points[a][0] - points[b][0]
        dy1 = points[a][1] - points[b][1]
        dx2 = points[c][0] - points[b][0]
        dy2 = points[c][1] - points[b][1]
        return dx1*dy2 - dx2*dy1
    
    if len(points) == 2:
        return [(0, 1)]
    
    if len(points) == 3:
        # If points not colinear generate triangle
        # Otherwise, line
        if cp( 0, 1, 2 ) != 0:
            return [(0, 1), (1, 2), (0,2 )]
        return [(0, 1), (1, 2)]

    n = len(points)
    lpoints, rpoints = points[:n/2], points[n/2:]
    l = Delaunay( lpoints )
    r = [(i+n/2, j+n/2) for i, j in Delaunay( rpoints )]

    def in_cirumcircle( a, b, c, test ):
        ax, ay = points[a];     bx, by = points[b]
        cx, cy = points[c];     dx, dy = points[test]
        l1 = [ ax-dx, ay-dy, (ax**2-dx**2) + (ay**2-dy**2) ]
        l2 = [ bx-dx, by-dy, (bx**2-dx**2) + (by**2-dy**2) ]
        l3 = [ cx-dx, cy-dy, (cx**2-dx**2) + (cy**2-dy**2) ]
        return linalg.det( c_[l1, l2, l3] ) > 0        
        
    ysortl = sorted([ (y, -x, i) for i, (x, y) in enumerate( lpoints ) ])
    ysortr = sorted([ (y, x, i+n/2) for i, (x, y) in enumerate( rpoints ) ])
    
    def cp( a, b, c ):
        dx1 = points[a][0] - points[b][0]
        dy1 = points[a][1] - points[b][1]
        dx2 = points[c][0] - points[b][0]
        dy2 = points[c][1] - points[b][1]
        return dx1*dy2 - dx2*dy1
        
    def intersects( e, edge_list ):
        for e2 in edge_list:
            c1 = cp( e2[0], e2[1], e[0] )*cp( e2[0], e2[1], e[1] ) < 0
            c2 = cp( e[0], e[1], e2[0] )*cp( e[0], e[1], e2[1] ) < 0
            if c1 and c2:
                return True
        return False
    
    i, j = 0, 0
    while intersects( (ysortl[i][2], ysortr[j][2]), r ):
        j += 1

    while intersects( (ysortl[i][2], ysortr[j][2]), l ):
        i += 1
    li, ri = (ysortl[i][2], ysortr[j][2])
    
    for i in range(n/2):
        if cp( li, ri, i ) > 0:
            li = i
    for i in range(n/2, n):
        if cp( li, ri, i ) > 0:
            ri = i
    
    def opp( edge, v ):
        if edge[0] == v:    return edge[1]
        if edge[1] == v:    return edge[0]
        raise ValueError
    
    def angle( e1, e2, reverse ):
        if reverse:
            e1, e2 = e2, e1
            
        if e1[0] in e2:     common = e1[0]
        else:               common = e1[1]

        v1 = opp( e1, common )
        v2 = opp( e2, common )

        c = points[common]
        v1, v2 = points[v1], points[v2]

        dx1, dy1 = v1[0]-c[0], v1[1]-c[1]
        dx2, dy2 = v2[0]-c[0], v2[1]-c[1]
        
        dp = (dx1*dx2 + dy1*dy2) / sqrt(dx1**2+dy1**2) / sqrt(dx2**2+dy2**2)
        if dx1*dy2 - dx2*dy1 < 0:
            return dp

        # Return something such that sorting on the return value
        # here is equivalent to sorting on clockwise angle
        return -dp - 2.

    def best_cand( base, edge_list, reverse ):
        #print "Finding candidate:", base, edge_list, reverse
        a = [ (angle( (li, ri), e, reverse ), e)
              for e in edge_list if base in e ]
        
        angles = sorted( a, reverse = True )
        if not len(angles):
            return -1
        
        #print angles

        cand = -1
        while angles[0][0] > -1.0 and len(angles) >= 2:
            cand, ncand = opp( angles[0][1], base ), opp( angles[1][1], base )
            if in_cirumcircle( li, ri, cand, ncand ):
                del edge_list[edge_list.index(angles[0][1])]
                del angles[0]
                continue
            break

        if angles[0][0] > -1.0 and len(angles) == 1:
            return opp( angles[0][1], base )
        return cand

    #print "Combining!"
    edges = [(li, ri)]
    while True:
        print "State:", edges, l, r
        #print "Base edge:", (li, ri)
        lcand = best_cand( li, l, True )
        rcand = best_cand( ri, r, False )
        #print "Candidates:", (lcand, rcand)

        if lcand == -1 and rcand == -1:
            break

        if lcand == -1 or in_cirumcircle( li, ri, lcand, rcand ):
            edges.append( (li, rcand) )
            ri = rcand
        else:
            edges.append( (ri, lcand) )
            li = lcand

    edges.extend( l )
    edges.extend( r )
    return edges

if __name__ == "__main__":
    from mpl_toolkits.mplot3d import axes3d
    from matplotlib.pyplot import *
    from matplotlib.collections import PolyCollection
    
    points = [(random.rand()*1.8-0.9, random.rand()*1.8-0.9) for i in range(100)]

##    points = [
##            (0., 1.),
##            (1., 1.),
##            (0.2, 0.8),
##            (0.8, 0.8),
##            (0.5, 0.2),
##            (0.48, 0.18),
##            (0.52, 0.22)
##        ]

    rs = [ 0.2, 0.4, 0.6, 0.8, 1.0 ]
    tstep = [ pi, pi/2, pi/4, pi/8, pi / 16 ]
    points = [(r*cos(t), r*sin(t))
     for i, r in enumerate(rs)
     for t in arange(0., 2*pi-0.001, tstep[i])]

    print points
    p = sorted(points)
    edges = Delaunay( p )
    #print p
    #print edges

    polygons = [(p[i], p[j]) for i, j in edges]
    coll = PolyCollection( polygons )

    fig = figure()
    ax = fig.gca()
    ax.add_collection(coll)
    axis([-1, 1, -1, 1])
    show()



