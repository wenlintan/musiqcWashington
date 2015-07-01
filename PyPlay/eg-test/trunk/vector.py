
class Vector2:
    def __init__( self, x, y ):
        self.x, self.y = x, y
        self.data = (x, y)

    def dot( self, rhs ):
        return self.x*rhs.x + self.y*rhs.y

    def cross( self, rhs ):
        return self.x*rhs.y - rhs.x*self.y

    def __add__( self, rhs ):
        return Vector2( self.x + rhs.x, self.y + rhs.y )

    def __sub__( self, rhs ):
        return Vector2( self.x - rhs.x, self.y - rhs.y )

    def __neg__( self ):
        return Vector2( -self.x, -self.y )

    def __str__( self ):
        return "Vector2(%f, %f)" % (self.x, self.y)

    def __repr__( self ):
        return str( self )

class Point2:
    def __init__( self, x, y ):
        self.x, self.y = x, y
        self.data = (x, y)

    def __add__( self, rhs ):
        return Point2( self.x + rhs.x, self.y + rhs.y )
            
    def __sub__( self, rhs ):
        return Vector2( self.x - rhs.x, self.y - rhs.y )

    def __str__( self ):
        return "Point2(%f, %f)" % (self.x, self.y)

    def __repr__( self ):
        return str( self )
Point2.origin = Point2( 0., 0. )
