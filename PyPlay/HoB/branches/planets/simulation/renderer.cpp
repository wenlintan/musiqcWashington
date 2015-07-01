
#ifdef WIN32
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#pragma comment( lib, "opengl32.lib" )
#pragma comment( lib, "glu32.lib" )
#endif

#include <sdl.h>
#include <gl/gl.h>
#include <gl/glu.h>

//#define GL_GLEXT_PROTOTYPES
#include "glext.h"

// Something up there is defining this crap ... Idiotic
#undef min
#undef max

#pragma warning( disable: 4996 )
#include <algorithm>

#include <boost/python.hpp>
#include <boost/assign/list_of.hpp>

#include "renderer.hpp"


using namespace boost::python;
void wrap_renderer() {
	class_< ScreenSystem, ScreenSystem::pointer_type, bases<System>,
		boost::noncopyable >( "ScreenSystem",
		init<const unsigned short, const unsigned short>() )
		.def( "begin", &ScreenSystem::begin )
		.def( "update", &ScreenSystem::update )
		.def( "end", &ScreenSystem::end )

		.def_readwrite( "has_multitexture", &ScreenSystem::use_multitexture )
		.def_readwrite( "has_fbos", &ScreenSystem::use_fbos )
		.def_readwrite( "has_shaders", &ScreenSystem::use_shaders )
		;

	class_< MeshRendererSystem, MeshRendererSystem::pointer_type,
		bases<System>, boost::noncopyable>( "MeshRendererSystem" )
		.def( "update", &MeshRendererSystem::update )
		;
}

////////////////////////////////////////////////////////////////////////////////////////
//extension functions
PFNGLACTIVETEXTUREARBPROC				glActiveTextureARB;
PFNGLMULTITEXCOORD2FARBPROC				glMultiTexCoord2fARB;
PFNGLMULTITEXCOORD2FVARBPROC			glMultiTexCoord2fvARB;
PFNGLCLIENTACTIVETEXTUREARBPROC			glClientActiveTextureARB;

PFNGLBINDRENDERBUFFEREXTPROC			glBindRenderbufferEXT;
PFNGLDELETERENDERBUFFERSEXTPROC			glDeleteRenderbuffersEXT;
PFNGLGENRENDERBUFFERSEXTPROC			glGenRenderbuffersEXT;
PFNGLRENDERBUFFERSTORAGEEXTPROC			glRenderbufferStorageEXT;

PFNGLBINDFRAMEBUFFEREXTPROC				glBindFramebufferEXT;
PFNGLDELETEFRAMEBUFFERSEXTPROC			glDeleteFramebuffersEXT;
PFNGLGENFRAMEBUFFERSEXTPROC				glGenFramebuffersEXT;
PFNGLCHECKFRAMEBUFFERSTATUSEXTPROC		glCheckFramebufferStatusEXT;

PFNGLFRAMEBUFFERTEXTURE2DEXTPROC		glFramebufferTexture2DEXT;
PFNGLFRAMEBUFFERRENDERBUFFEREXTPROC		glFramebufferRenderbufferEXT;
PFNGLDRAWBUFFERSPROC					glDrawBuffers;

PFNGLCREATEPROGRAMOBJECTARBPROC			glCreateProgramObjectARB;
PFNGLCREATESHADEROBJECTARBPROC			glCreateShaderObjectARB;
PFNGLSHADERSOURCEARBPROC				glShaderSourceARB;
PFNGLCOMPILESHADERARBPROC				glCompileShaderARB;
PFNGLATTACHOBJECTARBPROC				glAttachObjectARB;
PFNGLLINKPROGRAMARBPROC					glLinkProgramARB;
PFNGLUSEPROGRAMOBJECTARBPROC			glUseProgramObjectARB;
PFNGLBINDFRAGDATALOCATIONEXTPROC		glBindFragDataLocationEXT;
PFNGLDELETEOBJECTARBPROC				glDeleteObjectARB;
PFNGLGETINFOLOGARBPROC					glGetInfoLogARB;

PFNGLUNIFORM1IARBPROC					glUniform1iARB;
PFNGLUNIFORM1IVARBPROC					glUniform1ivARB;
PFNGLUNIFORM1FARBPROC					glUniform1fARB;
PFNGLUNIFORM1FVARBPROC					glUniform1fvARB;
PFNGLUNIFORM3FARBPROC					glUniform3fARB;
PFNGLUNIFORM3FVARBPROC					glUniform3fvARB;
PFNGLUNIFORMMATRIX4FVARBPROC			glUniformMatrix4fvARB;
PFNGLGETUNIFORMLOCATIONARBPROC			glGetUniformLocationARB;

