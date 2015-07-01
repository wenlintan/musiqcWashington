import shapes
from vector3 import *

class collider:
    def __init__(self, scene):
        self.scene = scene

    def __call__(self, ray):
        return self.scene.collide(ray)

class scene:
    def __init__(self):
        self.shapes = []
        self.lights = []

        self.collides = []

    def select_collides(self, arr = []):
        "Sets the subset of geometry that will be used in all future operations"
        if not len(arr):
            self.collides = self.shapes
            return
        self.collides = arr

    def get_eccentricities(self, start, end):
        """"Returns: an array of the eccentricities of the contained geometry
            Notes: eccentricity is a number representing how close a ray
                   is to intersecting the object, 0.0 is the edge of the
                   object, more positive numbers indicate we're further
                   from intersection, more negative numbers mean the
                   intersection is less avoidable
        """
        ray = shapes.ray(start, end-start)
        return [ s.eccentricity(ray) for s in self.collides ]

    def get_augmented_eccentricities(self, start, end):
        """Notes: see documentation for get_eccentricities
                  adds the relevant shape to a tuple with the eccentricity
        """
        ray = shapes.ray(start,end-start)
        return [ ( s.eccentricity(ray), s ) for s in self.collides ]

    def is_blocked(self, start, end):
        """Returns: boolean value indicating whether is any geometry between
                    start and end
           Notes: More highly optimized than standard collide
        """
        #be careful with length, ray will normalize its direction
        direct = end - start
        direct_mag2 = direct.mag_squared()

        ray = shapes.ray(start, direct)
        for x in self.collides:
            coll = x.collide(ray)
            if coll and coll.t**2 < direct_mag2:
                return True

        return False
        

    def collide(self, ray):
        "Returns: first intersection along ray"

        #get all of the collisions with geometry
        seq = [ x.collide(ray) for x in self.collides ]

        #select the collision with the smallest t value
        first = min(seq)
        return first

    
        
        
