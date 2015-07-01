
import numpy
from matplotlib.pyplot import *

#Load fits
fit1s = [ [ float(i.strip()) for i in l.split() ] 
				for l in file('fit1s_weird.txt') ]
fit1s = numpy.array( fit1s )

fit500ms = [ [ float(i.strip()) for i in l.split() ] 
				for l in file('fit500ms_weird.txt') ]
fit500ms = numpy.array( fit500ms )

#Load data
eps1s = 207891
delta1s = -0.629647
scale1s = 0.002 #0.00238967

data1s = [ float(i.strip()) for l in file('heat_rate_1s_1kHz-12-6-12-2.txt')
			for i in l.split() ]
data1s = numpy.array( data1s )

eps500ms = 137954
delta500ms = -0.894705
scale500ms = 0.002 #0.00306838

data500ms = [ float(i.strip()) for l in file('heat_rate_500ms_1kHz-12-6-12-2.txt')
			for i in l.split() ]
data500ms = numpy.array( data500ms )

plot( fit1s[::10, 0], fit1s[::10, 1] )
plot( fit1s[::10, 0], scale1s*data1s[200:301] )
show()

plot( fit500ms[::10, 0], fit500ms[::10, 1] )
plot( fit500ms[::10, 0], scale500ms*data500ms[200:301] )
show()

