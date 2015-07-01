#!/usr/bin/env python
"Plot 1762 Frequency scans."

import numpy as np
import matplotlib.pyplot as plt

import sys
if len( sys.argv ) < 2:
	print( "usage: {} data_file".format( sys.argv[0] ) )
	sys.exit(0)

filename = sys.argv[1]
data = np.genfromtxt( filename, delimiter="\t", skip_header=1, dtype=float )

plt.grid( True )
plt.ylim( -0.01, 1 )
plt.xlim( 83.7, 87.3 )

plt.title( "Shelving Probability vs. 1762 Frequency Offset" )
plt.xlabel( "1762 Frequency Offset (MHz)" )
plt.ylabel( "Shelving Probability" )

plt.plot( data[:, 0] / 1e6, 1 - data[:, 1], 'r' )
plt.show()
