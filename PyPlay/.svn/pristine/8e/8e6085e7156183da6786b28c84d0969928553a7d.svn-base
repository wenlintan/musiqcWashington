
ship_vertex = """
#version 330
uniform mat4 modelviewprojection;

in vec3 vertex;
in vec3 normal;

out vec3 frag_normal;

void main() {
	gl_Position = modelviewprojection * vec4( vertex , 1.0 );
	frag_normal = normal;

}

"""

ship_fragment = """
#version 330
in vec3 frag_normal;
out vec4 out_color;

const vec3 light = normalize( vec3( 0., 1.0, 1.0 ) );
void main() {
	out_color = dot( frag_normal, light ) * vec4( 0.8, 0.8, 0.8, 1.0 );
}

"""

