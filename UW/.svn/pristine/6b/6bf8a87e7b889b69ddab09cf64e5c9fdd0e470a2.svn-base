#!/usr/bin/env python

import numpy as np
import matplotlib
from matplotlib import pyplot as plt

font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 22}

matplotlib.rc('font', **font)

ax = plt.axes()
ax.text( 0.1, 3, "1.31 MHz" )
ax.annotate( '', xytext=(1.0, 3), xy=(1.0, 3 + 0.5*0.86),
		arrowprops=dict(arrowstyle="-|>") )
ax.annotate( '', xytext=(1.5, 3), xy=(1.5, 3 + 0.5*0.50),
		arrowprops=dict(arrowstyle="-|>") )
ax.scatter( [2.0, 2.5], [3, 3], s=[10, 10], color='purple' )

ax.text( 0.1, 2, "1.28 MHz" )
ax.annotate( '', xytext=(1.0, 2), xy=(1.0, 2 + 0.5*-0.5),
		arrowprops=dict(arrowstyle="-|>") )
ax.annotate( '', xytext=(1.5, 2), xy=(1.5, 2 + 0.5*0.86),
		arrowprops=dict(arrowstyle="-|>") )
ax.scatter( [2.0, 2.5], [2, 2], s=[10, 10], color='purple' )

ax.text( 0.1, 1, "1.03 MHz" )
ax.annotate( '', xytext=(2.0, 1), xy=(2.0, 1 + 0.5*0.50),
		arrowprops=dict(facecolor='purple', arrowstyle="-|>") )
ax.annotate( '', xytext=(2.5, 1), xy=(2.5, 1 + 0.5*0.86),
		arrowprops=dict(facecolor='purple', arrowstyle="-|>") )
ax.scatter( [1.0, 1.5], [1, 1], s=[10, 10] )

ax.text( 0.1, 0, "1.01 MHz" )
ax.annotate( '', xytext=(2.0, 0), xy=(2.0, 0 + 0.5*-0.86),
		arrowprops=dict(facecolor='purple', arrowstyle="-|>") )
ax.annotate( '', xytext=(2.5, 0), xy=(2.5, 0 + 0.5*0.50),
		arrowprops=dict(facecolor='purple', arrowstyle="-|>") )
ax.scatter( [1.0, 1.5], [0, 0], s=[10, 10] )

ax.text( 0.95, -0.7, "Ba" )
ax.text( 1.45, -0.7, "Ba" )
ax.text( 1.95, -0.7, "Yb" )
ax.text( 2.45, -0.7, "Yb" )

plt.xlim(0, 2.7)
plt.ylim(-0.9, 3.7)
plt.xticks([])
plt.yticks([])
plt.show()
