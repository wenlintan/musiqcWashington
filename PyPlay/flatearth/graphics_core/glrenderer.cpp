#include "glrenderer.h"

map< Renderer::VertexDataType, GLuint > GLRenderer::GLVertexTypeMap;
void export_glrenderer()
{
	/*
	class_<GLRenderer, bases<Renderer> >( "glrenderer", init< const Vector2d&, bool >() )
		.def( "initialize", &GLRenderer::initialize )
		.def( "start_frame", &GLRenderer::start_frame )
		.def( "end_frame", &GLRenderer::end_frame );

	register_ptr_to_python< shared_ptr<GLRenderer> >();
	*/
}

void export_glfont()
{
	/*
	class_<GLFont, bases<Font> >( "glfont", init< const string&, shared_ptr<Renderer> >() )
		.def( "add_color", &GLFont::add_color )
		.def( "select_color", (void (GLFont::*)(const string&))(&GLFont::select_color) )
		.def( "write", &GLFont::print );
	
	register_ptr_to_python< shared_ptr<GLFont> >();
	*/
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

#define LOAD(type, name)	name = (type) SDL_GL_GetProcAddress(#name)

bool GLRenderer::initialize( const Vector2d &screendim, bool fullscreen )
{
	GLVertexTypeMap[ Renderer::POINT ] = GL_POINTS;
	GLVertexTypeMap[ Renderer::LINE ] = GL_LINES;
	GLVertexTypeMap[ Renderer::LINE_STRIP ] = GL_LINE_STRIP;
	GLVertexTypeMap[ Renderer::TRI ] = GL_TRIANGLES;
	GLVertexTypeMap[ Renderer::TRI_STRIP ] = GL_TRIANGLE_STRIP;
	GLVertexTypeMap[ Renderer::QUAD ] = GL_QUADS;
	GLVertexTypeMap[ Renderer::QUAD_STRIP ] = GL_QUAD_STRIP;

	if(SDL_Init( SDL_INIT_VIDEO | SDL_INIT_TIMER | SDL_INIT_NOPARACHUTE ) == -1)
	{
		LOG_ERR("Could not initialize SDL");
		LOG_ERR(SDL_GetError());
		return false;
	}

	//create the actual window using SDL for convenience and portability
	LOG_INFO("Creating SDL Window at 32 bpp");
	SDL_GL_SetAttribute(SDL_GL_RED_SIZE, 8);
	SDL_GL_SetAttribute(SDL_GL_BLUE_SIZE, 8);
	SDL_GL_SetAttribute(SDL_GL_GREEN_SIZE, 8);
	SDL_GL_SetAttribute(SDL_GL_ALPHA_SIZE, 8);

	LOG_INFO("Creating SDL Window with double buffering");
	SDL_GL_SetAttribute(SDL_GL_DOUBLEBUFFER, 1);
	SDL_GL_SetAttribute(SDL_GL_DEPTH_SIZE, 16);

	_SDLSurface = SDL_SetVideoMode( screendim.x, screendim.y, 32, SDL_OPENGL );
	if(!_SDLSurface)
	{
		LOG_ERR( string("Could not set GL Mode: ") + SDL_GetError() );
		return false;
	}

	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
	LOG_SUCCESS("SDL Window created successfully");

	LOG_INFO( string("Vendor: ") + (const char*)glGetString(GL_VENDOR) );
	LOG_INFO( string("Renderer: ") + (const char*)glGetString(GL_RENDERER) );
	LOG_INFO( string("Extensions: ") + (const char*)glGetString(GL_EXTENSIONS) );

	//load opengl multitexturing extensions
#ifndef NO_MULTITEX
	LOAD(PFNGLACTIVETEXTUREARBPROC,				glActiveTextureARB);
	LOAD(PFNGLMULTITEXCOORD2FARBPROC,			glMultiTexCoord2fARB);
	LOAD(PFNGLMULTITEXCOORD2FVARBPROC,			glMultiTexCoord2fvARB);
	LOAD(PFNGLCLIENTACTIVETEXTUREARBPROC,		glClientActiveTextureARB);

	_UseMultiTexture = glActiveTextureARB && glMultiTexCoord2fARB && glMultiTexCoord2fvARB &&
					   glClientActiveTextureARB;
#else
	_UseMultiTexture = false;
#endif

	if( _UseMultiTexture )		LOG_INFO( "Multitexture support detected and loaded." );
	else						LOG_WARN( "Multitexture support not detected." );

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

	_UseFBOs = glBindRenderbufferEXT && glDeleteRenderbuffersEXT && glGenRenderbuffersEXT &&
			   glRenderbufferStorageEXT && glBindFramebufferEXT && glDeleteFramebuffersEXT &&
			   glGenFramebuffersEXT && glCheckFramebufferStatusEXT && glFramebufferTexture2DEXT &&
			   glFramebufferRenderbufferEXT && glDrawBuffers;
#else
	_UseFBOs = false;
#endif

	if( _UseFBOs )		LOG_INFO( "FBO support detected and loaded." );
	else				LOG_WARN( "FBO support not detected." );

	//load opengl shader extensions
#ifndef NO_SHADERS
	LOAD(PFNGLCREATEPROGRAMOBJECTARBPROC,		glCreateProgramObjectARB);
	LOAD(PFNGLCREATESHADEROBJECTARBPROC,		glCreateShaderObjectARB);
	LOAD(PFNGLSHADERSOURCEARBPROC,				glShaderSourceARB);
	LOAD(PFNGLCOMPILESHADERARBPROC,				glCompileShaderARB);
	LOAD(PFNGLATTACHOBJECTARBPROC,				glAttachObjectARB);
	LOAD(PFNGLLINKPROGRAMARBPROC,				glLinkProgramARB);
	LOAD(PFNGLUSEPROGRAMOBJECTARBPROC,			glUseProgramObjectARB);
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

	_UseShaders =	glCreateProgramObjectARB && glCreateShaderObjectARB &&  glShaderSourceARB &&
					glCompileShaderARB && glAttachObjectARB && glLinkProgramARB && glUseProgramObjectARB &&
					glDeleteObjectARB && glGetInfoLogARB && glUniform3fARB && glUniform3fvARB && 
					glGetUniformLocationARB && glVertexAttrib3fARB && glVertexAttrib3fvARB &&
					glVertexAttribPointerARB && glDisableVertexAttribArrayARB && glEnableVertexAttribArrayARB &&
					glGetAttribLocationARB;
#else
	_UseShaders = false;
#endif

	if( _UseShaders )		LOG_INFO( "GLSL support detected and loaded." );
	else					LOG_WARN( "GLSL support not detected." );

	//setup opengl constants
	_Dimensions = screendim;

	glMatrixMode( GL_MODELVIEW );
	glLoadIdentity();

	glClearColor( 0.0f, 0.0f, 0.0f, 0.0f );						// Black Background
	glClearDepth( 1.0f );										// Depth Buffer Setup
	glColor4f( 1.0f, 1.0f, 1.0f, 1.0f );						// Set The Color To White

	LightColor lc( 1.0f, 1.0f, 1.0f, 1.0f );
	//glMaterialfv( GL_FRONT_AND_BACK, GL_AMBIENT, &lc.r );
	//glMaterialfv( GL_FRONT_AND_BACK, GL_DIFFUSE, &lc.r );
	//glMaterialfv( GL_FRONT_AND_BACK, GL_SPECULAR, &lc.r );

	glEnable( GL_LINE_SMOOTH );
	glEnable( GL_POLYGON_SMOOTH );
	glLineWidth( 0.25f );

	glDepthFunc( GL_LESS );									// The Type Of Depth Testing (Less Or Equal)
	glShadeModel( GL_SMOOTH );									// Select Smooth Shading
	glHint( GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST );		// Set Perspective Calculations To Most Accurate
	
	glEnable( GL_DEPTH_TEST );
	glEnable( GL_TEXTURE_2D );

	glFrontFace( GL_CCW );
	glCullFace( GL_BACK );
	glEnable( GL_CULL_FACE );

	glDisable( GL_LIGHTING );

	//when we enable blending this is the function we want
	glDisable( GL_BLEND );
	glBlendFunc( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA );

	int maxtsize;
	glGetIntegerv( GL_MAX_TEXTURE_SIZE, &maxtsize );

	check_errors();
	return true;
}

void GLRenderer::shutdown()
{
	if( _SDLSurface )
		SDL_Quit();

	_SDLSurface = NULL;
}

void GLRenderer::start_frame()
{
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
}

void GLRenderer::end_frame()
{
	SDL_GL_SwapBuffers();
}

void GLRenderer::check_errors()
{
	int errs = glGetError();
	if(errs!= 0)
	{
		const GLubyte* err = gluErrorString(errs);
		const char* blah = (const char*)err;
		if(blah)	LOG_ERR( string("OpenGL error:") + blah );
		else		LOG_ERR( "Unknown OpenGL error." );
	}
}

void GLRenderer::apply_draw_call_info( const DrawCallInfo& info )
{
	glMatrixMode( GL_MODELVIEW );
	glPushMatrix();
	glTranslatef( info.translation.x, info.translation.y, info.translation.z );
	glRotatef( info.rotation.z, 0.0f, 0.0f, 1.0f );
	glRotatef( info.rotation.y, 0.0f, 1.0f, 0.0f );
	glRotatef( info.rotation.x, 1.0f, 0.0f, 0.0f );
	
	Vector3ub color = info.color.RawColor;
	glColor4ub( color.r, color.g, color.b, info.color.Alpha );

	if( info.ccw )
		glFrontFace( GL_CCW );
	else
		glFrontFace( GL_CW );

	if( info.blend_enabled ) {
		glEnable( GL_BLEND );
		switch( info.blend_method ) {
			case DrawCallInfo::SOURCE:
				glBlendFunc( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA );
				break;
			case DrawCallInfo::DEST:
				glBlendFunc( GL_ONE_MINUS_DST_ALPHA, GL_DST_ALPHA );
				break;
			case DrawCallInfo::SOURCE_DEST:
				glBlendFunc( GL_SRC_ALPHA, GL_DST_ALPHA );
				break;
		}
	} else { 
		glDisable( GL_BLEND );
	}
}

void GLRenderer::unapply_draw_call_info()
{
	glPopMatrix();
	glFrontFace( GL_CCW );
	glColor4ub( 255, 255, 255, 255 );
	glDisable( GL_BLEND );
}

void GLRenderer::unset_client_states()
{
	glDisableClientState( GL_VERTEX_ARRAY );
	glDisableClientState( GL_COLOR_ARRAY );
	glDisableClientState( GL_NORMAL_ARRAY );

	if( _UseMultiTexture ) {
		for( ushort i = 0; i < 4; ++i ) {
			glClientActiveTextureARB( GL_TEXTURE0_ARB + i );
			glDisableClientState( GL_TEXTURE_COORD_ARRAY );
		}
	} else {
		glDisableClientState( GL_TEXTURE_COORD_ARRAY );
	}
}

void GLRenderer::apply_render_state(const boost::shared_ptr<State> state)
{
	switch( state->SpecType )
	{
	case Resource::TEXTURE:
	case Resource::DATA_TEXTURE:
		{
		if( !state->RenderData ) {
			glBindTexture( GL_TEXTURE_2D, 0 );
			break;
		}

		shared_ptr<GLTexture> gltex = boost::shared_static_cast<GLTexture, Resource>( state->RenderData );
		_UseColor = false;

		glColor4f( 1.0f, 1.0f, 1.0f, 1.0f );

		glEnable( gltex->GLTarget );
		glBindTexture( gltex->GLTarget, gltex->GLTex );
		break;
		}
	case Resource::MULTI_TEXTURE:
		{
		shared_ptr<MultiTexture> mt = boost::shared_static_cast<MultiTexture, State>( state );
		glActiveTextureARB( GL_TEXTURE0_ARB + mt->TextureUnit );
		apply_render_state( mt->Texture );

		glClientActiveTextureARB( GL_TEXTURE0_ARB + mt->TextureUnit );
		glTexCoordPointer( 2, GL_FLOAT, 0, &mt->Coordinates[0] );
		glEnableClientState( GL_TEXTURE_COORD_ARRAY );

		glClientActiveTextureARB( GL_TEXTURE0_ARB );
		glActiveTextureARB( GL_TEXTURE0_ARB );
		break;
		}
	case Resource::FLAT_COLOR:
		{
		shared_ptr<Color> c = boost::shared_static_cast<Color, State>( state );

		_UseColor = true;
		_Color = c->RawColor;

		glDisable( GL_TEXTURE_2D );
		glColor4ub( _Color.r, _Color.g, _Color.b, c->Alpha );

		if( c->Alpha != 255 )
			glEnable( GL_BLEND );

		break;
		}
	case Resource::CULLING:
		{
		shared_ptr<Culling> c = boost::shared_static_cast<Culling, State>( state );
		if( c->enabled ) {
			glEnable( GL_CULL_FACE );
			glCullFace( c->front?GL_FRONT:GL_BACK );
		} else {
			glDisable( GL_CULL_FACE );
		}
		break;
		}
	case Resource::PROGRAM:
		{
		if( !state->RenderData ) {
			glUseProgramObjectARB( 0 );		//revert to fixed function
			break;
		}

		shared_ptr<GLProgram> glprog = boost::shared_static_cast<GLProgram, Resource>( state->RenderData );
		glUseProgramObjectARB( glprog->GLProg );
		break;
		}
	case Resource::RENDER_TARGET:
		{
		if( !state->RenderData ) {
			glBindFramebufferEXT( GL_FRAMEBUFFER_EXT, 0 );
			glDrawBuffer( GL_BACK );
			break;
		}

		shared_ptr<RenderTarget> targ = boost::shared_static_cast<RenderTarget, State>( state );
		shared_ptr<GLTarget> gltarg = boost::shared_static_cast<GLTarget, Resource>( state->RenderData );

		glBindFramebufferEXT( GL_FRAMEBUFFER_EXT, gltarg->GLFBO );
		glViewport( 0, 0, targ->Width, targ->Height );

		GLenum ready = glCheckFramebufferStatusEXT( GL_FRAMEBUFFER_EXT );
		if(  ready != GL_FRAMEBUFFER_COMPLETE_EXT || !targ->Targets.size() ) {
			check_errors();
			break;
		}

		glDrawBuffers( (GLenum)gltarg->Targets.size(), &gltarg->Targets[0] );
		break;
		}
	case Resource::LIGHT:
		{
		shared_ptr<Light> l = boost::shared_static_cast<Light, State>( state );
		if( l->Enabled )	glEnable( GL_LIGHTING );
		else				glDisable( GL_LIGHTING );
		l->apply();
		break;
		}
	case Resource::CAMERA:
		{
		shared_ptr<Camera> cam = boost::shared_static_cast<Camera, State>( state );
		CameraPosition = cam->_Position;

		glMatrixMode(GL_PROJECTION);
		glLoadIdentity();
		gluPerspective( cam->_FOV, (GLfloat)cam->_Width/(GLfloat)cam->_Height,
						cam->_NearZ, cam->_FarZ );
		
		glMatrixMode(GL_MODELVIEW);
		glLoadIdentity();
		gluLookAt(	cam->_Position.x, cam->_Position.y, cam->_Position.z,
					cam->_Look.x, cam->_Look.y, cam->_Look.z,
					cam->_Up.x, cam->_Up.y, cam->_Up.z  );
		break;
		}
	case Resource::ORTHO:
		{
		shared_ptr<Ortho> ort = boost::shared_static_cast<Ortho, State>( state );
		CameraPosition = Vector3f( ort->_Width / 2.0f, ort->_Height / 2.0f, (ort->_NearZ+ort->_FarZ)/2.0f );

		glMatrixMode(GL_PROJECTION);
		glLoadIdentity();
		glOrtho( 0, ort->_Width, 0, ort->_Height, ort->_NearZ, ort->_FarZ );

		glMatrixMode(GL_MODELVIEW);
		glLoadIdentity();
		break;
		}
	}
	check_errors();
}

bool GLRenderer::vertex_source_proje( const vector<Vertex>& verts )
{
	if( !verts.size() )	{
		_VertexSourceSize = 0;
		return false;
	}

	glEnableClientState( GL_VERTEX_ARRAY );
	glEnableClientState( GL_TEXTURE_COORD_ARRAY );
	glEnableClientState( GL_NORMAL_ARRAY );
	_VertexSourceSize = (uint)verts.size();
	
	glEnable( GL_TEXTURE_2D );

	glInterleavedArrays( GL_T2F_N3F_V3F, sizeof(Vertex), &verts[0] );
	check_errors();
	return true;
}

bool GLRenderer::vertex_source_proje( const vector<NormalVertex>& verts ) 
{
	if( !verts.size() )	{
		_VertexSourceSize = 0;
		return false;
	}

	glEnableClientState( GL_VERTEX_ARRAY );
	glEnableClientState( GL_NORMAL_ARRAY );
	_VertexSourceSize = (uint)verts.size();

	glDisable( GL_TEXTURE_2D );

	glInterleavedArrays( GL_N3F_V3F, sizeof(NormalVertex), &verts[0] );
	check_errors();
	return true;
}
	

bool GLRenderer::vertex_source_proje( const vector<ColorVertex>& verts )
{
	if( !verts.size() )	{
		_VertexSourceSize = 0;
		return false;
	}

	glEnableClientState( GL_VERTEX_ARRAY );
	glEnableClientState( GL_COLOR_ARRAY );
	_VertexSourceSize = (uint)verts.size();

	glDisable( GL_TEXTURE_2D );

	glInterleavedArrays( GL_C3F_V3F, sizeof(ColorVertex), &verts[0] );
	check_errors();
	return true;
}

bool GLRenderer::vertex_source_proje( const vector<Vector3f>& verts )
{
	if( !verts.size() ) {
		_VertexSourceSize = 0;
		return false;
	}

	glEnableClientState( GL_VERTEX_ARRAY );
	_VertexSourceSize = (uint)verts.size();

	glDisable( GL_TEXTURE_2D );

	glVertexPointer( 3, GL_FLOAT, sizeof(Vector3f), &verts[0].x );
	check_errors();
	return true;
}

bool GLRenderer::draw_vertices_proje( const DrawCallInfo& info )
{
	if( _VertexSourceSize == 0 )
		return false;

	apply_draw_call_info( info );
	glDrawArrays( GLVertexTypeMap[ info.type ], info.start, (info.numdraw==(uint)-1)?_VertexSourceSize:info.numdraw );
	unapply_draw_call_info();

	check_errors();
	return true;
}

bool GLRenderer::draw_indices_proje( const vector<ushort>& indices, const DrawCallInfo& info )
{
	if( indices.empty() || _VertexSourceSize == 0 )
		return false;

	apply_draw_call_info( info );
	glDrawElements( GLVertexTypeMap[ info.type ], (info.numdraw==(uint)-1)?(indices.size()-info.start):info.numdraw, 
					GL_UNSIGNED_SHORT, &indices[ info.start ] );

	unapply_draw_call_info();
	check_errors();
	return true;
}

bool GLRenderer::draw_simple_coords_proje( const std::vector<Vector3f> &verts, const DrawCallInfo& info )
{
	if( verts.empty() )
		return false;

	apply_draw_call_info( info );
	glBegin( GLVertexTypeMap[ info.type ] );

	for( vector<Vertex>::size_type i = 0; i != ((info.numdraw==(uint)-1)?verts.size():info.numdraw); ++i )
		glVertex3fv( (GLfloat*)(&verts[i].x) );

	glEnd();
	unapply_draw_call_info();

	check_errors();
	return true;
}

bool GLRenderer::release_vertex_source()
{
	unset_client_states();
	return true;
}

void GLRenderer::load_texture(boost::shared_ptr<State> data)
{
	if( data->RenderData )	return;
	shared_ptr<Resource> res( new GLTexture(data) );
	data->RenderData = res;

	check_errors();
}

void GLRenderer::disable_all_textures() 
{
	int max_units = -1;
	glGetIntegerv( GL_MAX_TEXTURE_UNITS_ARB, &max_units );

	for( int i = 0; i < max_units; ++i ) {
		glActiveTextureARB( GL_TEXTURE0_ARB + i );
		glBindTexture( GL_TEXTURE_2D, 0 );
	}

	glActiveTextureARB( GL_TEXTURE0_ARB );		
}


void GLRenderer::load_shader(boost::shared_ptr<State> data)
{
	if( data->RenderData || !_UseShaders )	return;
	shared_ptr<Resource> res( new GLProgram(data) );
	data->RenderData = res;

	check_errors();
}

void GLRenderer::load_render_target(boost::shared_ptr<State> data)
{
	if( data->RenderData || !_UseFBOs )	return;
	shared_ptr<Resource> res( new GLTarget(data) );
	data->RenderData = res;

	check_errors();
}

void GLRenderer::save_render_target( shared_ptr<State> targ, size_t target_index, vector<float>& data ) {
	shared_ptr<GLTarget> target = boost::shared_static_cast<GLTarget, Resource>( targ->RenderData );
	target->save( target_index, data );

	check_errors();
}

void GLRenderer::set_shader_variable( shared_ptr<State> data, ShaderVariable& var ) {
	shared_ptr<Program> prog = boost::shared_static_cast<Program, State>( data );
	shared_ptr<GLProgram> glprog = boost::shared_static_cast<GLProgram, Resource>( prog->RenderData );

	switch( var.Modifier ) {
	case ShaderVariable::GLOBAL:
		{
		GLint loc = glGetUniformLocationARB( glprog->GLProg, var.Name.c_str() );
		if( loc == -1 )		return;

		switch( var.Type ) {
		case ShaderVariable::INT:
			{
			const int i = boost::any_cast<int>( var.Data );
			glUniform1iARB( loc, i );
			break;
			}
		case ShaderVariable::INT_ARRAY:
			{
			const vector< int >& data = boost::any_cast< vector<int> >( var.Data );
			if( !data.size() )	return;

			glUniform1ivARB( loc, data.size(), &data[0] );
			break;
			}
		case ShaderVariable::FLOAT: 
			{
			const float f = boost::any_cast<float>( var.Data );
			glUniform1fARB( loc, f );
			break;
			}
		case ShaderVariable::FLOAT_ARRAY:
			{
			const vector< float >& data = boost::any_cast< vector<float> >( var.Data );
			if( !data.size() )	return;

			glUniform1fvARB( loc, data.size(), &data[0] );
			break;
			}
		case ShaderVariable::VECTOR3F:
			{
			const Vector3f& v = boost::any_cast<Vector3f>( var.Data );
			glUniform3fARB( loc, v.x, v.y, v.z );
			break;
			}
		case ShaderVariable::VECTOR3F_ARRAY:
			{
			const vector<Vector3f>& data = boost::any_cast< vector<Vector3f> >( var.Data );
			if( !data.size() )	return;

			glUniform3fvARB( loc, (GLsizei)data.size(), &data[0].x );
			break;
			}
		case ShaderVariable::MATRIX44:
			{
			const Matrix44& data = boost::any_cast< Matrix44 >( var.Data );
			glUniformMatrix4fvARB( loc, 1, false, data.m );
			break;
			}
		case ShaderVariable::MATRIX44_ARRAY:
			{
			const vector<Matrix44>& data = boost::any_cast< vector<Matrix44> >( var.Data );
			if( !data.size() )	return;

			glUniformMatrix4fvARB( loc, data.size(), false, data[0].m );
			break;
			}

		}
		break;
		}
	}
	check_errors();
}


/////////////////////////////////////////////////////////////////////////////////////////
//GLTexture

bool GLTexture::initialize( const boost::shared_ptr<Resource> res )
{
	if( res->SpecType == Resource::TEXTURE ) {
		const shared_ptr<Texture> tex = boost::static_pointer_cast<Texture, Resource>( res );

		glGenTextures(1, &GLTex);
		glBindTexture(GL_TEXTURE_2D, GLTex);

		glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR);
		glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR);

		gluBuild2DMipmaps(	GL_TEXTURE_2D, 3, tex->Width, tex->Height,
							GL_RGB, GL_UNSIGNED_BYTE, tex->PixelData );

		GLTarget = GL_TEXTURE_2D;
		glBindTexture( GL_TEXTURE_2D, 0 );
		return true;
	}
	if( res->SpecType == Resource::DATA_TEXTURE ) {
		const shared_ptr<DataTexture> tex = boost::static_pointer_cast<DataTexture, Resource>( res );
		GLsizei height = tex->Size / tex->Width / tex->NComponents;

		if( height == 1 )	GLTarget = GL_TEXTURE_1D;
		else				GLTarget = GL_TEXTURE_2D;

		glGenTextures(1, &GLTex);
		glBindTexture(GLTarget, GLTex);

		glTexParameteri(GLTarget,GL_TEXTURE_MIN_FILTER,GL_LINEAR);
		glTexParameteri(GLTarget,GL_TEXTURE_MAG_FILTER,GL_LINEAR);

		if( tex->Type == DataTexture::FLOAT ) {
			GLenum gltype = (tex->Prec == DataTexture::COLOR)? GL_RGBA: 
							(tex->Prec == DataTexture::FLOAT16)? GL_RGBA16F_ARB: GL_RGBA32F_ARB;

			GLenum glfrmt = (tex->NComponents == 3)? GL_RGB:
							(tex->NComponents == 4)? GL_RGBA: GL_RED;

			const vector<float>& data = boost::any_cast<const vector<float>&>(tex->Data);
			
			if( height == 1 ) {
				glTexImage1D( GL_TEXTURE_1D, 0, gltype, tex->Width, 0, glfrmt, GL_FLOAT, &data[0]  );
			} else {
				glTexImage2D( GL_TEXTURE_2D, 0, gltype, tex->Width, height, 0, glfrmt, GL_FLOAT, &data[0] );
			}
		}

		glBindTexture( GLTarget, 0 );
		return true;
	}
	return false;
}

