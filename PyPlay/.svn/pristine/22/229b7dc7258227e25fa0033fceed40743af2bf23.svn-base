
from scipy import *
from scipy import integrate, linalg
from scipy.sparse import dok_matrix, csr_matrix

from mpl_toolkits.mplot3d import axes3d
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from matplotlib.pyplot import *

from collections import defaultdict
from itertools import combinations
import spatial, pdb

p = [(r*cos(t), r*sin(t))
     for r in arange(.1, 1.1, 0.4)
     for t in arange(0., 2*pi, pi/(10*r))]

p = sorted( p )
points = array( p )
edges = spatial.Delaunay( p )

neighbors = defaultdict(list)
for e in edges:
    neighbors[ e[0] ].append( e[1] )
    neighbors[ e[1] ].append( e[0] )

pdb.set_trace()

n = len(p)
mat_data, dmat_data = dok_matrix((n,n)), dok_matrix((n,n))
for i, (pix, piy) in enumerate(p):
    def solve( px, py, ax, ay, bx, by ):
        # p = q*a + r*b
        # r = (p.a * a.b / a.a - p.b) / (b.a * b.a / a.a - b.b)
        aa = ax**2 + ay**2
        bb = bx**2 + by**2
        ab = ax*bx + ay*by
        pa = px*ax + py*ay
        pb = px*bx + py*by
        r = (pa * ab / aa - pb) / (ab * ab / aa - bb)
        q = (pa - r*ab) / aa

        drdpx = (ax * ab / aa - bx) / (ab * ab / aa - bb)
        drdpy = (ay * ab / aa - by) / (ab * ab / aa - bb)
        dqdpx = (ax - drdpx*ab) / aa
        dqdpy = (ay - drdpy*ab) / aa
        return q, r, dqdpx, dqdpy, drdpx, drdpy

    def tri_contrib( ox, oy, sx, sy, self = False ):
        scale = abs((ox-pix)*(sy-piy) - (sx-pix)*(oy-piy))
        def i_fn( u, v ):
            if self:    return (1.-u-v)**2 * scale
            return u * (1.-u-v) * scale
            px = pix + (ox-pix)*u + (sx-pix)*v - ox
            py = piy + (oy-piy)*u + (sy-piy)*v - oy
            
            q, r, qx, qy, rx, ry = solve( px, py, pix-ox, piy-oy, sx-ox, sy-oy )
            return (1.-q-r) * (1.-u-v) * scale
        
        return integrate.dblquad( i_fn, 0, 1, lambda u:0, lambda u:1.-u )[0]

    def dtri_contrib( ox, oy, sx, sy, self = False ):
        scale = abs((ox-pix)*(sy-piy) - (sx-pix)*(oy-piy))
        def i_fn( u, v ):
            if self:    return 2.*scale
            return -1.*scale
            px = pix + (ox-pix)*u + (sx-pix)*v - ox
            py = piy + (oy-piy)*u + (sy-piy)*v - oy
            
            q, r, qx, qy, rx, ry = solve( px, py, pix-ox, piy-oy, sx-ox, sy-oy )
            return ((qx+rx)*(ox-pix)+(qy+ry)*(oy-piy) +
                    (qx+rx)*(sx-pix)+(qy+ry)*(sy-piy)) * scale
        
        return integrate.dblquad( i_fn, 0, 1, lambda u:0, lambda u:1.-u )[0]

    adjacent = [ (a,b) for
        (a,b) in combinations(neighbors[i], 2)
        if (b in neighbors[a] and a in neighbors[b]) ]

    v = sum([ tri_contrib( p[a][0], p[a][1], p[b][0], p[b][1], True )
              for a,b in adjacent])
    
    dv = sum([ dtri_contrib( p[a][0], p[a][1], p[b][0], p[b][1], True )
               for a,b in adjacent])
    
    mat_data[(i,i)] = v
    dmat_data[(i,i)] = dv
        
    for j, (pjx, pjy) in [ (j, p[j]) for j in neighbors[ i ] if i < j ]:
        shared = set( neighbors[i] ) & set( neighbors[j] )
        if len(shared) == 0:
            print "ERROR: No shared"
        val = sum([ tri_contrib( pjx, pjy, *p[s] ) for s in shared ])
        dval = sum([ dtri_contrib( pjx, pjy, *p[s] ) for s in shared ])

        mat_data[(i,j)] = val
        mat_data[(j,i)] = val
        dmat_data[(i,j)] = dval
        dmat_data[(j,i)] = dval

M, L = mat_data.todense(), dmat_data.todense()
f = c_[[-4]*n]

for i, j in combinations(range(n), 2):
    if abs(M[i,j] - M[j,i]) > 1e-10:
        print "ERROR", j, i

#print "f", f.shape, f
#print "M", M
print "L", L
#print "-Mf", -M*f