PFNGLVERTEXATTRIB3FARBPROC				glVertexAttrib3fARB;
PFNGLVERTEXATTRIB3FVARBPROC				glVertexAttrib3fvARB;
PFNGLVERTEXATTRIBPOINTERARBPROC			glVertexAttribPointerARB;
PFNGLDISABLEVERTEXATTRIBARRAYARBPROC	glDisableVertexAttribArrayARB;
PFNGLENABLEVERTEXATTRIBARRAYARBPROC		glEnableVertexAttribArrayARB;
PFNGLGETATTRIBLOCATIONARBPROC			glGetAttribLocationARB;

struct ScreenSystemInternals {
	SDL_Window* window;
	SDL_GLContext context;
};

ScreenSystem::ScreenSystem( 
	const unsigned short x_, const unsigned short y_ ): 
	x( x_ ), y( y_ ) {

	int flags = SDL_INIT_VIDEO | SDL_INIT_TIMER | SDL_INIT_NOPARACHUTE;
	if( SDL_Init( flags ) == -1 ) {
		std::cerr << "Could not initialize SDL" << std::endl;
		return;
	}

	SDL_GL_SetAttribute(SDL_GL_RED_SIZE, 8);
	SDL_GL_SetAttribute(SDL_GL_BLUE_SIZE, 8);
	SDL_GL_SetAttribute(SDL_GL_GREEN_SIZE, 8);
	SDL_GL_SetAttribute(SDL_GL_ALPHA_SIZE, 8);

	SDL_GL_SetAttribute(SDL_GL_DOUBLEBUFFER, 1);
	SDL_GL_SetAttribute(SDL_GL_DEPTH_SIZE, 16);

	//surface = SDL_SetVideoMode( x, y, 32, SDL_OPENGL );
	internals = new ScreenSystemInternals();
	internals->window = SDL_CreateWindow( "Title", 
		SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, x, y, 
		SDL_WINDOW_OPENGL | SDL_WINDOW_RESIZABLE );
	if( !internals->window ) {
		std::cerr << "Could not create surface" << std::endl;
		std::cerr << SDL_GetError() << std::endl;
		return;
	}

	internals->context = SDL_GL_CreateContext(internals->window);
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

	//load opengl multitexturing extensions
#define LOAD(type, name)	name = (type) SDL_GL_GetProcAddress(#name)
#ifndef NO_MULTITEX
	LOAD(PFNGLACTIVETEXTUREARBPROC,				glActiveTextureARB);
	LOAD(PFNGLMULTITEXCOORD2FARBPROC,			glMultiTexCoord2fARB);
	LOAD(PFNGLMULTITEXCOORD2FVARBPROC,			glMultiTexCoord2fvARB);
	LOAD(PFNGLCLIENTACTIVETEXTUREARBPROC,		glClientActiveTextureARB);

	use_multitexture = 
		glActiveTextureARB && glMultiTexCoord2fARB && glMultiTexCoord2fvARB &&
		glClientActiveTextureARB;
#else
	use_multitexture = false;
#endif

	//load opengl fbo extensions
#ifndef NO_FBO
	LOAD(PFNGLBINDRENDERBUFFEREXTPROC,			glBindRenderbufferEXT);
	LOAD(PFNGLDELETERENDERBUFFERSEXTPROC,		glDeleteRenderbuffersEXT);
	LOAD(PFNGLGENRENDERBUFFERSEXTPROC,			glGenRenderbuffersEXT);
	LOAD(PFNGLRENDERBUFFERSTORAGEEXTPROC,		glRenderbufferStorageEXT);

	LOAD(PFNGLBINDFRAMEBUFFEREXTPROC,			glBindFramebufferEXT);
	LOAD(PFNGLDELETEFRAMEBUFFERSEXTPROC,		glDeleteFramebuffersEXT);
	LOAD(PFNGLGENFRAMEBUFFERSEXTPROC,			glGenFramebuffersEXT);
	LOAD(PFNGLCHECKFRAMEBUFFERSTATUSEXTPROC,	glCheckFramebufferStatusEXT);

	LOAD(PFNGLFRAMEBUFFERTEXTURE2DEXTPROC,		glFramebufferTexture2DEXT);
	LOAD(PFNGLFRAMEBUFFERRENDERBUFFEREXTPROC,	glFramebufferRenderbufferEXT);
	LOAD(PFNGLDRAWBUFFERSPROC,					glDrawBuffers);

	use_fbos = 
		glBindRenderbufferEXT && glDeleteRenderbuffersEXT && 
		glGenRenderbuffersEXT && glRenderbufferStorageEXT && 
		glBindFramebufferEXT && glDeleteFramebuffersEXT &&
		glGenFramebuffersEXT && glCheckFramebufferStatusEXT && 
		glFramebufferTexture2DEXT && glFramebufferRenderbufferEXT && 
		glDrawBuffers;
#else
	use_fbos = false;
#endif

	//load opengl shader extensions
#ifndef NO_SHADERS
	LOAD(PFNGLCREATEPROGRAMOBJECTARBPROC,		glCreateProgramObjectARB);
	LOAD(PFNGLCREATESHADEROBJECTARBPROC,		glCreateShaderObjectARB);
	LOAD(PFNGLSHADERSOURCEARBPROC,				glShaderSourceARB);
	LOAD(PFNGLCOMPILESHADERARBPROC,				glCompileShaderARB);
	LOAD(PFNGLATTACHOBJECTARBPROC,				glAttachObjectARB);
	LOAD(PFNGLLINKPROGRAMARBPROC,				glLinkProgramARB);
	LOAD(PFNGLUSEPROGRAMOBJECTARBPROC,			glUseProgramObjectARB);
	LOAD(PFNGLBINDFRAGDATALOCATIONEXTPROC,		glBindFragDataLocationEXT);
	LOAD(PFNGLDELETEOBJECTARBPROC,				glDeleteObjectARB);
	LOAD(PFNGLGETINFOLOGARBPROC,				glGetInfoLogARB);

	
	LOAD(PFNGLUNIFORM1IARBPROC,					glUniform1iARB);
	LOAD(PFNGLUNIFORM1IVARBPROC,				glUniform1ivARB);
	LOAD(PFNGLUNIFORM1FARBPROC,					glUniform1fARB);
	LOAD(PFNGLUNIFORM1FVARBPROC,				glUniform1fvARB);
	LOAD(PFNGLUNIFORM3FARBPROC,					glUniform3fARB);
	LOAD(PFNGLUNIFORM3FVARBPROC,				glUniform3fvARB);
	LOAD(PFNGLUNIFORMMATRIX4FVARBPROC,			glUniformMatrix4fvARB);
	LOAD(PFNGLGETUNIFORMLOCATIONARBPROC,		glGetUniformLocationARB);

	LOAD(PFNGLVERTEXATTRIB3FARBPROC,			glVertexAttrib3fARB);
	LOAD(PFNGLVERTEXATTRIB3FVARBPROC,			glVertexAttrib3fvARB);
	LOAD(PFNGLVERTEXATTRIBPOINTERARBPROC,		glVertexAttribPointerARB);
	LOAD(PFNGLDISABLEVERTEXATTRIBARRAYARBPROC,	glDisableVertexAttribArrayARB);
	LOAD(PFNGLENABLEVERTEXATTRIBARRAYARBPROC,	glEnableVertexAttribArrayARB);
	LOAD(PFNGLGETATTRIBLOCATIONARBPROC,			glGetAttribLocationARB);

	use_shaders =	
		glCreateProgramObjectARB && glCreateShaderObjectARB &&  
		glShaderSourceARB && glCompileShaderARB && glAttachObjectARB && 
		glLinkProgramARB && glUseProgramObjectARB && glDeleteObjectARB && 
		glGetInfoLogARB && glUniform3fARB && glUniform3fvARB && 
		glGetUniformLocationARB && glVertexAttrib3fARB && 
		glVertexAttrib3fvARB && glVertexAttribPointerARB && 
		glDisableVertexAttribArrayARB && glEnableVertexAttribArrayARB &&
		glGetAttribLocationARB;
#else
	use_shaders = false;
#endif

	glMatrixMode( GL_PROJECTION );
	glLoadIdentity();

	glMatrixMode( GL_MODELVIEW );
	glLoadIdentity();

	glClearColor( 0.0f, 0.0f, 0.0f, 0.0f );
	glClearDepth( 1.0f );
	glColor4f( 1.0f, 1.0f, 1.0f, 1.0f );

	//glEnable( GL_LINE_SMOOTH );
	//glEnable( GL_POLYGON_SMOOTH );
	glLineWidth( 0.25f );
	//glPolygonMode( GL_FRONT_AND_BACK, GL_LINE );
	glPolygonMode( GL_FRONT_AND_BACK, GL_FILL );

	glDepthFunc( GL_LESS );
	glShadeModel( GL_SMOOTH /*GL_FLAT*/ );
	glHint( GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST );
	
	glEnable( GL_DEPTH_TEST );
	glEnable( GL_TEXTURE_2D );

	//glFrontFace( GL_CCW );
	//glCullFace( GL_BACK );
	//glEnable( GL_CULL_FACE );

	glDisable( GL_LIGHTING );
	glViewport( 0, 0, x, y );

	//when we enable blending this is the function we want
	glDisable( GL_BLEND );
	glBlendFunc( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA );

}

