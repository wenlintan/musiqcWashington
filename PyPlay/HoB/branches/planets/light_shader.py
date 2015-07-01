
light_vertex = """
#version 330
uniform mat4 modelviewprojection;

in vec3 vertex;

void main() {
	gl_Position = modelviewprojection * vec4( vertex , 1.0 );

}

"""

light_fragment = """
#version 330

void main() {
}

"""

