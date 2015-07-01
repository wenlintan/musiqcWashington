
#include <boost/python.hpp>
#include "renderer_components.hpp"

using namespace boost::python;
void wrap_renderer_components() {
	enum_< TextureData::Precision >( "TextureDataPrecision" )
		.value( "Byte", TextureData::Byte )
		.value( "Float16", TextureData::Float16 )
		.value( "Float32", TextureData::Float32 )
		.value( "Depth32", TextureData::Depth32 )
		;

	class_< TextureData, TextureData::pointer_type, boost::noncopyable >
		( "TextureData", init<const std::string&>() )
		.def( init<unsigned short, unsigned short, unsigned short,
			size_t, TextureData::Precision>() )
		.def_readonly( "w", &TextureData::w )
		.def_readonly( "h", &TextureData::h )
		.def_readonly( "ncomponents", &TextureData::ncomponents )
		.def_readonly( "dimension", &TextureData::dimension )
		.def_readonly( "precision", &TextureData::precision )
		;

	class_< Texture, Texture::pointer_type, bases<Component>,
		boost::noncopyable >( "Texture",
		init< size_t, const TextureData::pointer_type >() )
		.def_readwrite( "flags", &Texture::flags )
		.def_readwrite( "unit", &Texture::unit )
		.def_readwrite( "texture", &Texture::texture )
		;

	class_< Color, Color::pointer_type, bases<Component> >
		( "Color", init< const Vector3f& >() )
		.def_readwrite( "color", &Color::color )
		;

	enum_< Renderbuffer::Type >( "RenderbufferType" )
		.value( "Depth", Renderbuffer::Depth )
		.value( "Stencil", Renderbuffer::Stencil )
		.value( "Color0", Renderbuffer::Color0 )
		;

	enum_< Renderbuffer::Precision >( "RenderbufferPrecision" )
		.value( "Byte", Renderbuffer::Byte )
		.value( "Float16", Renderbuffer::Float16 )
		.value( "Float32", Renderbuffer::Float32 )
		;

	class_< Renderbuffer, Renderbuffer::pointer_type, boost::noncopyable >
		( "Renderbuffer", 
		init<Renderbuffer::Type, TextureData::pointer_type>() )
		.def( init< Renderbuffer::Type, Renderbuffer::Precision,
			unsigned short, unsigned short >() )
		;

	enum_< Framebuffer::Binding >( "FramebufferBinding" )
		.value( "Front", Framebuffer::Front )
		.value( "Back", Framebuffer::Back )
		.value( "Color0", Framebuffer::Color0 )
		;

	class_< Framebuffer, Framebuffer::pointer_type, bases<Component>,
		boost::noncopyable >( "Framebuffer",
		init<unsigned short, unsigned short>() )
		.def( "attach_renderbuffer", &Framebuffer::attach_renderbuffer )
		.def( "set_drawbuffer", &Framebuffer::set_drawbuffer )
		.def_readwrite( "flags", &Framebuffer::flags )
		.def_readwrite( "x", &Framebuffer::x )
		.def_readwrite( "y", &Framebuffer::y )
		;

	class_< ProgramVariable, ProgramVariable::pointer_type, 
		boost::noncopyable >( "ProgramVariable", no_init )
		.def( "float1", &ProgramVariable::float1 )
		.staticmethod( "float1" )
		.def( "float3", &ProgramVariable::float3 )
		.staticmethod( "float3" )
		.def( "int1", &ProgramVariable::int1 )
		.staticmethod( "int1" )
		.def( "mat4", &ProgramVariable::mat4 )
		.staticmethod( "mat4" )
		.def( "transform", &ProgramVariable::transform )
		.staticmethod( "transform" )
		.def( "mesh_attribute", &ProgramVariable::mesh_attribute )
		.staticmethod( "mesh_attribute" )
		;

	class_< Program, Program::pointer_type, bases<Component>,
		boost::noncopyable >( "Program",
		init<const std::string&, const std::string&, const std::string&>() )
		.def( "set_frag_location", &Program::set_frag_location )
		.def( "set_camera_transform", &Program::set_camera_transform )
		.def( "set_variable", &Program::set_variable )
		.def_readwrite( "flags", &Program::flags )
		;

	enum_< Camera::Type >( "CameraType" )
		.value( "Perspective", Camera::Perspective )
		.value( "Ortho", Camera::Ortho )
		;

	class_< Camera, Camera::pointer_type, bases<Component>,
		boost::noncopyable >( "Camera",
		init<float, float, float, float>() )
		.def( init<float, float, float, float, float, float>() )
		.def( "build_matrix", &Camera::build_matrix )

		.def_readwrite( "flags", &Camera::flags )
		.def_readwrite( "type", &Camera::type )
		.def_readwrite( "priority", &Camera::priority )

		.def_readwrite( "fov", &Camera::fov )
		.def_readwrite( "aspect", &Camera::aspect )
		.def_readwrite( "minx", &Camera::minx )
		.def_readwrite( "maxx", &Camera::maxx )
		.def_readwrite( "miny", &Camera::miny )
		.def_readwrite( "maxy", &Camera::maxy )
		.def_readwrite( "nearz", &Camera::nearz )
		.def_readwrite( "farz", &Camera::farz )
		;

	class_< MeshRenderer, MeshRenderer::pointer_type, bases<Component>,
		boost::noncopyable >( "MeshRenderer",
		init<RenderFlags>() )
		.def_readwrite( "flags", &MeshRenderer::flags )
		;

}

ProgramVariable::pointer_type ProgramVariable::float1( float v ) {
	return pointer_type( new ProgramVariable( FLOAT, 1, v ) );
}

ProgramVariable::pointer_type ProgramVariable::float3( const Vector3f& v ) {
	return pointer_type( new ProgramVariable( FLOAT, 3, v.d ) );
}

ProgramVariable::pointer_type ProgramVariable::int1( int v ) {
	return pointer_type( new ProgramVariable( INT, 1, v ) );
}

ProgramVariable::pointer_type ProgramVariable::transform( 
	const Transform& t, bool trans_first ) {
	return pointer_type( 
		new ProgramVariable( FLOAT_MATRIX, 1, 
			t.build_matrix( trans_first ).d ) );
}

ProgramVariable::pointer_type ProgramVariable::mat4( const Matrix4f& t ) {
	return pointer_type( 
		new ProgramVariable( FLOAT_MATRIX, 1, t.d ) );
}

ProgramVariable::pointer_type ProgramVariable::mesh_attribute(
	MeshVertexData::AttributeType type ) {
	return pointer_type( new ProgramVariable( MESH_ATTRIBUTE, 1, type ) );
}

void Program::set_frag_location( const std::string& name, size_t index ) {
	frag_location[ index ] = name;
}

void Program::set_camera_transform( const std::string& name ) {
	camera_transform = name;
}

void Program::set_variable( const std::string& name,
	ProgramVariable::pointer_type var ) {
	variables[ name ] = var;
}

Matrix4f Camera::build_matrix() {
	if( type == Camera::Perspective ) {
		return Matrix4f::perspective( fov, aspect, nearz, farz );
	} else {
		return Matrix4f::ortho( minx, maxx, miny, maxy, nearz, farz );
	}
}
