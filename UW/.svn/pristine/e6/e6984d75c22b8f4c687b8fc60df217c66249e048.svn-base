#!/usr/bin/env python
"Plot reordering data vs. cooling frequency."

import sys
from matplotlib import pyplot
import numpy as np
from scipy.optimize import curve_fit

AMU = 1.67e-27
KBOLTZMANN = 1.38e-23

GAMMA = 10.5

if len(sys.argv) < 2:
    print( "usage: {} <lineshape> <reordering>".format( sys.argv[0] ) )
    sys.exit(0)

LINESHAPE = np.loadtxt( sys.argv[1] )
DATA = np.loadtxt( sys.argv[2] )

FREQS = LINESHAPE[:, 0]
COUNTS = LINESHAPE[:, 1]

def LORENTZIAN( freqs, mag, center, sat ):
    return mag * sat / ( 1 + sat + 4 * (freqs - center)**2 / GAMMA ** 2 )
print( FREQS, COUNTS, LORENTZIAN( FREQS, 240, 714470, 0.2 ) )

PARAMS, COV = curve_fit( LORENTZIAN, FREQS, COUNTS, [240, 714470, 0.2] )
MAG, CENTER, SAT = PARAMS
print( CENTER, SAT )



FREQS = DATA[:, 0]
REORDERS = DATA[:, 1]
ERROR = np.sqrt( (1 - REORDERS) * REORDERS / DATA[:, 2] )

pyplot.errorbar( FREQS - CENTER, REORDERS, yerr=ERROR, fmt='r+' )

pyplot.title( "Probability of Chain Order Stability" )
pyplot.ylabel( "Probability of Ion Chain Stability" )
pyplot.xlabel( "Cooling Laser Detuning (MHz)" )
pyplot.ylim( 0, 1.01 )
#pyplot.xlim( 0, 4 )
pyplot.grid( True )
pyplot.show()