ScreenSystem::~ScreenSystem() {
	SDL_GL_DeleteContext( internals->context );
	SDL_Quit();
	delete internals;
}

void ScreenSystem::begin() {
	glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT );
}

void ScreenSystem::update( Entity::pointer_type ent ) {
	if( !ent->has_component( Component::Transform ) ) return;
	if( !ent->has_component( Component::Camera ) ) return;

	Transform& t = ent->transform();
	Camera& camera = static_cast<Camera&>(
		ent->get_component( Component::Camera ) );


	//std::cout << "Matrix" << std::endl;
	//for( size_t i = 0; i < 16; ++i ) {
	//	std::cout << m[i] << " " << t.transform[i] << std::endl;
	//}
}

void ScreenSystem::end() {
	SDL_GL_SwapWindow( internals->window );
}

//C++11 Hack
template< typename T >
std::map< MeshVertexData::AttributeDataType, int > wrap_map_type( const T& t ){
	std::map<MeshVertexData::AttributeDataType, int> mt = t;
	return mt;
}

std::map< MeshVertexData::AttributeDataType, int > 
	BaseRendererSystem::gl_type_map = 
		wrap_map_type( boost::assign::map_list_of
		(MeshVertexData::FLOAT, GL_FLOAT)
		(MeshVertexData::USHORT, GL_UNSIGNED_SHORT)
		(MeshVertexData::UCHAR, GL_UNSIGNED_BYTE) );

