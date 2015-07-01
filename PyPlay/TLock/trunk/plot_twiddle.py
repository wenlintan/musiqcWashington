
import sys

from numpy import *
from matplotlib.pyplot import *

if len(sys.argv) < 2:
	print( "Must pass which twiddle data to graph." )
	sys.exit(0)

i = sys.argv[1]
f = open("test_{}.txt".format(i), "r")

data = array([[float(d.strip()) for d in l.split()] for l in f.readlines()])
f.close()

# Skip header
data = data[3:,:]

print "Errors:"
for i in range(3):
	err = sum( data[:,i]**2 ) / float(len(data[:,i]))
	print "Channel 1: {}".format(err)

plot( data[:,0] )
plot( data[:,1] )
plot( data[:,2] )
show()

