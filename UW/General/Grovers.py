#!/usr/bin/python

import numpy

N = 10
val = 254

arr = [[1]]
arr.extend( [[0]]*(2**N-1) )

state = numpy.array( arr )
hadamard = 1 / numpy.sqrt(2) * numpy.array( ((1., 1.), (1., -1.)) )

hadamardN = hadamard.copy()
for i in range( N-1 ):
	X, Y = hadamardN.shape
	out = numpy.empty((2*X, 2*Y) )
	for k in range(2):
		for l in range(2):
			for m in range(X): 
				for n in range(Y):
					out[k*X +m, l*Y +n] = hadamard[k,l]*hadamardN[m,n]
	hadamardN = out

arr = [1.]*(2**N - val)
arr.append( -1. )
arr.extend( [1.]*(val-1) )
oracle = numpy.diag( arr )

diffusion = 2. / 2**N * numpy.ones( (2**N, 2**N) ) - numpy.identity( 2**N )

state = numpy.dot( hadamardN, state )
step = 0
while step < numpy.pi * numpy.sqrt( 2**N ) / 4:
	state = numpy.dot( diffusion, numpy.dot( oracle, state ) )
	print state[2**N -val, 0]
	step += 1

#print state