bool GLTexture::initialize( const string& filename, shared_ptr<Renderer> rend )
{
	shared_ptr<Resource> res = Resource::load( filename, rend );
	if( !res )	return false;

	return initialize( res );
}

void GLTexture::shutdown()
{
	if( GLTex != -1 )
		glDeleteTextures(1, &GLTex);

	GLTex = -1;
}

/////////////////////////////////////////////////////////////////////////////////////////
//GLShader

bool GLProgram::initialize( const shared_ptr<Resource>& res ) {
	if( !glCreateProgramObjectARB )
		return false;

	shared_ptr<Program> shader = boost::shared_static_cast<Program, Resource>(res);

	GLProg = glCreateProgramObjectARB();
	GLVertexShader = glCreateShaderObjectARB( GL_VERTEX_SHADER_ARB );
	GLFragShader = glCreateShaderObjectARB( GL_FRAGMENT_SHADER_ARB );

	const char *vprog = shader->Vertex->Source.c_str(), *fprog = shader->Frag->Source.c_str();
	glShaderSourceARB( GLVertexShader, 1, &vprog, NULL );
	glShaderSourceARB( GLFragShader, 1, &fprog, NULL );
	glCompileShaderARB( GLVertexShader );
	glCompileShaderARB( GLFragShader );

	glAttachObjectARB( GLProg, GLVertexShader );
	glAttachObjectARB( GLProg, GLFragShader );
	glLinkProgramARB( GLProg );

	glUseProgramObjectARB( GLProg );

	GLsizei length;
	char raw_buffer[ 16000 ];
	glGetInfoLogARB( GLProg, 16000, &length, raw_buffer );

	stringstream buffer;
	buffer << "Shader Program information: " << raw_buffer;
	LOG_INFO( buffer.str() );


	if( glGetError() != 0 ) {

		LOG_ERR( "Program failed to compile." );
		return false;
	}

	return true;
}

