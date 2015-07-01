#!/usr/bin/env python
"Fit heating rate from series of temperature measurements."

import sys
from matplotlib import pyplot
import numpy

if len( sys.argv ) < 2:
    print( "usage: {} file_name".format( sys.argv[0] ) )
    sys.exit(0)

FILENAME = sys.argv[1]
DATA = numpy.loadtxt( FILENAME, skiprows=1 )
TIMES = DATA[:, 0]
NBARS = DATA[:, 1]
SIGMAS = DATA[:, 2]

FIT = numpy.polyfit( TIMES[1:], NBARS[1:], 1 ) #, cov=True )
ERR = (0, 0) #numpy.sqrt( numpy.diag(COV) )
print( "Heating rate: {} +- {}".format( FIT[0], ERR[0] ) )
print( "Initial quanta: {} +- {}".format( FIT[1], ERR[0] ) )

pyplot.xlim( -1, 420 )
pyplot.ylim( 0, 500 )
pyplot.grid( True )

pyplot.title( "Simulated Radial $\\bar{n}$ vs. Fit Radial $\\bar{n}$" )
pyplot.xlabel( "Simulated Radial $\\bar{n}$ with Laser Noise (quanta)" )
pyplot.ylabel( "Fit Radial $\\bar{n}$ (quanta)" )

pyplot.errorbar( TIMES, NBARS, yerr=SIGMAS, fmt='r+' )
pyplot.plot( TIMES, numpy.polyval( FIT, TIMES ), 'r' )

pyplot.show()

