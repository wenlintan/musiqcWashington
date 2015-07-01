
from scipy import *
from scipy import integrate, linalg
from scipy.sparse import dok_matrix, csr_matrix

from mpl_toolkits.mplot3d import axes3d
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from matplotlib.pyplot import *

from collections import defaultdict
from itertools import combinations
import spatial_rewrite, pdb

rs = [ 0.2, 0.4, 0.6, 0.8, 1.0 ]
tstep = [ pi/8, pi/12, pi/16, pi/24, pi/32 ]
p = [(r*cos(t), r*sin(t))
     for i, r in enumerate(rs)
     for t in arange(0., 2*pi-0.001, tstep[i])]
p.append((0., 0.))

##p = [(-0.49,-0.51), (0.49, -0.49), (-0.51, 0.49), (0.51, 0.51), (0.,0.)]
##p = [(0.,0.), (0., 1.), (-0.5, -0.5), (0.5, -0.5)]
neighbors = spatial_rewrite.Delaunay( p ).edges
print neighbors
points = array( p )

n = len(p)
dirichlet = {}
dirichlet_mapping = {-1:-1}
mapping = {-1:-1}

for i, pt in enumerate(p):
    if pt[0]*pt[0] + pt[1]*pt[1] > 0.95:
        dirichlet[i] = 0.0
        dirichlet_mapping[i] = dirichlet_mapping[i - 1] + 1
        mapping[i] = mapping[i - 1]
    else:
        dirichlet_mapping[i] = dirichlet_mapping[i - 1]
        mapping[i] = mapping[i - 1] + 1

print dirichlet, dirichlet_mapping, mapping

nreal = mapping[n - 1] + 1
ndirichlet = dirichlet_mapping[n - 1] + 1

print nreal, ndirichlet

d = zeros((ndirichlet, 1))
for i, val in dirichlet.items():
    d[ dirichlet_mapping[i] ] = val

##pdb.set_trace()
if ndirichlet != 0:
    Ddata = dok_matrix((nreal, ndirichlet))
Mdata, Ldata = zeros(nreal,), dok_matrix((nreal, nreal))

def accum_data( a, b, data ):
    if a in dirichlet and b in dirichlet:
        return
    if a in dirichlet:
        a, b = b, a
        
    if b in dirichlet:
        Ddata[(mapping[a], dirichlet_mapping[b])] += data
    else:
        Ldata[(mapping[a], mapping[b])] += data
        if a != b:
            Ldata[(mapping[b], mapping[a])] += data

def advance( edges, vert, off ):
    l = len( edges )
    return edges[ (edges.index(vert)+off) % l ]

for i, lst in neighbors.items():
    adjacent = [(lst[k-1],lst[k]) for k in range( len(lst) )
                if (i < lst[k-1] and i < lst[k] and
                    advance( neighbors[lst[k-1]], i, -1 ) == lst[k] and
                    advance( neighbors[lst[k]],   i, +1 ) == lst[k-1])]
    
    for (j, k) in adjacent:
        pi, pj, pk = p[i], p[j], p[k]
        dux, duy = pj[0] - pi[0], pj[1] - pi[1]
        dvx, dvy = pk[0] - pi[0], pk[1] - pi[1]
        dwx, dwy = pk[0] - pj[0], pk[1] - pj[1]
        
        if dvx*duy < dux*dvy:
            continue

        area = 0.5 * (dvx*duy - dux*dvy)
        for r in (i, j, k):
            if r not in dirichlet:
                Mdata[ mapping[r] ] += area / 3.0

        # Want to solve 1 - b(x-pix) - c(y-piy)
        # 0 = 1 - b(pjx - pix) - c(pjy - piy)
        # 0 = 1 - b(pkx - pix) - c(pky - piy)
        bi = dwy / 2 / area
        ci = -dwx / 2 / area

        bj = duy / 2 / area
        cj = -dux / 2 / area

        bk = -dvy / 2 / area
        ck = dvx / 2 / area

        accum_data( i, i, (bi*bi + ci*ci) * area )
        accum_data( j, j, (bj*bj + cj*cj) * area )
        accum_data( k, k, (bk*bk + ck*ck) * area )
        
        accum_data( i, j, (bi*bj + ci*cj) * area )
        accum_data( j, k, (bj*bk + cj*ck) * area )
        accum_data( i, k, (bi*bk + ci*ck) * area )

##        print "Triangle:", i, j, k
##        print Ldata.todense()

L = Ldata.todense() 
f = -transpose(matrix( r_[ [-4]*nreal ] * Mdata ))
##f = -transpose(matrix( r_[ [0]*5, -20, [0]*(nreal-6) ] * Mdata ))
##print "M", Mdata
##print "f", f
if ndirichlet != 0:
    f -= Ddata.todense()*matrix(d)

##print "L", L
##print "f", transpose(f)

sol = zeros((nreal,1))
for i, (x,y) in enumerate(p):
    if i not in dirichlet:
        sol[ mapping[i] ] = 1 - x**2 - y**2
error = transpose(L*sol - f)
##pdb.set_trace()

print "Error:", error

##print "Shapes:", L.shape, f.shape
u = linalg.solve( L, f, sym_pos = True )
##print "u", transpose(u)

def h( i ):
    if i in dirichlet:  return d[ dirichlet_mapping[i] ]
    return u[ mapping[i] ]

edges = [(i,j) for i, lst in neighbors.items() for j in lst]
polygons = [((p[i][0],p[i][1],h(i)), (p[j][0],p[j][1],h(j))) for i,j in edges ] 

fig = figure()
ax = fig.add_subplot(111, projection='3d')
ax.add_collection( Line3DCollection(polygons) )
show()


        
    
