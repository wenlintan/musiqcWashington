
src = """
#version 330
uniform float block_size, block_tex_size;
uniform int chunk_size;
uniform sampler3D blocks;
uniform mat4 modelview, projection;
uniform vec3 chunk_position;

in vec3 v, n;
in vec2 t;
out vec2 tex_coord;
out vec3 normal;
out vec4 test;
out vec3 vertex;
flat out int block;

void main() {
    ivec3 block_offset = ivec3(
            gl_InstanceID % chunk_size,
            (gl_InstanceID / chunk_size) % chunk_size,
            (gl_InstanceID / chunk_size / chunk_size)
        );

    vec4 data = texelFetch( blocks, block_offset, 0 );
    block = int(data.a);
    test = vec4(0., 0., 0., 0.);// data.r, 0., data.g, 0. );

    vertex = vec3(block_offset) * block_size + v + chunk_position;
    vertex = vertex * float(block != 4);
    gl_Position = projection * modelview * vec4( vertex, 1.0 );
    
    normal = n;
    tex_coord = vec2( t.x, 1. - (t.y + block_tex_size * block) );
}

--Vertex/Fragment--
#version 330
uniform isampler2D random;
uniform vec3 camera_position;
uniform vec4 cmap[ 6 ] = {
    vec4( 0.2, 0.7, 0.1, 1. ),  vec4( 0.4, 0.25, 0.125, 1. ),
	vec4( 0.9, 0.0, 0.1, 1. ),  vec4( 0.0, 0.25, 0.125, 1. ),
	vec4( 0.2, 0.1, 0.7, 1. ),  vec4( 0.25, 0.4, 0.125, 1. ),
};

uniform vec3 gradients[ 16 ] = {
    vec3( 1., 1., 0. ), vec3( -1., 1., 0. ), vec3( 1., -1., 0. ), vec3( -1., -1., 0. ),
    vec3( 1., 0., 1. ), vec3( -1., 0., 1. ), vec3( 1., 0., -1. ), vec3( -1., 0., -1. ),
    vec3( 0., 1., 1. ), vec3( 0., -1., 1. ), vec3( 0., 1., -1. ), vec3( 0., -1., -1. ),
    vec3( 1., 1., 0. ), vec3( 0., -1., 1. ), vec3( -1., 1., 0. ), vec3( 0., -1., -1. )
};

in vec3 vertex;
in vec2 tex_coord;
in vec3 normal;
in vec4 test;
flat in int block;
out vec4 out_color;

float fade ( float t ) {
    return t * t * t * (t * (t * 6 - 15) + 10);
}

vec3 grad( int h, int y ) {
    return gradients[ texelFetch( random, ivec2( h, y ), 0 ).r & 15 ];
}

float noise2( int y, vec2 point ) {
    int X = int(floor( point.x )) & 255, Y = int(floor( point.y )) & 255;
    vec2 pt = vec2( point.x - floor( point.x ), point.y - floor( point.y ) );

    int A = texelFetch( random, ivec2( X, y ), 0 ).r + Y;
	int B = texelFetch( random, ivec2( X + 1, y ), 0 ).r + Y;

    return mix( 
        mix( 
            dot( grad( A, y ).xy, pt ), 
            dot( grad( B, y ).xy, pt + vec2( -1., 0. ) ), 
            fade(pt.x) ),
        mix( 
            dot( grad( A + 1, y ).xy, pt + vec2( 0., -1. ) ), 
            dot( grad( B + 1, y ).xy, pt + vec2( -1., -1. ) ), 
            fade(pt.x) ),
        fade(pt.y) );
}

float noise3( int y, vec3 point ) {
    int X = int(floor( point.x )) & 255, 
	    Y = int(floor( point.y )) & 255,
        Z = int(floor( point.z )) & 255;
		
    vec3 pt = vec3( 
        point.x - floor( point.x ), 
        point.y - floor( point.y ),
        point.z - floor( point.z ) );

    int A = texelFetch( random, ivec2( X, y ), 0 ).r + Y;
    int B = texelFetch( random, ivec2( X + 1, y ), 0 ).r + Y;
    
    int AA = texelFetch( random, ivec2( A , y ), 0 ).r + Z;
    int AB = texelFetch( random, ivec2( A + 1, y ), 0 ).r + Z;
    int BA = texelFetch( random, ivec2( B, y ), 0 ).r + Z;
    int BB = texelFetch( random, ivec2( B + 1, y ), 0 ).r + Z;

    return mix(
        mix( 
            mix( 
                dot( grad( AA, y ), pt ), 
                dot( grad( BA, y ), pt + vec3( -1., 0., 0. ) ), 
                fade(pt.x) ),
            mix( 
                dot( grad( AB, y ), pt + vec3( 0., -1., 0. ) ), 
                dot( grad( BB, y ), pt + vec3( -1., -1., 0. ) ), 
                fade(pt.x) ),
            fade(pt.y) ),
		mix( 
            mix( 
                dot( grad( AA + 1, y ), pt + vec3( 0., 0., -1. )), 
                dot( grad( BA + 1, y ), pt + vec3( -1., 0., -1. ) ), 
                fade(pt.x) ),
            mix( 
                dot( grad( AB + 1, y ), pt + vec3( 0., -1., -1. ) ), 
                dot( grad( BB + 1, y ), pt + vec3( -1., -1., -1. ) ), 
                fade(pt.x) ),
            fade(pt.y) ),
        fade(pt.z) );
}

float noise( vec3 vertex ) {
    return clamp( 1.5 * noise3( 1, vertex * 0.05 ) + 
	    0.4 * noise3( 1, vertex * 0.5 ) + .2, 0., 1. );
}

uniform float h = 0.001;
void main() {
    vec3 light = camera_position - vertex;
    
    float n = noise( vertex );
    float dx = (n - noise( vertex + vec3( h, 0., 0. ) ) ) / h;
    float dy = (n - noise( vertex + vec3( 0., h, 0. ) ) ) / h;
    float dz = (n - noise( vertex + vec3( 0., 0., h ) ) ) / h;
    vec3 noff = -vec3( dx, dy, dz );
	
    vec4 color = mix( cmap[block * 2], cmap[block*2 + 1], n );
    float dp = dot( normalize(light), normalize(normal + noff) );
    out_color = clamp( dp * 8. / length( light ), 0.2, 1. ) * color + test;
}
"""

