#!/usr/bin/env python
"Plot trace from molecular dynamics simulation."

import sys
from matplotlib import pyplot
import numpy as np

if len(sys.argv) < 2:
    print( 'usage: {} <data>'.format( sys.argv[0] ) )
    sys.exit(0)

DATA = np.loadtxt( sys.argv[1] )
TIMES = DATA[::, 0]
AXIALS = DATA[::, 3::3]

pyplot.title( "Axial Position of Ions During Recooling" )
pyplot.xlabel( "Time ($\\mu$s)" )
pyplot.ylabel( "Axial Position ($\\mu$m)" )
pyplot.ylim( -30, 30 )
pyplot.grid( True )

for i in range( AXIALS.shape[1] ):
    SMOOTH = np.convolve( AXIALS[:, i], np.ones(20)/20., 'valid' )
    pyplot.plot( TIMES[10:-9]*1e6, SMOOTH*1e6 )
pyplot.show()