void BaseRendererSystem::load_texture( TextureData& data ) {
	GLenum targets[3] = {GL_TEXTURE_1D, GL_TEXTURE_2D, GL_TEXTURE_3D};

	glGenTextures( 1, &data.texture );
	glBindTexture( GL_TEXTURE_2D, data.texture );

	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);

	if( data.filename.length() ) {
		SDL_Surface* tex = SDL_LoadBMP( data.filename.c_str() );
		data.w = tex->w;
		data.h = tex->h;
		data.ncomponents = tex->format->BytesPerPixel;
		data.dimension = 2;

		GLenum format;
		if( data.ncomponents == 4 ) {
			if( tex->format->Rmask == 0x000000ff )
				format = GL_RGBA;
			else format = GL_BGRA;
		} else if( data.ncomponents == 3 ) {
			if( tex->format->Rmask == 0x000000ff )
				format = GL_RGB;
			else format = GL_BGR;
		} else {
			std::cerr << "Failed to load texture: " << 
				data.filename << std::endl;
			return;
		}

		glTexImage2D( GL_TEXTURE_2D, 0, data.ncomponents, data.w, data.h, 0, 
			format, GL_UNSIGNED_BYTE, tex->pixels );
		SDL_FreeSurface( tex );
	} else {
		GLenum format, internal_format;
		switch( data.precision ) {
			case Renderbuffer::Byte:	
				format = internal_format = GL_RGBA; 
				break;
			case Renderbuffer::Float16:	
				format = GL_RGBA16F_ARB; 
				internal_format = GL_RGBA;
				break;
			case Renderbuffer::Float32:	
				format = GL_RGBA32F_ARB; 
				internal_format = GL_RGBA;
				break;
			case Renderbuffer::Depth32:
				format = GL_DEPTH_COMPONENT;
				internal_format = GL_DEPTH_COMPONENT32_ARB;
				glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S,
					GL_CLAMP );
				glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T,
					GL_CLAMP );
				glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_COMPARE_MODE, 
					GL_COMPARE_R_TO_TEXTURE );
				glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_COMPARE_FUNC,
					GL_LESS );
				glTexParameteri( GL_TEXTURE_2D, GL_DEPTH_TEXTURE_MODE,
					GL_INTENSITY );
				break;
			default:	break;
		}

		if( data.data ) {
			glTexImage2D( GL_TEXTURE_2D, 0, internal_format, 
				data.w, data.h, 0, format, GL_UNSIGNED_BYTE, data.data );
		} else {
			glTexImage2D( GL_TEXTURE_2D, 0, internal_format, 
				data.w, data.h, 0, format, GL_FLOAT, 0 );
		}
				
	}
}

