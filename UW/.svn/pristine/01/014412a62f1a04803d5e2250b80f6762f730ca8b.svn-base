#!/usr/bin/env python
"Plot reordering data and simulated temperatures."

import sys
from matplotlib import pyplot
import numpy as np

AMU = 1.67e-27
KBOLTZMANN = 1.38e-23

if len(sys.argv) < 2:
    print( "usage: {} <data> <sim> <initial_temp (K)> <heating_rate (K)>".
        format( sys.argv[0] ) )
    sys.exit(0)

DATA = np.loadtxt( sys.argv[1], skiprows=1 )
SIM = np.loadtxt( sys.argv[2] )

VELS = SIM[:, 0]
TEMPS = 0.5 * 138 * AMU * VELS * VELS / KBOLTZMANN
REORDERS = 1. - SIM[:, 1]

SIMHDL, = pyplot.plot( TEMPS, REORDERS, label='simulation' )

TIMES = DATA[:, 0]
TEMPS = float(sys.argv[3]) + float(sys.argv[4]) * TIMES
REORDERS = DATA[:, 1]
ERROR = np.sqrt( (1 - REORDERS) * REORDERS / DATA[:, 2] )

DATAHDL, _, __ = pyplot.errorbar( TEMPS, REORDERS, yerr=ERROR, fmt='r+', label='Experiment' )
print(DATAHDL)

pyplot.title( "Probability of Chain Order Stability" )
pyplot.ylabel( "Probability of Ion Chain Stability" )
pyplot.xlabel( "Temperature (K)" )
pyplot.ylim( 0, 1.01 )
pyplot.xlim( 0, 4 )
pyplot.grid( True )
pyplot.legend([SIMHDL, DATAHDL], ["Simulation", "Experiment"])
pyplot.show()