void GLProgram::shutdown() {
	if( GLProg != 0 )
		glDeleteObjectARB( GLProg );

	GLProg = -1;
}

/////////////////////////////////////////////////////////////////////////////////////////
//GLTarget

bool GLTarget::initialize( const shared_ptr<Resource>& res ) {
	if( !glGenFramebuffersEXT )
		return false;

	const shared_ptr<RenderTarget>& rt = boost::shared_static_cast<RenderTarget, Resource>( res );
	
	glGenFramebuffersEXT(1, &GLFBO);
	for( size_t i = 0; i < rt->Attachments.size(); ++i )
		attach( rt->Attachments[i], i );

	if( rt->ZBuffering ) { 
		glBindFramebufferEXT( GL_FRAMEBUFFER_EXT, GLFBO );

		glGenRenderbuffersEXT( 1, &GLDepth );
		glBindRenderbufferEXT( GL_RENDERBUFFER_EXT, GLDepth );
		glRenderbufferStorageEXT( GL_RENDERBUFFER_EXT, GL_DEPTH_COMPONENT, rt->Width, rt->Height );
		glFramebufferRenderbufferEXT( GL_FRAMEBUFFER_EXT, GL_DEPTH_ATTACHMENT_EXT, GL_RENDERBUFFER_EXT, GLDepth );

		glBindFramebufferEXT( GL_FRAMEBUFFER_EXT, 0 );
	}

	Targets = rt->Targets;
	Attachments = rt->Attachments;

	//use GLTarget's Targets to refer to GLenum values
	for( size_t i = 0; i < rt->Targets.size(); ++i ) {
		if( Targets[i] == RenderTarget::BACK )		Targets[i] = GL_BACK;
		if( Targets[i] == RenderTarget::FRONT )		Targets[i] = GL_FRONT;
		else										Targets[i] += GL_COLOR_ATTACHMENT0_EXT;
	}

	return true;
}