void BaseRendererSystem::bind_texture( Texture& texture ) {
	GLenum targets[3] = {GL_TEXTURE_1D, GL_TEXTURE_2D, GL_TEXTURE_3D};
	glEnable( GL_TEXTURE_2D );

	if( !texture.texture ) {
		glActiveTextureARB( GL_TEXTURE0 + (GLuint)texture.unit );
		glBindTexture( GL_TEXTURE_2D/*TODO find real dimension*/, 0 );
		return;
	}

	if( texture.texture->texture == -1 )
		load_texture( *texture.texture );

	glActiveTextureARB( GL_TEXTURE0 + (GLuint)texture.unit );
	glBindTexture( targets[texture.texture->dimension-1],
		texture.texture->texture );
}

void BaseRendererSystem::create_rbo( Renderbuffer& rb ) {
	switch( rb.type ) {
	case Renderbuffer::Depth:
		std::cout << "Creating depth rbo." << std::endl;
		if( !rb.texture ) {
			glGenRenderbuffersEXT( 1, &rb.buffer );
			glBindRenderbufferEXT( GL_RENDERBUFFER_EXT, rb.buffer );

			glRenderbufferStorageEXT( GL_RENDERBUFFER_EXT,
				GL_DEPTH_COMPONENT, rb.x, rb.y );
			glFramebufferRenderbufferEXT( GL_FRAMEBUFFER_EXT,
				GL_DEPTH_ATTACHMENT_EXT, GL_RENDERBUFFER_EXT,
				rb.buffer );
		} else {
			std::cout << "Creating depth texture rbo." << std::endl;
			if( rb.texture->texture == -1 ) {
				std::cout << "Loading texture." << std::endl;
				load_texture( *rb.texture );
			}

			glFramebufferTexture2DEXT( GL_FRAMEBUFFER_EXT,
				GL_DEPTH_ATTACHMENT_EXT, GL_TEXTURE_2D,
				rb.texture->texture, 0 );
		}
		break;
	case Renderbuffer::Stencil:
		break;
	default: {
		GLenum attach = GL_COLOR_ATTACHMENT0_EXT + 
			(rb.type - Renderbuffer::Color0);
		if( !rb.texture ) {
			glGenRenderbuffersEXT( 1, &rb.buffer );
			glBindRenderbufferEXT( GL_RENDERBUFFER_EXT, rb.buffer );

			GLenum target;
			switch( rb.precision ) {
				case Renderbuffer::Byte:	target = GL_RGBA; break;
				case Renderbuffer::Float16:	target = GL_RGBA16F_ARB; break;
				case Renderbuffer::Float32:	target = GL_RGBA32F_ARB; break;
				default:	break;
			}
			glRenderbufferStorageEXT( GL_RENDERBUFFER_EXT,
				target, rb.x, rb.y );
			glFramebufferRenderbufferEXT( GL_FRAMEBUFFER_EXT,
				attach, GL_RENDERBUFFER_EXT,
				rb.buffer );
		} else {
			if( rb.texture->texture == -1 )
				load_texture( *rb.texture );
			glFramebufferTexture2DEXT( GL_FRAMEBUFFER_EXT,
				attach, GL_TEXTURE_2D,
				rb.texture->texture, 0 );
		}
		break;
	}
	}
}

