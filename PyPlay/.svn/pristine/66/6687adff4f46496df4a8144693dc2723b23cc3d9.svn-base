from vector3 import *
from random import *
import shapes

class light(object):
    def __init__(self, point, d_falloff, diffuse, specular):
        "Arguments: center point, diffuse component"
        self.p = point
        self.fall = float(d_falloff)
        self.diff = diffuse / 255.0
        self.spec = specular / 255.0

class point_light(light):
    def __init__(self, point, d_falloff, diffuse, specular):
        super(point_light,self).__init__(point, d_falloff, diffuse, specular)

        #point lights may give aliasing contributions
        #because they try to generate hard lines
        self.alias_contributor = True
        
    def get_shade(self, scene, point):
        """Returns: shade factor that should be used for all contributions
                    from this light
        """

        #point source, either all visible or all not
        if scene.is_blocked(point, self.p):
            return 0.0
        return 1.0

class square_light(light):
    dimension_shade = 8
    def __init__(self, point, width, depth, d_falloff, diffuse, specular):
        """Arguments: self, point of front left, width, depth,
                      distance falloff term,
                      diffuse component, specular component
        """

        #store all of the important things
        super(square_light,self).__init__(point, d_falloff, diffuse, specular)
        self.w = float(width)
        self.d = float(depth)

        #compute the interval between points
        self.dx = self.w / float(square_light.dimension_shade)
        self.dz = self.d / float(square_light.dimension_shade)

        #determine the contribution from each precomputed point
        self.contribution = 1.0 / float(square_light.dimension_shade)**2

        #we already smooth around this light, it doesn't get aliased
        self.alias_contributor = False

    def get_shade(self, scene, point):
        """Returns: shade factor that should be used for all contributions
                    from this light
        """
        shade = 0.0

        #use eccentricities to determine if we're likely to hit anything
        self_ecc = math.sqrt( self.w**2 + self.d**2 )
        eccs = scene.get_augmented_eccentricities(point, self.p)

        #try to get out of here quickly
        min_eccs = min(eccs)

        #if the minimum eccentricity is less than ours then no part
        #of the light will be blocked
        if min_eccs[0] > self_ecc:
            return 1.0

        #if the minimum eccentricity is less than the negation of ours
        #we'll never make it positive, all light will be blocked
        if min_eccs[0] < -self_ecc:
            return 0.0

        #regardless we only need to collide our many light rays with
        #geometry that could possibly intersect them
        necessary = [x[1] for x in eccs if x[0] < self_ecc and x[0] > -self_ecc]
        scene.select_collides( necessary )

        #compute some points around out point intervals based on a random factor
        points = [ self.p + vector3( self.dx*x + random() * self.dx,
                                     0.0,
                                     self.dz*z + random() * self.dz )
                   for z in range(square_light.dimension_shade)
                   for x in range(square_light.dimension_shade) ]

        #check each precomputed point to see if have sight of point
        #get approximate fraction of light visible from point
        for light_point in points:
            if not scene.is_blocked( point, light_point ):
                shade += self.contribution

        #reset scene to collide with everything
        scene.select_collides()

        return shade
        

class material:
    ambient = vector3()
    specular_falloff = 3.0
    def __init__(self, emissive, ambient, diffuse, specular, shiny, reflective):
        """Arguments:
            1. Emissive component of object color
            2. Diffuse component
            3. Specular component
            4. Shininess constant for specular
            4. Constant of reflection
        """
        self.emis = emissive / 255.0
        self.ambi = ambient / 255.0
        self.diff = diffuse / 255.0
        self.spec = specular / 255.0
        self.shiny = int(shiny)     #we're using this as an exp, keep it an int
        self.refl = float(reflective)

    def color(self, scene, collision, camera):
        """Arguments: scene containing all geometry and lighting,
                      collision object containing information
                          about the impact on this surface
        """
        if not collision:
            return (0.0, 0.0, 0.0)     

        #info used to constuct final stored info struct
        #info struct can be check to see if pixels are on a boundary
        #to use supersampling anti-aliasing only when necessary
        num_lights = 0
        refl_info = None

        #base color is the emissive
        color = self.emis

        #add ambient, no falloff or anything
        color += self.ambient.component_mult( self.ambi )

        #need to pull out a little to avoid colliding
        #with surface that this point is on
        surface_norm = collision.surf.normal( collision.point )
        collision.point += surface_norm * 0.0001

        to_camera = (camera - collision.point).norm()

        #other light components must be done independently for each light
        for light in scene.lights:
            #check the angles because that's the cheapest
            #nothing's going to happen if we're on the wrong side of surface
            to_light = (light.p - collision.point).norm()
            dp = to_light.dp(surface_norm)

            if dp < 0.0:
                continue
            
            #check to see if this light is visible from current point
            #back out if have collision betweeen source and light
            shade = light.get_shade( scene, collision.point )
            if shade < 0.01:
                continue

            #num_lights is used in the info struct that deals
            #with anti-aliasing, if the light doesn't affect this ignore it
            if light.alias_contributor:
                num_lights += 1

            #add diffuse, falloff on angle from light and distance
            diff_factor = max( 0.0, to_light.dp(surface_norm) ) * shade
            color += light.diff.component_mult(self.diff) * diff_factor

            #specular factor will be computed based on dot product
            #between normal and vector halfway between
            #vector to light and vector to camera

            #this means the closers the object is to directly reflecting
            #the light into the camera the higher the specular factor
            #which is exactly what we want
            ideal_reflect = (to_camera + to_light).norm()

            spec_factor = max( 0.0, ideal_reflect.dp(surface_norm) )
            spec_factor = (spec_factor ** self.shiny) * shade
            color += light.spec.component_mult(self.spec) * spec_factor

        if self.refl > 0.0:
            #reflect ray by subtracting twice the ray projected onto
            #the normal, this essentially reverses its direction relative
            #to the normal while leaving the rest intact
            #which is what we want
            
            ray_onto_norm = surface_norm * collision.ray.d.dp(surface_norm)
            reflected = collision.ray.d - (ray_onto_norm * 2.0)
            reflect_ray = shapes.ray( collision.point, reflected )

            ref_collide = scene.collide( reflect_ray )
            ref_color = ref_collide.surf.m.color(scene, ref_collide, camera )
            ref_color = ref_color / 255.0

            refl_info = ref_collide.surf.m.info

            color *= (1.0-self.refl)
            color += ref_color * self.refl

        # set our info struct so it can be read if desired
        self.info = (collision.surf, num_lights, refl_info)
        color.cut_max(1.0)
        color = color * 255.0
        return color



        
