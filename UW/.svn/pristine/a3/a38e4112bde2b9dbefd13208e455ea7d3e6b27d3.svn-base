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
EIGENS = DATA[:, 1]
NBARS = DATA[:, 5]

FIT = numpy.polyfit( EIGENS, NBARS, 1 ) #, cov=True )
ERR = (0, 0) #numpy.sqrt( numpy.diag(COV) )
print( "Heating rate: {} +- {}".format( FIT[0], ERR[0] ) )
print( "Initial quanta: {} +- {}".format( FIT[1], ERR[0] ) )

#pyplot.xlim( 0.0002, 0.0018 )
pyplot.xlim( 0.02, 0.045 )
pyplot.ylim( 0, 15000 )
pyplot.grid( True )

pyplot.title( "$\\bar{n}$ in Radial Modes with Different Cooling Strengths" )
pyplot.xlabel( "Maximum Barium Eigenvector Component" )
pyplot.ylabel( "Average Thermal Occupation Number" )

pyplot.plot( EIGENS, NBARS, 'ro' )
FIT_XS = numpy.arange( 0.0, 0.05, 0.001 )
pyplot.plot( FIT_XS, numpy.polyval( FIT, FIT_XS ), 'r' )

pyplot.show()

