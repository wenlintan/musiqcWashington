
#include <boost/smart_ptr/shared_ptr.hpp>
#include <map>

#include "vector.hpp"

#include "component.hpp"
#include "transform.hpp"
#include "mesh.hpp"

#pragma once

void wrap_renderer_components();
typedef unsigned int RenderFlags;

struct TextureData {
	typedef boost::shared_ptr<TextureData> pointer_type;
	enum Precision { Byte, Float16, Float32, Depth32 };

	TextureData( const std::string& filename_ ): 
		filename( filename_ ), data( 0 ), texture( -1 )
	{}

	TextureData( unsigned short w_, unsigned short h_, 
		unsigned short nc, size_t dim, Precision prec,
	    unsigned char* data_ = 0	):
		w( w_ ), h( h_ ), ncomponents( nc ), dimension( dim ), 
		precision( prec ), texture( -1 ), data( data_ )
	{}

	std::string filename;
	unsigned short w, h, ncomponents;

	unsigned int texture;
   	size_t dimension;
	Precision precision;
	unsigned char* data;
};

struct Texture: Component {
	typedef boost::shared_ptr< Texture > pointer_type;
	Texture( size_t tex_number, TextureData::pointer_type tdata ):
		Component( Component::Texture ), flags( 0xffffffff ),
		unit( tex_number ), texture( tdata )
	{}

	RenderFlags flags;
	size_t unit;
	TextureData::pointer_type texture;
};

struct Color: Component {
	typedef boost::shared_ptr< Color > pointer_type;
	Color( const Vector3f& c ): Component( Component::Color ), color( c )
	{}

	Vector3f color;
};

struct Screen: Component {
	unsigned short x, y;
	unsigned char bpp;
};

struct Renderbuffer {
	typedef boost::shared_ptr< Renderbuffer > pointer_type;
	enum Type { Depth, Stencil, Color0 };
	enum Precision { Byte, Float16, Float32, Depth32 };

	Renderbuffer( Type type_, TextureData::pointer_type tex ):
		type( type_ ), texture( tex )
	{}

	Renderbuffer( Type type_, Precision prec_, 
			unsigned short x_, unsigned short y_ ):
		type( type_ ), precision( prec_ ), x( x_ ), y( y_ )
	{}

	Type type;
	Precision precision;
	unsigned short x, y;

	TextureData::pointer_type texture;
	unsigned int buffer;
};

struct Framebuffer: Component {
	typedef boost::shared_ptr< Framebuffer > pointer_type;
	enum Binding { Front, Back, Color0 };

	Framebuffer( unsigned short x_, unsigned short y_ ): 
		Component( Component::Framebuffer ), flags( 0xffffffff ),
		x( x_ ), y( y_ ), buffer( -1 )
	{}

	void attach_renderbuffer( Renderbuffer::pointer_type buffer ) {
		render_buffers.push_back( *buffer );
	}

	void set_drawbuffer( size_t index, Binding binding ) {
		if( index >= buffer_types.size() )	buffer_types.resize( index+1 );
		buffer_types[ index ] = binding;
	}

	std::vector< Renderbuffer > render_buffers;
	std::vector< unsigned int > buffer_types;

	RenderFlags flags;
	unsigned short x, y;
	unsigned int buffer;
};

struct ProgramVariable {
	typedef boost::shared_ptr< ProgramVariable > pointer_type;
	enum Type { FLOAT, INT, FLOAT_MATRIX, MESH_ATTRIBUTE };

	template< typename T >
	struct Capture {
		static void apply( ProgramVariable& pv, const T& tdata ) {
			if( sizeof( T ) > sizeof(pv.buffer) )
				pv.data = (void*)(new T( tdata ));
			else {
				new (pv.buffer) T( tdata );
				pv.data = pv.buffer;
			}
		}
	};

	template< typename T, size_t N >
	struct Capture< T[N] > {
		static void apply( ProgramVariable& pv, const T tdata[N] ) {
			if( sizeof( T )* N > sizeof(pv.buffer) )
				pv.data = (void*)(new T[ N ]);
			else pv.data = pv.buffer;

			for( size_t i = 0; i < N; ++i ) {
				new ((void*)(&((T*)pv.data)[i])) T( tdata[i] );
			}
		}
	};

	template< typename T >
	ProgramVariable( Type t, size_t d, const T& tdata ): 
		type( t ), dimension( d ) {
		Capture< T >::apply( *this, tdata );
	}


	~ProgramVariable() {
		if( data != buffer ) {
			if( dimension > 1 || type == FLOAT_MATRIX )
				delete [] data;
			else delete data;
		}
	}

	static pointer_type float1( float v );
	static pointer_type float3( const Vector3f& v );
	static pointer_type int1( int v );
	static pointer_type transform( const Transform& t, bool trans_first );
	static pointer_type mat4( const Matrix4f& t );
	static pointer_type mesh_attribute( 
		MeshVertexData::AttributeType type );

	Type type;
	size_t dimension;

	unsigned char buffer[ sizeof(float)*4 ];
	void* data;
};

struct Program: Component {
	typedef boost::shared_ptr< Program > pointer_type;
	Program( const std::string& vsource, const std::string& fsource,
		const std::string& gsource ): 
		Component( Component::Program ), flags( 0xffffffff ),
		vertex_source( vsource ),
		fragment_source( fsource ), geometry_source( gsource ),
		vertex_shader( -1 )
	{}

	RenderFlags flags;
	std::string vertex_source, fragment_source, geometry_source;
	unsigned int vertex_shader, fragment_shader, geometry_shader;
	unsigned int program;

	enum { MAX_FRAMEBUFFERS = 3 };
	std::string frag_location[ MAX_FRAMEBUFFERS ];
	std::string camera_transform;

	typedef std::map< std::string, ProgramVariable::pointer_type > variable_map;
	variable_map variables;

	void set_frag_location( const std::string& name, size_t index = 0 );
	void set_camera_transform( const std::string& name );
	void set_variable( const std::string& name, 
		ProgramVariable::pointer_type var );
};

struct Camera: Component {
	enum Type { Perspective, Ortho };
	typedef boost::shared_ptr<Camera> pointer_type;

	Camera( float fov_, float aspect_, float nearz_, float farz_ ):
		Component( Component::Camera ), flags( 0x1 ), type( Perspective ),
		fov( fov_ ), aspect( aspect_ ), nearz( nearz_ ), farz( farz_ )
	{}

	Camera( float minx_, float maxx_, float miny_, float maxy_,
		float nearz_, float farz_ ):
		Component( Component::Camera ), flags( 0x1 ), type( Ortho ),
		minx( minx_ ), maxx( maxx_ ), miny( miny_ ), maxy( maxy_ ),
		nearz( nearz_ ), farz( farz_ )
	{}

	Matrix4f build_matrix();

	RenderFlags flags;
	Type type;
	unsigned short priority;

	float fov, aspect, nearz, farz;
	float minx, maxx, miny, maxy;
};

struct MeshRenderer: Component {
	typedef boost::shared_ptr<MeshRenderer> pointer_type;
	MeshRenderer( RenderFlags f_ ): Component( Component::MeshRenderer ), 
		flags( f_ )
	{}

	RenderFlags flags;
};