class conjugate_gradient_solver:
    def __init__( self, threshold = 1e-8, max_iterations = 100, x0 = None ):
        self.x0 = x0
        self.threshold = threshold
        self.max_iterations = max_iterations
        
    def solve( self, A, b ):
        x = self.x0
        if x is None:
            x = full_matrix( [[0.0]] * A.n )
 
        r = b - A*x
        p = r

        iterations = 0
        while iterations < self.max_iterations:
            rmag = transpose(r)*r
            alpha = rmag / (transpose(p)*A*p)
            x = x + p*alpha
            r = r - A*p*alpha

            if abs(rmag) < self.threshold:
                break

            beta = transpose(r)*r / rmag
            p = r + p*beta
            iterations += 1

        return x

x0 = transpose(matrix([1-x**2-y**2 for x,y in p]))
x0 = c_[[-1e5]*n]
pdb.set_trace()

cgs = conjugate_gradient_solver( x0 = x0 )
u = cgs.solve( L, -M*f )
#Linv = linalg.inv( L )
#print "L*Linv", L*Linv
#u = -Linv*M*f
#u = linalg.solve( L, -M*f, debug = True )
#u = linalg.lstsq( L, -M*f )[0]
print u.shape, u
print "Lu", L*u
print "err", L*u+M*f

fig = figure()
ax = fig.add_subplot(111, projection='3d')
xs, ys = points[:,0], points[:,1]
zs = u
points = c_[points[:,0], points[:,1], u]
#print points

i = 17
pix, piy = (1.,1.)
def solve( px, py, ax, ay, bx, by ):
    # p = q*a + r*b
    # r = (p.a * a.b / a.a - p.b) / (b.a * b.a / a.a - b.b)
    aa = ax**2 + ay**2
    bb = bx**2 + by**2
    ab = ax*bx + ay*by
    pa = px*ax + py*ay
    pb = px*bx + py*by
    r = (pa * ab / aa - pb) / (ab * ab / aa - bb)
    q = (pa - r*ab) / aa

    drdpx = (ax * ab / aa - bx) / (ab * ab / aa - bb)
    drdpy = (ay * ab / aa - by) / (ab * ab / aa - bb)
    dqdpx = (ax - drdpx*ab) / aa
    dqdpy = (ay - drdpy*ab) / aa
    return q, r, dqdpx, dqdpy, drdpx, drdpy

def tri_contrib( ox, oy, sx, sy, self = False ):
    scale = abs((ox-pix)*(sy-piy) - (sx-pix)*(oy-piy))
    def i_fn( u, v ):
        if self:    return (1-u-v)**2*scale
        px = pix + (ox-pix)*u + (sx-pix)*v - ox
        py = piy + (oy-piy)*u + (sy-piy)*v - oy
        
        q, r, qx, qy, rx, ry = solve( px, py, pix-ox, piy-oy, sx-ox, sy-oy )
        return (1.-q-r) #* (1.-u-v)# * scale
    return i_fn
    return integrate.dblquad( i_fn, 0, 1, lambda u:0, lambda u:1.-u )

def dtri_contrib( ox, oy, sx, sy, self = False ):
    scale = abs((ox-pix)*(sy-piy) - (sx-pix)*(oy-piy))
    def i_fn( u, v ):
        if self:    return 2*scale
        px = pix + (ox-pix)*u + (sx-pix)*v - ox
        py = piy + (oy-piy)*u + (sy-piy)*v - oy
        
        q, r, qx, qy, rx, ry = solve( px, py, pix-ox, piy-oy, sx-ox, sy-oy )
        #return q, r, qx, qy, rx, ry
        return q, r, qx, qy, rx, ry, ((qx+rx)*(ox-pix)+(qy+ry)*(oy-piy),
                (qx+rx)*(sx-pix)+(qy+ry)*(sy-piy)), scale
    return i_fn
    return integrate.dblquad( i_fn, 0, 1, lambda u:0, lambda u:1.-u )

adjacent = [ (a,b) for
    (a,b) in combinations(neighbors[i], 2)
    if (b in neighbors[a] and a in neighbors[b]) ]

o, s = adjacent[0]
print i, o, s
#ifn = tri_contrib( p[o][0], p[o][1], *p[s] )
difn = tri_contrib( 0., 1.5, 1., 1.75 )

print "(0,0)", difn(0,0)
print "(1,0)", difn(1,0)
print "(0,1)", difn(0,1)
print "(0.5,0.5)", difn(0.5,0.5)
print "(0, 0.5)", difn(0, 0.5)
print "(0, 0.75)", difn(0, 0.75)
print "(0.25, 0.25)", difn(0.25, 0.25)
        
polygons = [((p[i][0],p[i][1],u[i]), (p[j][0],p[j][1],u[j])) for i,j in edges ] 
ax.add_collection( Line3DCollection(polygons) )
#xs, ys = mgrid[0:1:10j, 0:1:10j]
#zs = difn(xs, ys)
#ax.plot_wireframe( xs, ys, zs )
#axis([-1, 1, -1, 1])
show()



                            
            
    