update_src = """
#version 330
uniform mat4 modelview, projection;

in vec3 v;
out vec2 tex_coord;

void main() {
    gl_Position = projection * modelview * vec4( v, 1.0 );
    tex_coord = v.xy;
}

--Vertex/Fragment--
#version 330
uniform sampler3D blocks, velocity_blocks;

uniform float dt = 1., scale = 1.;
uniform ivec2 center = ivec2( 16, 16 );

uniform float mass[5] = { 320., 20., 100., 1000., 0. };
uniform ivec3 offsets[4] = { 
	ivec3( -1, 0, 0 ), ivec3( 1, 0, 0 ), ivec3( 0, 1, 0 ), ivec3( 0, -1, 0 ) 
};

in vec2 tex_coord;
out vec4 blocks_out, velocity_out;

bool is_empty( vec4 data ) {
    return abs( data.w - 4. ) < 0.1;
}

void main() {
    ivec3 position = ivec3(tex_coord * scale, 6);
    vec4 data = texelFetch( blocks, position, 0 );
	vec4 velocity = texelFetch( velocity_blocks, position, 0 );
	
	ivec3 offset;
	float m = mass[ int(data.w) ];
	for( int i = 0; i < 4; ++i ) {
		vec4 neighbor = texelFetch( blocks, position + offsets[i], 0 );
		if( !is_empty(neighbor) ) { // If neighbor is not empty
			float neighbor_off = dot( neighbor.xy, vec2(offsets[i].xy) );
			float overlap = dot( data.xy, vec2(offsets[i].xy) ) - neighbor_off;
			
			if( overlap > 0. && !is_empty(data) ) {
				float n = mass[ int(neighbor.w) ];
				data -= vec4(overlap * offsets[i] * n / (m + n), 0);
				velocity = vec4( reflect( velocity.xyz, vec3(offsets[i]) ), 0.);
			}

			if( is_empty(data) ) { // If current block is empty
				offset += ivec3( step( 125., -neighbor_off ) * offsets[i] );
			}
		}
	}
    offset.y *= int( offset.x == 0 );
    
    bool max = any(equal(data.xy, vec2(125, 125)));
    bool min = any(equal(data.xy, vec2(-125, -125)));
	if( bool(offset.x) || bool(offset.y) ) {
		position += offset;
		data = texelFetch( blocks, position, 0 );
		velocity = texelFetch( velocity_blocks, position, 0 );
		data += vec4(offset * 250., 0);

	} else if( max || min ) {
		data.w = 4.;
	}	
	
    float l = length( vec2(position.xy - center) ) + 0.1;
    vec2 gravity = -m * vec2( position.xy - center ) / l / l / l;

	vec2 output = velocity.xy + gravity;
    output = clamp( output, vec2( -125., -125. ), vec2( 125., 125. ) );
	velocity_out = vec4( output, velocity.zw );
	
	output = data.xy + velocity.xy;
    output = clamp( output, vec2( -125., -125. ), vec2( 125., 125. ) );
	if( abs(output.y) == 125. && abs(output.x) == 125. ) {
		output.y -= output.y / abs(output.y) * 0.0001;
	}

	blocks_out = vec4( output, data.zw );
}
"""



