
import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import proj3d

class Arrow3D(FancyArrowPatch):
    def __init__(self, xs, ys, zs, *args, **kwargs):
        FancyArrowPatch.__init__(self, (0,0), (0,0), *args, **kwargs)
        self._verts3d = xs, ys, zs

    def draw(self, renderer):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, renderer.M)
        self.set_positions((xs[0],ys[0]),(xs[1],ys[1]))
        FancyArrowPatch.draw(self, renderer)

def drawSphere(xCenter, yCenter, zCenter, r):
    #draw sphere
    u, v = np.mgrid[np.pi/2+np.pi/1.5:2*np.pi+np.pi/2+np.pi/1.5:80j, 0:np.pi:80j]
    #u2, v2 = np.mgrid[0:2*np.pi:50j, 0:np.pi:2j]
    #u = np.concatenate( (u1, u2), axis=0 )
    #v = np.concatenate( (v1, v2) )
    
    x=np.cos(u)*np.sin(v)
    y=np.sin(u)*np.sin(v)
    z=np.cos(v)
    # shift and scale sphere
    x = r*x + xCenter
    y = r*y + yCenter
    z = r*z + zCenter
    return (x,y,z)


x = 10*np.random.rand(20)
y = 10*np.random.rand(20)
z = 10*np.random.rand(20)
r = np.random.rand(20)


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

(xs, ys, zs) = drawSphere( 0, 0, 0, 1 )
ax.plot_wireframe( xs, ys, zs, cstride=40, rstride=40 )

ax.add_artist( Arrow3D( [0, 0], [0, 0], [0, 1], mutation_scale=20, lw=3, arrowstyle="-|>", color='r' ) )
ax.add_artist( Arrow3D( [0, 0], [0, 0], [0, -1], mutation_scale=20, lw=3, arrowstyle="-|>", color='r' ) )
ax.add_artist( Arrow3D( [0, 0], [0, -1], [0, 0], mutation_scale=20, lw=2, arrowstyle="-|>", color='k' ) )
ax.add_artist( Arrow3D( [0, 1], [0, 0], [0, 0], mutation_scale=20, lw=2, arrowstyle="-|>", color='k' ) )

ax.text( 0, 0, 1.1, "$\\hat{z} = \\left| 1 \\right>$", size=20 )
ax.text( 1.15, -0.1, 0, "$\\hat{x}$", size=20 )
ax.text( 0.1, -1.35, 0, "$\\hat{y}$", size=20 )
ax.text( 0, 0, -1.3, "$\\left| 0 \\right>$", size=20 )
plt.show()
