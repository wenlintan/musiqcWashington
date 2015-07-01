

tile_vertex = """
#version 330
uniform mat4 modelviewprojection;

in vec2 tcoord0;
in vec3 vertex;
in vec4 color;

out vec2 tcoord0_int;
out vec4 color_int;

void main() {
	gl_Position = modelviewprojection * vec4( vertex , 1.0 );
	tcoord0_int = tcoord0;
	color_int = color;
}

"""

tile_fragment = """
#version 330
uniform sampler2D tileset;

in vec2 tcoord0_int;
in vec4 color_int;
out vec4 out_color;

uniform int draw_colors;

void main() {
	out_color = texture( tileset, tcoord0_int );
	if( draw_colors != 0 ) {
		out_color *= vec4( color_int.rgb, 1.0 ) * color_int.a +
			vec4( out_color.rgb, 1.0 ) * ( 1. - color_int.a );
	}
}

"""