void BaseRendererSystem::create_fbo( Framebuffer& fb ) {
	std::cout << "Creating fbo." << std::endl;
	glGenFramebuffersEXT( 1, &fb.buffer );
	glBindFramebufferEXT( GL_FRAMEBUFFER_EXT, fb.buffer );

	for( size_t i = 0; i < fb.render_buffers.size(); ++i ) {
		std::cout << "Creating rbo." << std::endl;
		create_rbo( fb.render_buffers[i] );
	}

	for( size_t i = 0; i < fb.buffer_types.size(); ++i ) {
		switch( fb.buffer_types[i] ) {
		case Framebuffer::Front:	fb.buffer_types[i] = GL_FRONT; break;
		case Framebuffer::Back:		fb.buffer_types[i] = GL_BACK; break;
		default:
			fb.buffer_types[i] = GL_COLOR_ATTACHMENT0_EXT +
				( fb.buffer_types[i] - Framebuffer::Color0 );
			break;
		}
	}

	glBindFramebufferEXT( GL_FRAMEBUFFER_EXT, 0 );
	std::cout << "Done creating fbo." << std::endl;
}

void BaseRendererSystem::bind_fbo( Framebuffer& fb ) {
	if( fb.buffer == -1 )
		create_fbo( fb );

	glBindFramebufferEXT( GL_FRAMEBUFFER_EXT, fb.buffer );
	glViewport( 0, 0, fb.x, fb.y );
	if( fb.buffer_types.size() )
		glDrawBuffers( (GLsizei)fb.buffer_types.size(), &fb.buffer_types[0] );
	else {
		glDrawBuffer( GL_NONE );
		glReadBuffer( GL_NONE );
	}

	GLenum status = glCheckFramebufferStatusEXT( GL_FRAMEBUFFER_EXT );
	if( status != GL_FRAMEBUFFER_COMPLETE_EXT ) {
		std::cout << "Bad fbo " << status << std::endl;
	}
}

void BaseRendererSystem::bind_program( Program& program, 
	Mesh& mesh, Matrix4f& camera ) {

	if( program.vertex_shader == -1 ) {
		program.vertex_shader = glCreateShaderObjectARB( GL_VERTEX_SHADER );
		const char* src = program.vertex_source.c_str();
		glShaderSourceARB( program.vertex_shader, 1, &src, NULL );
		glCompileShaderARB( program.vertex_shader );

		program.fragment_shader = 
			glCreateShaderObjectARB( GL_FRAGMENT_SHADER );
		src = program.fragment_source.c_str();
		glShaderSourceARB( program.fragment_shader, 1, &src, NULL );
		glCompileShaderARB( program.fragment_shader );

		program.program = glCreateProgramObjectARB();
		glAttachObjectARB( program.program, program.vertex_shader );
		glAttachObjectARB( program.program, program.fragment_shader );

		for( GLuint i = 0; i < Program::MAX_FRAMEBUFFERS; ++i )
			if( program.frag_location[i].length() ) {
				glBindFragDataLocationEXT( program.program, i, 
					program.frag_location[i].c_str() );
			}

		glLinkProgramARB( program.program );

		if( true || glGetError() != 0 ) {
			char error_message[2048];
			int nwritten = 0;
			glGetInfoLogARB( program.program, 2048, &nwritten, error_message );

			std::cerr << "Program failed to compile: " << std::endl;
			std::cerr << error_message << std::endl;
		}
	}

	glUseProgramObjectARB( program.program );

	if( program.camera_transform.length() ) {
		if( program.variables.count( program.camera_transform ) ) {
			std::copy( camera.ptr(), camera.ptr()+16,
				(float*)program.variables[ program.camera_transform ]
					->data );
		} else {
			program.variables[ program.camera_transform ] =
				ProgramVariable::mat4( camera );
		}
	}
	
	Program::variable_map::iterator i;
	for( i = program.variables.begin(); i != program.variables.end(); ++i )
		bind_variable( program, mesh, i->first, *i->second );
}

