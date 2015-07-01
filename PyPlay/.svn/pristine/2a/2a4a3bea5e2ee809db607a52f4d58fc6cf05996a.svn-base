from vector3 import *

class collision:
    def __init__(self, ray):
        """Arguments: the ray that this collision is based on
           Notes: should be called at the start of collision detection
        """
        self.ray = ray

    def __call__(self, coll=False, surface=None, t=100000000000.0):
        """Arguments:
                1. boolean indicating whether actually collided
                2. surface that the collision was with
                3. t value along ray passed at construction
           Notes: returns self to facilitate such code as:
                return coll()
        """
        self.collided = coll
        self.surf = surface
        self.t = t

        #calculate actual point of intersection
        self.point = None
        if self.collided:
            self.point = self.ray.get(self.t)

        return self

    def __nonzero__(self):
        return self.collided

    def __lt__(self, other):
        return self.t < other.t

    def __repr__(self):
        return "collision(%s)(%s, %s, %f)" % ( str(self.ray),
                                               str(self.collided),
                                               str(self.surf),
                                               self.t )

class ray:
    def __init__(self, start, direct):
        "Arguments: starting position, direction"
        self.s = start
        self.t = direct.mag()
        self.d = direct / self.t

    def get_end(self):
        "Returns: the original end passed to creation"
        return self.s + (self.d * self.t)
    e = property(get_end)

    def get(self, t):
        "Returns: the point at the specified value of t"
        return self.s + (self.d * t)

    def __repr__(self):
        return "ray(%s, %s)" % ( str(self.s),
                                 str(self.d * self.t) )


class plane:
    def __init__(self, point, normal, mat):
        "Arguments: point on plane, normal, material"
        self.n = normal.norm()
        self.p = point
        self.m = mat

    def collide(self, ray):
        """ Arguments: a ray to collide with
            Returns: a fully constructed collision object
        """

        coll = collision(ray)

        # |proj of to_plane onto self.n|
        # ___________________________
        # |proj of ray.d onto self.n|

        #simplify assumption: len(self.n) == 1.0

        to_plane_onto_n = (ray.s - self.p).dp(self.n)
        dir_onto_n = ray.d.dp(self.n)
        
        if abs(dir_onto_n) < 0.000001:
            return coll()

        t = -to_plane_onto_n / dir_onto_n
        if t < 0.0:
            return coll()

        return coll(True, self, t)

    def normal(self, point):
        "Returns: normal to this surface at given point"
        return self.n

    def eccentricity(self, ray):
        "Returns: float representing how close the ray is to intersecting"
        #Calculate this by determing which side of the plane start and
        #end points are on

        #If they're on opp. sides we'll always intersect eccentricity = -inf
        #Otherwise we'll never intersect eccentricity = inf

        #the sign of the direction to each point dotted with the normal
        #gives us the side of the plane each point is on
        
        to_start = ray.s - self.p
        to_end = ray.e - self.p

        dp_start = to_start.dp( self.n )
        dp_end = to_start.dp( self.n )

        if ((dp_start < 0.0 and dp_end > 0.0) or
            (dp_start > 0.0 and dp_end < 0.0)):
            return -100000000000.0
        return 100000000000.0

    def __repr__(self):
        return "plane(%s, %s, %s)" % ( str(self.p),
                                       str(self.n),
                                       str(self.m) )
        
        
        
        

class sphere:
    def __init__(self, point, radius, mat):
        "Arguments: center point, radius, material"
        self.p = point
        self.r = float(radius)
        self.m = mat

    def collide(self, ray):
        """ Arguments: a ray to collide with
            Returns: a fully contructed collision object
        """
        #sphere: (x - self.p).dp(x - self.p) = self.r**2
        #ray: x = ray.s + t * ray.d
        
        #(ray.s + t*ray.d - self.p).mag_squared() = self.r**2
        #condense to form a * t**2 + b * t + c = 0
        # a = ray.d.dp(ray.d)
        # b = (2*(ray.s-self.p)).dp(ray.d)
        # c = (ray.s - self.p).dp(ray.s - self.p)

        # simplify assumption: ray.d.norm() == 1.0

        coll = collision(ray)
        
        to_sphere = ray.s - self.p 
        b = to_sphere.dp(ray.d)

        #the final expression for t implies that if b is positive
        #t will never be positive which is what we want
        if b > 0.0:
            return coll()
        
        c = to_sphere.mag_squared() - self.r**2

        det = b*b - c
        if det < 0.0:
            return coll()
        
        t = -b - math.sqrt(det)
        if t < 0.0:
            return coll()
        
        return coll(True, self, t)

    def normal(self, point):
        "Returns: normal to this surface at a given point"
        n = point - self.p
        return n.norm()

    def eccentricity(self, ray):
        """Returns: float representing how close the ray is to intersecting
           Notes: modifier is a factor scaled on distance along ray
                  that is subtracted from normal eccentricity
        """
        
        to_sphere = self.p - ray.s
        theta = to_sphere.theta( ray.d )

        #if theta > pi / 2 the two rays are going in opposite directions
        #it's never going to hit us, eccentricity = inf
        if theta > math.pi / 2.0:
            return 100000000000.0

        perp_distance = to_sphere.mag() * math.sin(theta)        

        return perp_distance - self.r

    def fraction_light(self, ray, modifier):
        pass

    def __repr__(self):
        return "sphere(%s, %f, %s)" % ( str(self.p),
                                        self.r,
                                        str(self.m) )

        
