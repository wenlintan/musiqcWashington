#!/usr/bin/env python
from mpl_toolkits.mplot3d import axes3d
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib import cm
import matplotlib.pyplot as plt
import numpy as np
import sys

if len(sys.argv) < 3:
	print( "usage: ", sys.argv[0], " <datafile> <trifile>" )
	sys.exit(0)

data = np.genfromtxt( sys.argv[1], delimiter=' ' )
tris = np.genfromtxt( sys.argv[2], delimiter=' ', dtype=int )

#xs = np.arange( -1+0./99, 1.001-0./99, 2./99 )
xs = data[1::30,0]
ys = data[1::30,3]
actual = 4 / np.pi / (1 - xs**2)**0.5

plt.plot( xs, ys )
plt.plot( xs, actual )
plt.show()
sys.exit(0)

fig = plt.figure()
ax = fig.gca( projection='3d' )

for i in range( len(tris) ):
	tri = data[ tris[i] ]
	coll = Poly3DCollection( [list(zip(tri[:,0], tri[:,1], tri[:,2]))],
		array=tri[:,3], cmap=cm.jet )
	ax.add_collection3d( coll )

ax.set_ylim( -5000, 5000 )
ax.set_xlim( -5000, 5000 )
ax.set_zlim3d( -15000, 15000 )

plt.show()

