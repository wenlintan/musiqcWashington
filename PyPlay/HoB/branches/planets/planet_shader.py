

from atmos_shader_utils import *

planet_vertex = """
#version 330
uniform mat4 modelviewprojection;

in vec3 vertex;
in vec3 normal;

out vec3 vout;
out vec3 nout;

void main() {
	vout = vertex;
	nout = normal;
	gl_Position = modelviewprojection * vec4( vertex, 1.0 );
}

"""

planet_fragment = """
#version 330

""" + atmos_shader_utils + """

uniform sampler2D dirt;
uniform sampler2D grass;
uniform sampler2D rock;
uniform sampler2D snow;
uniform sampler2DShadow shadow;

uniform mat4 modelviewprojection;
uniform mat4 shadow_transform;

in vec3 vout;
in vec4 gl_FragCoord;

in vec3 nout;
out vec4 color;

void main() {
	vec3 dir = vout - camera;
	dir = dir / length( dir );
	vec2 atmos_endpts = ray_to_sphere( dir, atmos_radius );
	vec2 water_endpts = ray_to_sphere( dir, planet_radius );

	vec3 start = camera;
	if( atmos_endpts.x > 0 )
		start += dir * atmos_endpts.x;

	vec4 atmos_color = atmos_sample( start, vout );

	vec2 tcoord;
	if( abs(vout.z) > abs(vout.x) && abs(vout.z) > abs(vout.y) )
		tcoord = vout.xy*100;
	else if( abs(vout.y) > abs(vout.x) )
		tcoord = vout.xz*100;
	else
		tcoord = vout.yz*100;

	float l = length( vout );
	float nscale = clamp( pow( dot( nout, vout ) / l, 20 ), 0.0, 1.0 );
	float hscale = clamp( (l - 1.0) / 0.0015 + 0.5, 0.0, 1.0 );

	float light = max( dot( nout, sun ), 0.5 );
	
	if( length(camera) < 1.003 ) {
		vec4 lightpos = ( shadow_transform * vec4( vout, 1.0 ) );
		vec3 lookup = ( lightpos.xyz / lightpos.w + vec3( 1.0, 1.0, 1.0 ) ) / 2
			- vec3( 0.0, 0.0, 0.01 );
		light *= texture( shadow, lookup ) + 0.2;
	} 

	vec4 water_pt = modelviewprojection * 
		vec4( camera + dir * water_endpts.x, 1.0 );
	vec4 pt = modelviewprojection * vec4( vout, 1.0 );
	if( water_endpts.x > 0 && water_pt.z / water_pt.w < pt.z / pt.w ) {
		color = max( dot( vout, sun ) / l, 0.5 )  * vec4( .2, .4, .6, 0. );
		return;
	}

	color = atmos_color + light*mix( texture( rock, tcoord ),
		mix( texture( dirt, tcoord ), texture( snow, tcoord ), hscale ),
		nscale );
}
"""

