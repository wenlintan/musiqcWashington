
import numpy as np
from matplotlib import pyplot as plt
import matplotlib

font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 22}

matplotlib.rc('font', **font)

plt.plot( [-0.1, 0.1], [-1, -1], 'k', linewidth=2.0 )
plt.text( 0.2, -1.03, '$\\left| 00 \\right>$' )
plt.plot( [-0.1, 0.1], [1, 1], 'k', linewidth=2.0 )
plt.text( 0.2, 0.97, '$\\left| 11 \\right>$' )

for y, n in zip( (-0.2, 0, 0.2), ("n-1", "n", "n+1") ):
    plt.plot( [-0.8, -0.6], [y, y], 'k', linewidth=2.0 )
    plt.text( -1.35, y-0.03, '$\\left| 10 \\right> \\left| {} \\right>$'.format(n) )
    plt.plot( [0.6, 0.8], [y, y], 'k', linewidth=2.0 )
    plt.text( .87, y-0.03, '$\\left| 01 \\right> \\left| {} \\right>$'.format(n) )

ax = plt.axes()
ax.annotate( '', xytext=(0, -1), xy=(-0.68, 0.17), 
	arrowprops=dict(arrowstyle="<|-|>", linewidth=2.0) )
ax.annotate( '', xytext=(0, -1), xy=(-0.68, -0.13), 
	arrowprops=dict(arrowstyle="<|-|>", linewidth=2.0) )
ax.annotate( '$\\omega + \\delta$', xy=( -0.3, -0.4 ) )

ax.annotate( '', xytext=(-0.68, 0.13), xy=(0, 1), 
	arrowprops=dict(arrowstyle="<|-|>", linewidth=2.0) )
ax.annotate( '', xytext=(-0.68, -0.17), xy=(0, 1), 
	arrowprops=dict(arrowstyle="<|-|>", linewidth=2.0) )
ax.annotate( '$\\omega - \\delta$', xy=( -0.6, 0.7 ) )

ax.annotate( '', xytext=(0, -1), xy=(0.67, -0.13), 
	arrowprops=dict(arrowstyle="<|-|>", linewidth=2.0) )
ax.annotate( '', xytext=(0, -1), xy=(0.67, 0.17), 
	arrowprops=dict(arrowstyle="<|-|>", linewidth=2.0) )
ax.annotate( '', xytext=(0.67, -0.17), xy=(0, 1), 
	arrowprops=dict(arrowstyle="<|-|>", linewidth=2.0) )
ax.annotate( '', xytext=(0.67, 0.13), xy=(0, 1), 
	arrowprops=dict(arrowstyle="<|-|>", linewidth=2.0) )

ax.annotate( '', xytext=(0.7, 0.02), xy=(0.7, -0.22), 
	arrowprops=dict(arrowstyle="<|-|>", linewidth=2.0) )
ax.annotate( '$\\omega_x$', xy=( 0.73, -0.13 ) )

plt.xticks( [] )
plt.yticks( [] )
plt.xlim( -1.4, 1.45 )
plt.ylim( -1.2, 1.2 )
plt.show()

