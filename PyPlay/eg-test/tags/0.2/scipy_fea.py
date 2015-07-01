
from scipy import *
from scipy import integrate, linalg

from mpl_toolkits.mplot3d import axes3d
from matplotlib.pyplot import *

resolution = 10
scale = 1. / resolution
def basis( i ):
    def basis_fn( x ):
        if x < scale*(i-1) or x > scale*(i+1):
            return 0.0
        if x < scale*i:
            return resolution*(x-scale*(i-1))
        return resolution*(scale*(i+1)-x)
    return basis_fn

def basis_deriv( i ):
    def basis_deriv_fn( x ):
        if x < scale*(i-1) or x > scale*(i+1):
            return 0.0
        if x < scale*i:
            return 1./scale
        return -1./scale
    return basis_deriv_fn

#x = arange(0., 1.0, 0.05)
#plot( x, vectorize(basis(1))(x), 'r', x, vectorize(basis(4))(x), 'g' )
#show()

#print integrate.quad( lambda x: basis(1)(x)*basis(2)(x), 0, 1 )

M = [[integrate.quad( lambda x: basis(i)(x)*basis(j)(x), 0, 1 )[0]
      for i in range(1,resolution)] for j in range(1,resolution)]

L = [[integrate.quad( lambda x: basis_deriv(i)(x)*basis_deriv(j)(x), 0, 1 )[0]
      for i in range(1,resolution)] for j in range(1,resolution)]

M, L = map( array, [M, L] )
print "M", M
print "L", L

f = c_[[-2]*(resolution-1)]
u = linalg.solve( L, -dot(M,f), sym_pos = True )
print "u", u
print "err", dot(L,u)+dot(M,f)

x1 = arange(scale, 1.0, scale)
x2 = arange(0, 1.0, 0.0001)
plot( x1, u, 'r', x2, -(x2-0.5)**2+0.25, 'g' )
show()

##fig = figure()
##ax = fig.add_subplot(111, projection='3d')
##xs, ys = mgrid[0:pi:100j,0:pi:100j]
##zs = cos(xs)*sin(ys)
##ax.plot_wireframe( xs, ys, zs, rstride=10, cstride=3 )
##show()
    
