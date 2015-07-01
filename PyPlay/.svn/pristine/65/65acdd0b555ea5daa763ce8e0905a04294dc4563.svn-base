
import numpy
import random, math

class perlin_noise:
    def __init__( self, dim, res ):
        self.dim = dim
        self.res = res

        expand = self.dim / (self.res-1)
        self.dim = (self.res-1) * expand
        scale = 1. expand
        
        self.gradients = numpy.zeros( (self.res,self.res,2) )
        for i in range( self.res ): for j in range( self.res ):
            theta = random.random() * math.pi * 2.
            self.gradients[i][j][0] = math.cos( theta )
            self.gradients[i][j][1] = math.sin( theta )

        self.tex = numpy.zeros( (self.dim,self.dim,3), numpy.int8 )
        for i in range( self.dim ): for j in range( self.dim ):
            dx = ( i % self.res ) * scale
            dy = ( j % self.res ) * scale
            

    def easy( self, t ):
        return 3*t*t - 2*t*t*t
        
