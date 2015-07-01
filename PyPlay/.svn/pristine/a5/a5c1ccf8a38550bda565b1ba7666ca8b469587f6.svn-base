#!/usr/bin/env python

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot

import numpy as np
import sys

if len( sys.argv ) < 4:
	print( "usage: {0} <data> <nions> <ndark>".format( sys.argv[0] ) )
	sys.exit()

data = np.loadtxt( sys.argv[1] )
nions, ndark = int( sys.argv[2] ), int( sys.argv[3] )

#Assume background calibration is last column in data file
ions = (data[:,:-1] - data[:,-1,None]).flatten()
bkg = data[:,-1].flatten()
bkg = bkg - bkg.mean()
threshold = bkg.std()

fig = pyplot.figure()
ax = fig.add_subplot(311)
counts, bins, patches = ax.hist( ions, 30, facecolor='blue', align='left' )
countsbkg, bins, patches = ax.hist( bkg, bins, facecolor='red', rwidth=0.7, align='mid' )

n = 0
while bins[n] < threshold:
	n += 1

while counts[n+1] < counts[n]:
	n += 1
threshold = bins[ n ]

print( "Threshold:", threshold )

patterns = (data[:,:-1] - data[:,-1,None]) > threshold
bad_patterns = []
for i, p in enumerate( patterns ):
	if p.sum() != nions - ndark:
		print( "Incorrect number of ions ({0}) in pattern {1}".format( p.sum(), i ) )
		bad_patterns.append( i )

print( "{0} bad patterns.".format( len(bad_patterns) ) )
patterns = np.delete( patterns, bad_patterns, axis=0 )
data = np.delete( data, bad_patterns, axis=0 )

nbins = 4
binsize = (len(patterns)-1)/nbins
ys = [ sum([(patterns[i] != patterns[i+1]).any() 
	for i in range( x*binsize, (x+1)*binsize )]) / float(binsize)
	for x in range( nbins ) ]

ax = fig.add_subplot(312)
ax.plot( np.arange(nbins), ys )

nions = [ sum([patterns[i,2]
	for i in range( x*binsize, (x+1)*binsize )])
	for x in range( nbins ) ]
ys = [ sum([data[i,2] - data[i,-1]
	for i in range( x*binsize, (x+1)*binsize )]) / float(nions[x])
	for x in range( nbins ) ]

ax = fig.add_subplot(313)
ax.plot( np.arange(nbins), ys )

reorders = [ 1 for i in range( len(patterns)-1 ) 
	if (patterns[i] != patterns[i+1]).any() ]
print( "Probability:", float( len( reorders ) ) / len(patterns) )
print( "1-Probability:", 1.-float( len( reorders ) ) / len(patterns) )
print( "Usable Runs:", len(patterns) )

pyplot.savefig( 'analysis' )
#pyplot.show()