void BaseRendererSystem::bind_variable( Program& program, Mesh& mesh,
	const std::string& name, ProgramVariable& var ) {

	switch( var.type ) {
	case ProgramVariable::FLOAT: {
		GLint loc = glGetUniformLocationARB( program.program, name.c_str() );
		switch( var.dimension ) {
		case 1:		glUniform1fARB( loc, *(float*)var.data ); break;
		case 3:		glUniform3fvARB( loc, 1, (float*)var.data ); break;
		default:	break;
		}
		break;
	}
	case ProgramVariable::INT: {
		GLint loc = glGetUniformLocationARB( program.program, name.c_str() );
		glUniform1iARB( loc, *(int*)var.data );
		break;
	}
	case ProgramVariable::FLOAT_MATRIX: {
		GLint loc = glGetUniformLocationARB( program.program, name.c_str() );
		glUniformMatrix4fvARB( loc, 1, false, (float*)var.data );
		break;
	}
	case ProgramVariable::MESH_ATTRIBUTE: {
		GLint loc = glGetAttribLocationARB( program.program, name.c_str() );
		MeshVertexData::AttributeType t = 
			*(MeshVertexData::AttributeType*)var.data;

		Mesh::iterator_type iter;
		for( iter = mesh.begin(); iter != mesh.end(); ++iter ) {
			if( iter->type == t ) {
				GLenum type = 0;
				switch( iter->data_type ) {
				case MeshVertexData::FLOAT: type = GL_FLOAT;	break;
				case MeshVertexData::UCHAR: type = GL_UNSIGNED_BYTE;	break;
				default:	break;
				}

				glVertexAttribPointerARB( 
						loc, (GLint)iter->ncomponents, type,
						1, (GLsizei)iter->stride, iter->data + iter->offset );
				glEnableVertexAttribArrayARB( loc );
			}
		}
		break;
	}
	default:
		break;
	}
}

void BaseRendererSystem::ff_bind_camera( Matrix4f& t ) {
	glMatrixMode( GL_PROJECTION );
	glLoadIdentity();

	glMatrixMode( GL_MODELVIEW );
	glLoadIdentity();
	glLoadMatrixf( t.ptr() );
}

void BaseRendererSystem::ff_bind_vertex( MeshVertexData& data ) {
	glVertexPointer( (GLint)data.ncomponents, gl_type_map[ data.data_type ],
		(GLsizei)data.stride, data.data + data.offset );
	glEnableClientState( GL_VERTEX_ARRAY );
}

void BaseRendererSystem::ff_bind_color( MeshVertexData& data ) {
	glColorPointer( (GLint)data.ncomponents, gl_type_map[ data.data_type ],
		(GLsizei)data.stride, data.data + data.offset );
	glEnableClientState( GL_COLOR_ARRAY );
}

void MeshRendererSystem::draw_mesh( Entity::pointer_type ent, Mesh& mesh,
	Matrix4f& camera, RenderFlags flags ) {

	MeshRenderer& mr = static_cast<MeshRenderer&>(
		ent->get_component( Component::MeshRenderer ) );
	if( !(mr.flags & flags) )
		return;

	Matrix4f modelviewproj = Matrix4f::identity();
	if( ent->has_component( Component::Transform ) )
		modelviewproj = ent->transform().build_matrix();
	modelviewproj = camera * modelviewproj;

	Entity::component_range texs = 
		ent->get_components( Component::Texture );
	for( Entity::component_iterator i = texs.first; i != texs.second; ++i ){
		Texture& tex = static_cast<Texture&>(*(i->second));
		if( tex.flags & flags )
			bind_texture( tex );
	}

	Vector3f color( 1.f, 1.f, 1.f );
	if( ent->has_component( Component::Color ) )
		color = ( static_cast<Color&>( 
			ent->get_component( Component::Color ) ) ).color;
	glColor3f( color[0], color[1], color[2] );

	bool bound_prog = false;
	if( ent->has_component( Component::Program ) ) {
		Program& program = static_cast<Program&>(
			ent->get_component( Component::Program ) );
		if( program.flags & flags ) {
			bound_prog = true;
			bind_program( program, mesh, modelviewproj );
		}
	}

	if( !bound_prog ) {
		ff_bind_camera( modelviewproj );
		Mesh::iterator_type i = mesh.begin();
		for( ; i != mesh.end(); ++i ) {
			switch( i->type ) {
			case MeshVertexData::VERTEX:
				ff_bind_vertex( *i ); break;
			case MeshVertexData::COLOR:
				ff_bind_color( *i ); break;
			default:
				break;
			}
		}
	}

	MeshIndexData& index = mesh.index_data;
	glDrawElements( GL_TRIANGLES, (GLsizei)mesh.nindices, 
		gl_type_map[ index.type ], index.data );

	GLenum error;
	if( (error = glGetError()) != 0 ) {
		std::cout << "Error: " << error << std::endl;
		exit(0);
	}
}

void MeshRendererSystem::begin() {
	meshes.resize( 0 );
	cameras.resize( 0 );
}

