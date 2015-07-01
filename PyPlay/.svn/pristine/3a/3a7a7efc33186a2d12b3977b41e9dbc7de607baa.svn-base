
from random import random
from math import exp, log

from matplotlib.pyplot import *
from itertools import chain
import pdb

m, a, N = 1., 0.5, 20

def action( xs ):
    s = sum( (x - xs[i-1])*(x - xs[i-1]) for i, x in enumerate(xs) )
    v = sum( x*x for x in xs ) / 2.
    return m / 2 / a * s + a * v

def update( act, path ):
    for i in range( N ):
        eps = 1.4 * ( random() - 0.5 )
        path[ i ] += eps
        
        dact = action( path ) - act
        if dact > 0. and exp( -dact ) < random():
            path[ i ] -= eps
        else:
            act = dact + act
    return act, path

def sample( n, path ):
    s = sum( x*path[j-n] for j, x in enumerate(path) )
    return 1. / N * s

result = [ 0. ] * N
def integral( ):
    path = [ 0. ] * N    
    act = action( path )
    for j in range( 200 ):
        act, path = update( act, path )

    for i in range( 10000 ):
        for j in range( 20 ):
            act, path = update( act, path )
        for j in range( N ):
            result[ j ] += 1. / 10000 * sample( j, path )

integral()
x1 = list( 0.5 * i for i in range( N-1 ) )
y1 = list( (log(g / result[i+1]) / a)
           for i, g in enumerate(result[:-1]) )

print x1, y1
plot( x1, y1, 'r+' )
show()

