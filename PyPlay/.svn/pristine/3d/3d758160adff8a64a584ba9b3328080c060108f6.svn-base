
from atmos_shader_utils import *

sky_vertex = """
#version 330

uniform mat4 modelviewprojection;

in vec3 vertex;
out vec3 vout;

void main() {
	vout = vertex;
	gl_Position = modelviewprojection * vec4( vertex, 1.0 );
}
"""


sky_fragment = """
#version 330

""" + atmos_shader_utils + """

in vec3 vout;
out vec4 color_out;

void main() {

	vec3 dir = vout - camera;
	dir = dir / length( dir );
	vec2 endpts = ray_to_sphere( dir, atmos_radius );
	if( endpts.x == endpts.y )
		discard;

	vec3 start = camera;
	if( endpts.x > 0 )
		start += dir * endpts.x;

	color_out = atmos_sample( start, camera + dir * endpts.y );
/*
	vec3 end = camera + dir * endpts.y;
	float dist = length( end - start );

	float sample_dist = dist / nsamples;
	float scaled_dist = sample_dist * scale;
	vec3 pt = start + dir * 0.5 * sample_dist,
		sample_ray = dir * sample_dist;

	float start_angle = dot( dir, start ) / length(start);
	float start_depth = exp( scale_over_scale_depth *
		(planet_radius - length(start)));
	float start_offset = start_depth * scalefn( start_angle );

	vec3 color = vec3( 0., 0., 0. );
	for( int i = 0; i < nsamples; ++i ) {
		float height = length( pt );
		float depth = exp( scale_over_scale_depth * 
			(planet_radius - height) );
		float light = dot( sun, pt ) / height;
		float cam = dot( dir, pt ) / height;

		float scatter = start_offset + depth * 
			( scalefn(light) - scalefn(cam) );
		vec3 atten = exp( -scatter * 
			(oolambda4 * k_rayleigh_4pi + k_mie_4pi) );
		color += atten * depth * scaled_dist;
		pt += sample_ray;
	}

	float cosangle = dot( sun, -dir );
	color_out = vec4(
		phase( cosangle, 0.0 ) * color * oolambda4 * k_rayleigh * E_sun +
		phase( cosangle, g ) * color * k_mie * E_sun, 1.0 );
*/
	// HDR
	color_out = 1.0 - exp( color_out * -1.0 );
}

"""
