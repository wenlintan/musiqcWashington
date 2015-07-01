
import numpy
from numpy import arccos, cos, sin, dot, log, exp, sqrt

atmos_radius, planet_radius = 1.1, 1.0
scale = 1.0 / (atmos_radius - planet_radius)
rayleigh_scale_depth = 0.25;


def ray_to_sphere( pos, dir, radius ):
    b = 2.0 * dot( pos, dir );
    c = dot( pos, pos ) - radius * radius;

    det = b*b - 4.0 * c;
    if( det < 0. ):
        return None

    return 0.5 * ( -b - sqrt(det) ), 0.5 * ( -b + sqrt(det) )

resolution = 100
nsamples = 50
lookup = numpy.zeros( (resolution, resolution) )
dr_lookup = numpy.zeros( (resolution, resolution) )

for astep in range( resolution ):
    anglecos = 1.0 - 2.0*astep / resolution
    angle = arccos( anglecos )

    dir = numpy.array(( sin(angle), cos(angle), 0.0 ))
    for hstep in range( resolution ):
        height = planet_radius + (atmos_radius - planet_radius)* \
            hstep / resolution + 1e-6
        pos = numpy.array(( 0.0, height, 0.0 ))

        to_planet = ray_to_sphere( pos, dir, planet_radius )
        if to_planet is None or (to_planet[0] < 0. and to_planet[1] < 0.):
            density_ratio = exp( -(height-planet_radius) * scale /
                rayleigh_scale_depth )
        else:
            density_ratio = 0.75 * dr_lookup[ astep-1, hstep ]
        dr_lookup[ astep, hstep ] = density_ratio

        to_atmos = ray_to_sphere( pos, dir, atmos_radius )
        sample_length = to_atmos[1] / nsamples
        scaled_sample = scale * sample_length;

        step = dir * sample_length
        pt = pos + step * 0.5

        rayleigh_depth = 0.0
        for i in range(nsamples):
            height = sqrt( dot( pt, pt ) )
            scale_height = max( 0.0, (height - planet_radius) * scale )
            rayleigh_depth += exp( -scale_height / rayleigh_scale_depth )
            pt += step
        rayleigh_depth *= scaled_sample

        lookup[ astep, hstep ] = log(density_ratio)+rayleigh_depth

from matplotlib.pyplot import *

#hs = 1.0 - 2.0 * numpy.array( list(range(100)) ) / 100.0
hs = numpy.array( list(range(100)) )

#for point in range( 0, 100, 10 ):
#   plot( hs, lookup[ point, : ] / lookup[ point, 0 ] )
#plot( hs, exp( -5*hs ), 'o' )
plot( hs, lookup[ :, 5 ] )

f = numpy.polyfit( hs, lookup[ :, 5 ], 4 )
print( f )
plot( hs, numpy.polyval( f, hs ) )
show()
            

            