void GLTarget::shutdown() {
	//glDeleteRenderbuffersEXT( 1 &GLDepth );
	glDeleteFramebuffersEXT( 1, &GLFBO );
}

void GLTarget::attach( const shared_ptr<DataTexture>& dt, size_t i ) {
	const shared_ptr<GLTexture> tex = boost::shared_static_cast<GLTexture, Resource>( dt->RenderData );

	glBindFramebufferEXT( GL_FRAMEBUFFER_EXT, GLFBO );
	glFramebufferTexture2DEXT(GL_FRAMEBUFFER_EXT, GL_COLOR_ATTACHMENT0_EXT + (GLenum)i, GL_TEXTURE_2D, tex->GLTex, 0);
	glBindFramebufferEXT( GL_FRAMEBUFFER_EXT, 0 );
}

void GLTarget::save( size_t target_index, vector<float>& data ) {
	if( target_index >= Targets.size() )	return;

	glReadBuffer( Targets[ target_index ] );

	//get index into attachements and do sanity check
	size_t tex_index = Targets[ target_index ] - GL_COLOR_ATTACHMENT0_EXT;
	if( tex_index  > 20 )					return;

	const shared_ptr<DataTexture>& tex = Attachments[ tex_index ];
	if( tex->Type != DataTexture::FLOAT || tex->Prec != DataTexture::FLOAT32 )
		return;

	GLenum glfrmt = (tex->NComponents == 3)? GL_RGB:
					(tex->NComponents == 4)? GL_RGBA: GL_RED;

	data.resize( tex->Size, 0.0f );
	glReadPixels( 0, 0, tex->Width, tex->Size / tex->Width / tex->NComponents, glfrmt, GL_FLOAT, &data[0] );
}

