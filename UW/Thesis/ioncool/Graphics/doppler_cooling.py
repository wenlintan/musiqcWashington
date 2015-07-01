
import numpy as np
from matplotlib import pyplot

Gamma = 2*np.pi * 21e6
w = 2*np.pi * 1.1e6

hbar = 1.0545e-34
kb = 1.3806e-23

deltas = np.arange( -1., -1. / 8, 1. / 100 )
min_T = -hbar * 2 * ((Gamma/2)**2 + Gamma**2*deltas**2) / 8 / Gamma/deltas / kb  * 1000

pyplot.ylim( .2, .5 )
pyplot.title( "Minimum Ion Temperature vs. Laser Detuning" )
pyplot.ylabel( "Minimum Ion Temperature (mK)" )
pyplot.xlabel( "Laser Detuning from Resonance ($\Gamma$)" )
pyplot.plot( deltas, min_T )
pyplot.show()

