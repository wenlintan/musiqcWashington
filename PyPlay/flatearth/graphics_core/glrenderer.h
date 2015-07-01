#ifndef GL_RENDERER__H
#define GL_RENDERER__H

#include "stdafx.h"

#ifdef WIN32
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#pragma comment( lib, "opengl32.lib" )
#pragma comment( lib, "glu32.lib" )
#endif

#include <sdl.h>
#include <gl/gl.h>
#include <gl/glu.h>
#include "glext.h"

#include "renderer.h"
#include "texture.h"
#include "shader.h"
#include "render_target.h"
#include "light.h"
#include "camera.h"


void export_glrenderer();
void export_glfont();

class GLRenderer: public Renderer
{
public:

	GLRenderer(): _SDLSurface(NULL)
	{}

	GLRenderer( const Vector2d& screendim, bool fullscreen ): _SDLSurface(NULL)
	{
		if( !initialize( screendim, fullscreen ) )
			throw g5Exception("GLRenderer", "Failed to initialize renderer", true);
	}

	virtual ~GLRenderer()
	{ 
		shutdown(); 
	}

	//basic maintenance
	virtual bool initialize( const Vector2d& screendim, bool fullscreen );
	virtual void shutdown();

	virtual void start_frame();
	virtual void end_frame();
	
	//standard simple operations
	virtual void draw_simple_quad_ortho( const Vertex &vert1, const Vertex &vert2 ) {}
	virtual void draw_simple_quad_ortho( const Vector2d &screenpos, const Vector2d &screendim, const Vector2d &texstart ) {}
	virtual void draw_simple_quad_ortho( const Vector2d &screenpos, const Vector2d &screendim ) {}

	virtual void apply_render_state( const shared_ptr<State> state );

	virtual void set_texture_color_key( shared_ptr<State> tex, uint color )		{}
	virtual void load_texture( shared_ptr<State> data );
	virtual void disable_all_textures();

	virtual void set_shader_variable( shared_ptr<State> data, ShaderVariable& var );
	virtual void load_shader( shared_ptr<State> data );

	virtual void save_render_target( shared_ptr<State> targ, size_t target_index, vector<float>& data );
	virtual void load_render_target( shared_ptr<State> data );

	//3D operations
	virtual bool supports_3d_ops()								{ return true; }

	virtual bool vertex_source_proje( const vector<Vertex>& verts );
	virtual bool vertex_source_proje( const vector<ColorVertex>& verts );
	virtual bool vertex_source_proje( const vector<NormalVertex>& verts );
	virtual bool vertex_source_proje( const vector<Vector3f>& verts );
	
	virtual bool draw_vertices_proje( const DrawCallInfo& info );
	virtual bool draw_indices_proje(  const vector<ushort>& indices, const DrawCallInfo& info );
	virtual bool draw_simple_coords_proje( const vector<Vector3f> &verts, const DrawCallInfo& info );

	virtual bool release_vertex_source();

private:
	//checks for and logs opengl errors, should be checked after most opengl calls
	void check_errors();

	void apply_draw_call_info( const DrawCallInfo& info );
	void unapply_draw_call_info();
	void unset_client_states();

	static map< Renderer::VertexDataType, GLenum >	GLVertexTypeMap;

	Vector2d			_Dimensions;
	SDL_Surface*		_SDLSurface;

	uint				_VertexSourceSize;
	bool				_UseColor;
	Vector3ub			_Color;

	bool				_UseShaders, _UseMultiTexture, _UseFBOs;
	uint				_VertexProgram;

};

class GLTexture: public Resource
{
public:
	GLTexture(): GLTex(0)
	{}

	GLTexture( const shared_ptr<Resource> res ): GLTex(0)
	{
		if( !initialize( res ) )
			throw g5Exception("GLTexture", "Failed to load data into texture", true);
	}

	virtual ~GLTexture()
	{
		shutdown();
	}

	virtual bool initialize( const string& filename, shared_ptr<Renderer> rend );
	virtual bool initialize( const shared_ptr<Resource> res );
	virtual void shutdown();

	GLenum	GLTarget;
	uint	GLTex;
};

class GLProgram: public Resource
{
public:
	GLProgram(): GLProg(0), GLVertexShader(0), GLFragShader(0)
	{}

	GLProgram( const shared_ptr<Resource> res ): GLProg(0), GLVertexShader(0), GLFragShader(0)
	{
		if( !initialize( res ) )
			throw g5Exception("GLShader", "Failed to compile and link shader, check log for errors", true);
	}

	virtual ~GLProgram()
	{
		shutdown();
	}

	virtual bool initialize( const shared_ptr<Resource>& res );
	virtual void shutdown();

	uint GLProg, GLVertexShader, GLFragShader;
};

class GLTarget: public Resource
{
public:
	GLTarget(): GLFBO(0)
	{}

	GLTarget( const shared_ptr<Resource> res ): GLFBO(0)
	{
		if( !initialize( res ) )
			throw g5Exception("GLTarget", "Failed to create framebuffer_object", true);
	}

	virtual bool initialize( const shared_ptr<Resource>& res );
	virtual void shutdown();

	virtual void attach( const shared_ptr<DataTexture>& dt, size_t i );
	virtual void save( size_t target_index, vector<float>& data );

	uint									GLFBO, GLDepth;
	vector< uint >							Targets;
	vector< const shared_ptr<DataTexture> >	Attachments;
};

class GLFont: public Font
{
public:
	GLFont()
	{}

	GLFont( shared_ptr<Renderer> rend ): Font( rend )
	{}

	GLFont( const string& name, shared_ptr<Renderer> rend ): Font( rend )
	{
		if( !initialize( name ) )
			throw g5Exception("GLFont", "Failed to load font", true);
	}

	~GLFont()
	{
		shutdown();
	}

	virtual bool initialize( const string& name );
	virtual void shutdown();

	virtual void print( const Vector2d& pos, const string& text );

	virtual uchar add_color( const string& name, float r, float g, float b );
	virtual void select_color( const string& name );
	virtual void select_color( uchar index );
	virtual uchar get_color();

	virtual ushort get_height()			{ return 16; }
	virtual ushort get_width()			{ return 10; }

private:
	shared_ptr< Texture >		_Texture;
	GLuint						_DisplayList;

	uchar					_ActiveIndex;
	Color					_ActiveColor;

	vector< Color >			_Colors;
	map<string, uint>		_Indices;

};



#endif