/////////////////////////////////////////////////////////////////////////////////////////
//GLFont

bool GLFont::initialize( const std::string &name )
{
	LOG_INFO("Creating font");
	_Texture = shared_ptr< Texture >( new Texture(name) );
	_Renderer->load_texture( _Texture );

	LOG_INFO("Creating font display list");
	float x, y;

	_DisplayList = glGenLists(256);
	_Renderer->apply_render_state( _Texture );
	_ActiveColor = Color( Vector3ub( 255, 255, 255 ) );

	for (int i=0; i<256; ++i)
	{
		x = float(i%16)/16.0f;
		y = float(i/16)/16.0f;

		glNewList( _DisplayList + i, GL_COMPILE );
			glBegin( GL_QUADS );
				glTexCoord2f( x+0.0125f, 1-y-0.0625f );
				glVertex2i( 0, 0 );
				glTexCoord2f( x+0.075f,	1-y-0.0625f );
				glVertex2i( 16, 0 );
				glTexCoord2f( x+0.075f, 1-y );
				glVertex2i( 16, 16 );
				glTexCoord2f( x+0.0125f, 1-y );
				glVertex2i( 0, 16 );
			glEnd();
			glTranslated( 10, 0, 0);
		glEndList();
	}

	LOG_SUCCESS( "Font created successfully -- " + name );
	return true;
}

