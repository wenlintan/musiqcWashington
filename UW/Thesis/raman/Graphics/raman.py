
import numpy as np
import matplotlib
from matplotlib import pyplot as plt

font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 22}

matplotlib.rc('font', **font)

TS = np.arange( 30000 )
FN = np.cosh( TS / 3000 - 5 )**-1 * np.sin( TS / 500 )**10
FN2 = np.cosh( TS / 3000 - 5 )**-1 * np.sin( TS / 500 + 1 )**10 + 1.2

plt.plot( TS, FN )
plt.plot( TS, FN2 )

PEAK1 = 500 * (9*np.pi + np.pi/2)
PEAK2 = 500 * (11*np.pi + np.pi/2 - 1)
plt.plot( [PEAK1, PEAK1], [0.0, 1.15], 'k' )
plt.plot( [PEAK2, PEAK2], [1.05, 2.3], 'k' )

ax = plt.axes()
ax.annotate( '', xytext=(PEAK1, 1.1), xy=(PEAK2, 1.1), 
	arrowprops=dict(arrowstyle="<|-|>") )
ax.annotate( '$\\delta$', xy=( PEAK1 + 1000, 0.95 ) )

plt.xticks( [] )
plt.yticks( [] )
plt.xlabel( "Frequency" )
plt.ylim( 0, 2.3 )
plt.show()

