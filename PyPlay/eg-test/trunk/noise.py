
from random import shuffle, random
from math import floor

class Perlin:

    def __init__( self ):
        self.random = list( range(256) )
        shuffle( self.random )
        self.random = self.random * 2
    
    def noise( self, x, y, z ):
        X, Y, Z = map( lambda x: int(x) & 255, (x, y, z) )
        x, y, z = x - floor(x), y - floor(y), z - floor(z)

        u, v, w = map( self.fade, (x, y, z) )
        A, B = self.random[X] + Y, self.random[X+1] + Y
        AA, AB = self.random[A] + Z, self.random[A+1] + Z
        BA, BB = self.random[B] + Z, self.random[B+1] + Z

        return self.lerp( w,
            self.lerp( v, self.lerp( u, self.grad( AA,   x,   y,   z ),
                                        self.grad( BA,   x-1, y,   z ) ),
                          self.lerp( u, self.grad( AB,   x,   y-1, z ),
                                        self.grad( BB,   x-1, y-1, z ) ) ),
            self.lerp( v, self.lerp( u, self.grad( AA+1, x,   y,   z-1 ),
                                        self.grad( BA+1, x-1, y,   z-1 ) ),
                          self.lerp( u, self.grad( AB+1, x,   y-1, z-1 ),
                                        self.grad( BB+1, x-1, y-1, z-1 ) ) ) )

    @staticmethod
    def fade( t ):
        return t * t * t * (t * (t * 6 - 15) + 10)

    @staticmethod
    def lerp( t, a, b ):
        return a + t * (b - a)

    def grad( self, h, x, y, z ):
        h = self.random[h] & 15
        u = x if h<8 else y
        v = y if h<4 else (x if h==12 or h==14 else z)
        return (u if h&1 else -u) + (v if h&2 else -v)

class Brownian:
    def __init__( self ):
        self.ampls, self.freqs = [], []
        self.perlins = []

    def add_component( self, ampl, freq ):
        self.ampls.append( ampl )
        self.freqs.append( freq )
        self.perlins.append( Perlin() )

    def noise( self, x, y, z ):
        i = zip( self.ampls, self.freqs, self.perlins )
        return sum( a*p.noise( x*f, y*f, z*f ) for a, f, p in i )

