
atmos_shader_utils = """

const vec3 oolambda4 = vec3( 
	1.0 / pow( 0.650, 4. ),		// 650nm red
	1.0 / pow( 0.570, 4. ),		// 570nm green
	1.0 / pow( 0.475, 4. )		// 475nm blue
	);

const float rayleigh_scale_depth = 0.25;
const float mie_scale_depth = 0.1;

const float pi = 3.141592654;
const float k_rayleigh = 0.0025, k_mie = 0.0015;
const float k_rayleigh_4pi = k_rayleigh * 4 * pi, 
	k_mie_4pi = k_mie * 4 * pi;

const float E_sun = 15.0;
const float g = -0.95;

const int nsamples = 2;

//Should all be uniforms
uniform vec3 camera;
const vec3 planet = vec3(0.0, 0.0, 0.0);
uniform vec3 sun;
const float atmos_radius = 1.025, planet_radius = 1.0;

vec2 ray_to_sphere( const vec3 dir, const float radius ) {
	float b = 2.0 * dot( camera, dir );
	float c = dot( camera, camera ) - radius * radius;

	float det = b*b - 4.0 * c;
	if( det < 0. )
		return vec2(0., 0.);

	return vec2( 0.5 * ( -b - sqrt(det) ), 0.5 * ( -b + sqrt(det) ) );
}

float phase( float cosangle, float g ) {
	return 1.5 * (1 - g*g) / (2 + g*g) *
		(1 + cosangle*cosangle) /
		pow( 1 + g*g - 2 * g * cosangle, 1.5 );
}

float scalefn( float cos ) {
	//return -0.07745579*x*x*x*x + 0.03725586*x*x*x +
	//	0.83301755*x*x - 2.05222169*x + 2.22611096;
	//return -2.77507685*x*x*x*x + 0.11062549*x*x*x +
	//	9.01117222*x*x - 10.10260862*x + 4.62164229;
	float x = 1.0 - cos;
	return rayleigh_scale_depth * 
		exp(-0.00287 + x*(0.459 + x*(3.83 + x*(-6.80 + x*5.25))));
}

const float scale = 1.0 / (atmos_radius - planet_radius);
const float scale_over_scale_depth = scale / rayleigh_scale_depth;

vec4 atmos_sample( vec3 start, vec3 end ) {
	vec3 dir = normalize( end - start );
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

		float scatter = abs( start_offset + depth * 
			( scalefn(light) - scalefn(cam) ) );
		vec3 atten = exp( -scatter * 
			(oolambda4 * k_rayleigh_4pi + k_mie_4pi) );
		color += atten * depth * scaled_dist;
		pt += sample_ray;
	}

	float cosangle = dot( sun, -dir );
	return vec4(
		phase( cosangle, 0.0 ) * color * oolambda4 * k_rayleigh * E_sun +
		phase( cosangle, g ) * color * k_mie * E_sun, 1.0 );
}

"""

