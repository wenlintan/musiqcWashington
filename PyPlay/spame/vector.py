import math, copy

class vector3:
    epsilon = 0.0000001
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.normed = False
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def get_raw(self):
        return (self.x, self.y, self.z)
    raw = property(get_raw)

    def get_raw_list(self):
        return [self.x, self.y, self.z]
    raw_list = property(get_raw_list)
        
    def __add__(self, other):
        return vector3( self.x + other.x,
                        self.y + other.y,
                        self.z + other.z )

    def __sub__(self, other):
        return vector3( self.x - other.x,
                        self.y - other.y,
                        self.z - other.z )
    
    def __mul__(self, c):
        return vector3( self.x * c,
                        self.y * c,
                        self.z * c )

    def component_mult(self, other):
        return vector3( self.x * other.x,
                        self.y * other.y,
                        self.z * other.z )
    
    def __div__(self, c):
        return self * (1.0 / c)

    def component_div(self, other):
        try:
            return vector3( self.x / other.x,
                            self.y / other.y,
                            self.z / other.z )
        except ZeroDivisionError:
            nx = copy.copy( other )
            if other.x == 0.0:
                nx.x = vector3.epsilon
            if other.y == 0.0:
                nx.y = vector3.epsilon
            if other.z == 0.0:
                nx.z = vector3.epsilon
            return self.component_div( nx )
                

    def __neg__(self):
        return vector3( -self.x, -self.y, -self.z )    

    def __repr__(self):
        return "vector3(%f, %f, %f)" % (self.x, self.y, self.z )
            
    def __str__(self):
        return "[%f, %f, %f]" % (self.x, self.y, self.z)

    def dp(self, other):
        "Returns: dot product"
        return ( self.x * other.x +
                 self.y * other.y +
                 self.z * other.z )

    def cos(self, other):
        "Returns: cos(angle) between this vector and other"
        dp = self.dp(other)
        mags = self.mag() * other.mag()
        return dp / mags

    def theta(self, other):
        "Returns: theta of angle between this vector and other"
        dp = self.dp(other)
        mags = self.mag() * other.mag()
        return math.acos( dp / mags )

    def crossp(self, other):
        "Returns: the cross product of this vector and other"
        x = self.y * other.z - self.z * other.y
        y = self.z * other.x - self.x * other.z
        z = self.x * other.y - self.y * other.x
        return vector3( x, y, z )

    def cut_max(self, maximum):
        "Performs min([component,maximum]) componentwise"
        self.x = min( self.x, maximum )
        self.y = min( self.y, maximum )
        self.z = min( self.z, maximum )

    def cut_min(self, minimum):
        "Performs max([component,maximum]) componentwise"
        self.x = max( self.x, minimum )
        self.y = max( self.y, minimum )
        self.z = max( self.z, minimum )

    def contains( self, o ):
        return ( o.x > 0 and o.x < self.x and
                 o.y > 0 and o.y < self.y and
                 o.z > 0 and o.z < self.z )

    def _set_normed(self):
        self.normed = True
        return self

    def norm(self):
        "Returns: a new vector in the same direction with length 1.0"
        if self.normed:
            return self

        return (self / self.mag())._set_normed()
    
    def mag(self):
        "Returns: length of this vector"
        if self.normed:
            return 1.0
        return math.sqrt( self.x**2 + self.y**2 + self.z**2 )

    def mag_squared(self):
        """ Returns: the length of this vector squared
            Note: should be used when possible in place of mag()
        """
        return self.x**2 + self.y**2 + self.z**2
    
def raw_to_vec3(raw):
    return vector3( raw[0], raw[1], raw[2] )


class vector2:
    epsilon = 0.0000001
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.normed = False
        self.x = float(x)
        self.y = float(y)
        self.z = 0.0

    def get_raw(self):
        return (self.x, self.y)
    raw = property(get_raw)

    def get_raw_list(self):
        return [self.x, self.y]
    raw_list = property(get_raw_list)
        
    def __add__(self, other):
        return vector2( self.x + other.x,
                        self.y + other.y )

    def __sub__(self, other):
        return vector2( self.x - other.x,
                        self.y - other.y )
    
    def __mul__(self, c):
        return vector2( self.x * c,
                        self.y * c )

    def component_mult(self, other):
        return vector2( self.x * other.x,
                        self.y * other.y )
    
    def __div__(self, c):
        return self * (1.0 / c)

    def component_div(self, other):
        try:
            return vector2( self.x / other.x,
                            self.y / other.y )
        except ZeroDivisionError:
            nx = copy.copy( other )
            if abs( other.x ) < vector2.epsilon:
                nx.x = vector2.epsilon
            if abs( other.y ) < vector2.epsilon:
                nx.y = vector2.epsilon
            return self.component_div( nx )

    def __neg__(self):
        return vector2( -self.x, -self.y )    

    def __repr__(self):
        return "vector2(%f, %f)" % (self.x, self.y )
            
    def __str__(self):
        return "[%f, %f]" % (self.x, self.y)

    def dp(self, other):
        "Returns: dot product"
        return ( self.x * other.x +
                 self.y * other.y )

    def cos(self, other):
        "Returns: cos(angle) between this vector and other"
        dp = self.dp(other)
        mags = self.mag() * other.mag()
        return dp / mags

    def theta(self, other):
        "Returns: theta of angle between this vector and other"
        dp = self.dp(other)
        mags = self.mag() * other.mag()
        return math.acos( dp / mags )

    def crossz(self):
        "Returns: the cross product of this vector and z"
        return vector2( self.y, -self.x )

    def crossp(self, other):
        "Returns z component of cross product of this vector and other"
        return self.x * other.y - self.y * other.x

    def cut_max(self, maximum):
        "Performs min([component,maximum]) componentwise"
        self.x = min( self.x, maximum )
        self.y = min( self.y, maximum )

    def cut_min(self, minimum):
        "Performs max([component,maximum]) componentwise"
        self.x = max( self.x, minimum )
        self.y = max( self.y, minimum )

    def contains( self, o ):
        return ( o.x > 0 and o.x < self.x and
                 o.y > 0 and o.y < self.y )

    def _set_normed(self):
        self.normed = True
        return self

    def norm(self):
        "Returns: a new vector in the same direction with length 1.0"
        if self.normed:
            return self

        return (self / self.mag())._set_normed()
    
    def mag(self):
        "Returns: length of this vector"
        if self.normed:
            return 1.0
        return math.sqrt( self.x**2 + self.y**2 )

    def mag_squared(self):
        """ Returns: the length of this vector squared
            Note: should be used when possible in place of mag()
        """
        return self.x**2 + self.y**2

def raw_to_vec2(raw):
    return vector2( raw[0], raw[1] )

class ray2:
    def __init__( self, s, e ):
        self.s = s
        self.e = e
        
        self.d = e - s

    def collide( self, other ):

        n = other.d.norm().crossp()
        d_n = self.d.dp( n )

        if abs( d_n ) < vector2.epsilon:
            return False, 0.0, vector2()

        diff = other.s - self.s
        diff_n = diff.dp( n )

        t = diff_n / d_n
        if t < 0.0 or t > 1.0:
            return False, 0.0, vector2()

        return True, t, self.s + self.d * t
        
        
        
    