void MeshRendererSystem::update( Entity::pointer_type ent ) {
	if( ent->has_component( Component::Camera ) ) {
		Camera& c = static_cast<Camera&>( ent->get_component(
			Component::Camera ) );
		cameras.push_back( std::make_pair( c.priority, ent ) );
	} else if( ent->has_component( Component::MeshRenderer ) ) {
		meshes.push_back( ent );
	}
}

void MeshRendererSystem::end() {
	std::sort( cameras.begin(), cameras.end() );
	for( size_t c = 0; c < cameras.size(); ++c ) {
		Entity::pointer_type ent = cameras[c].second;
		Camera& camera = static_cast<Camera&>( 
			ent->get_component( Component::Camera ) );
		Transform& t = ent->transform();

		/*
		t.load_identity();
		t.translate( -camera.pos );
		t.rotate( Vector3f( 0., 1., 0. ), camera.rot.d[0] );
		t.rotate( Vector3f( 1., 0., 0. ), camera.rot.d[1] );
		*/
		Matrix4f view = Matrix4f::identity();
		view *= Matrix4f::rotation( Vector3f( 1., 0., 0. ), t.rotation[1] );
		view *= Matrix4f::rotation( Vector3f( 0., 1., 0. ), t.rotation[0] );
		view *= Matrix4f::translation( -t.position );
		//t.print();
		
		//if( camera.type == Camera::Perspective ) {
			//view = Matrix4f::perspective( camera.fov, camera.aspect, 
				//camera.nearz, camera.farz ) * view;
		//} else {
			//view = Matrix4f::ortho( camera.minx, camera.maxx, camera.miny, 
				//camera.maxy, camera.nearz, camera.farz ) * view;
		//}
		view = camera.build_matrix() * view;

		Entity::component_range texs = 
			ent->get_components( Component::Texture );
		for( Entity::component_iterator i = texs.first; i != texs.second; ++i )
			bind_texture( static_cast<Texture&>(*(i->second)) );

		if( ent->has_component( Component::Framebuffer ) ) {
			Framebuffer& fb = static_cast<Framebuffer&>(
				ent->get_component( Component::Framebuffer ) );
			bind_fbo( fb );
		}

		glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT );
		for( size_t m = 0; m < meshes.size(); ++m ) {
			Entity::pointer_type mesh = meshes[m];
			Entity::component_range mesh_data = 
				mesh->get_components( Component::Mesh );

			Entity::component_iterator mi = mesh_data.first;
			for( ; mi != mesh_data.second; ++ mi )
				draw_mesh( mesh, static_cast<Mesh&>(*(mi->second)), 
					view, camera.flags );
		}

		/*
		if( c == 0 ) {
			float* d = new float[ 800*600 ];
			glReadPixels( 0, 0, 800, 600, GL_DEPTH_COMPONENT, GL_FLOAT, d );

			unsigned char* ud = new unsigned char[ 3*800*600 ];
			for( size_t i = 0; i < 800; ++i )
			for( size_t j = 0; j < 600; ++j ) {
				ud[ (j*800 + i) * 3 ] = unsigned char(
					pow( d[ j*800 + i ], 1.f ) * 255. );
				ud[ (j*800 + i)*3 + 1 ] = 0;
				ud[ (j*800 + i)*3 + 2 ] = 0;
			}

			SDL_Surface* surf = SDL_CreateRGBSurfaceFrom( ud,
				800, 600, 24, 800*3, 0xff0000, 0x00ff00, 0x0000ff, 0 );
			SDL_SaveBMP( surf, "temp.bmp" );
			SDL_FreeSurface( surf );

			delete [] ud;
			delete [] d;
		}
		*/
		
		// Reset all state we might have used
		glDisable( GL_TEXTURE_2D );

		glDisableClientState( GL_VERTEX_ARRAY );
		glDisableClientState( GL_COLOR_ARRAY );
		if( glUseProgramObjectARB )
			glUseProgramObjectARB( 0 );

		if( glBindFramebufferEXT )
			glBindFramebufferEXT( GL_FRAMEBUFFER_EXT, 0 );
		glDrawBuffer( GL_BACK );
		glReadBuffer( GL_BACK );

		if( glDisableVertexAttribArrayARB ) {
			glDisableVertexAttribArrayARB( 0 );
			glDisableVertexAttribArrayARB( 1 );
		}

	}
}