void GLFont::shutdown() {
}

void GLFont::print( const Vector2d &pos, const std::string &text )
{
	_Renderer->apply_render_state( _Texture );

	glDisable( GL_DEPTH_TEST );
	glColor3ub( _ActiveColor.RawColor.r, _ActiveColor.RawColor.g, _ActiveColor.RawColor.b );

	glMatrixMode( GL_MODELVIEW );
	glPushMatrix();
	glLoadIdentity();
	glTranslated( pos.x, pos.y, -1 );

	glListBase( _DisplayList - 32 );
	glCallLists( (GLsizei)text.length(), GL_UNSIGNED_BYTE, text.c_str() );

	glMatrixMode( GL_MODELVIEW );
	glPopMatrix();

	glColor3d( 1.0, 1.0, 1.0 );
	glEnable( GL_DEPTH_TEST );
}

uchar GLFont::add_color(const std::string &name, float r, float g, float b)
{
	Color color( Vector3ub( (uchar)(r*255), (uchar)(g*255), (uchar)(b*255) ) );

	uchar pos = (uchar)_Colors.size();
	_Colors.push_back( color );
	_Indices[ name ] = pos;

	return pos;
}

void GLFont::select_color(const std::string &name)
{
	_ActiveIndex = _Indices[ name ];
	_ActiveColor = _Colors[ _ActiveIndex ];
}

void GLFont::select_color(uchar index)
{
	_ActiveIndex = index;
	_ActiveColor = _Colors[ index ];
}

uchar GLFont::get_color()
{
	return _ActiveIndex;
}