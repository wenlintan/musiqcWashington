#ifndef RENDERER__H
#define RENDERER__H

#include "stdafx.h"
#include "resource.h"
#include "texture.h"
#include "shader.h"

void export_renderer();
void export_font();

struct Vertex
{
	Vertex()
	{}

	Vertex( Vector3f coord ): Coordinates( coord )
	{}

	Vertex( Vector3f coord, Vector2f tcoords ): Coordinates( coord ), TexCoordinates( tcoords ), Normal( 0.0f, 0.0f, 1.0f )
	{}

	Vertex( Vector3f coord, Vector2f tcoords, Vector3f norm ): Coordinates( coord ), TexCoordinates( tcoords ), Normal( norm )
	{}

	Vector2f		TexCoordinates;
	Vector3f		Normal;
	Vector3f		Coordinates;
};

struct ColorVertex
{
	ColorVertex()
	{}

	ColorVertex( const Vector3f& pos, const Vector3f& color ): Coordinates(pos), Color(color)
	{}

	Vector3f		Color;
	Vector3f		Coordinates;
};

struct NormalVertex
{
	NormalVertex()
	{}

	NormalVertex( const Vector3f& pos, const Vector3f& norm ): Coordinates(pos), Normal(norm)
	{}

	Vector3f		Normal;
	Vector3f		Coordinates;
};

struct Culling: public State
{
	Culling(): State( Resource::CULLING )
	{}

	Culling( bool enabled_, bool front_ ): State( Resource::CULLING ), enabled( enabled_ ), front( front_ )
	{}

	bool enabled;
	bool front;
};


//declared after Renderer to use VertexDataType
struct DrawCallInfo;

class Renderer
{
public:

	enum VertexDataType{ POINT = 0, LINE_STRIP, LINE, TRI_STRIP, TRI, QUAD_STRIP, QUAD };

	Renderer()				{}
	virtual ~Renderer()		{}

	//basic maintenance
	virtual bool initialize( const Vector2d& screendim, bool fullscreen ) = 0;
	virtual void shutdown() = 0;

	virtual void start_frame() = 0;
	virtual void end_frame() = 0;
	
	//standard simple operations
	virtual void draw_simple_quad_ortho( const Vertex &vert1, const Vertex &vert2 ) = 0;
	virtual void draw_simple_quad_ortho( const Vector2d &screenpos, const Vector2d &screendim, const Vector2d &texstart ) = 0;
	virtual void draw_simple_quad_ortho( const Vector2d &screenpos, const Vector2d &screendim ) = 0;

	virtual void apply_render_state( const shared_ptr<State> state ) = 0;

	virtual void set_texture_color_key( shared_ptr<State> tex, uint color ) = 0;
	virtual void load_texture( shared_ptr<State> data ) = 0;
	virtual void disable_all_textures() = 0;

	virtual void set_shader_variable( shared_ptr<State> data, ShaderVariable& var ) = 0;
	virtual void load_shader( shared_ptr<State> data ) = 0;

	virtual void save_render_target( shared_ptr<State> targ, size_t target_index, vector<float>& data ) = 0;
	virtual void load_render_target( shared_ptr<State> data ) = 0;

	Vector3f	CameraPosition;
	virtual bool supports_3d_ops()								{ return false; }

	virtual bool vertex_source_proje( const vector<Vertex>& verts )				{ return true; }
	virtual bool vertex_source_proje( const vector<ColorVertex>& verts )		{ return true; }
	virtual bool vertex_source_proje( const vector<NormalVertex>& verts )		{ return true; }
	virtual bool vertex_source_proje( const vector<Vector3f>& verts )			{ return true; }
	
	virtual bool draw_vertices_proje( const DrawCallInfo& info )										{ return true; }
	virtual bool draw_indices_proje(  const vector<ushort>& indices, const DrawCallInfo& info )			{ return true; }
	virtual bool draw_simple_coords_proje( const vector<Vector3f> &verts, const DrawCallInfo& info )	{ return true; }

	virtual bool release_vertex_source()						{ return true; }

};

class Font
{
public:
	Font()			
	{}

	Font( shared_ptr<Renderer> rend ): _Renderer(rend)
	{}

	virtual bool initialize( const string& name ) = 0;
	virtual void shutdown() = 0;

	virtual void print( const Vector2d& pos, const string& text ) = 0;

	virtual uchar add_color( const string& name, float r, float g, float b ) = 0;
	virtual void select_color( const string& name ) = 0;
	virtual void select_color( uchar index ) = 0;
	virtual uchar get_color() = 0;

	virtual ushort get_height() = 0;
	virtual ushort get_width() = 0;

protected:
	shared_ptr<Renderer>	_Renderer;
};

struct DrawCallInfo
{
	//handles data for the general vertex draw calls
	//translation and color can be set through apply_render_state, but this method is more direct
	//translation and color only persist for the duration of the draw call

	const static Vector3f default_translation, default_rotation;
	const static Color default_color;

	enum BlendMethod { SOURCE, DEST, SOURCE_DEST };

	DrawCallInfo(): type( Renderer::TRI ), start(0), numdraw(-1), translation( default_translation ), rotation( default_rotation), color( default_color ), ccw( true )
	{}

	DrawCallInfo(	Renderer::VertexDataType datatype, uint num_to_draw = -1,
					const Vector3f& trans = default_translation, const Vector3f& rot = default_rotation,
					const Color& allcolor = default_color, bool counterclock = true	):
													type( datatype ), start( 0 ), numdraw( num_to_draw ),
													translation( trans ), rotation( rot ), color( allcolor ), ccw( counterclock )
	{}

	void blend( bool active, BlendMethod meth = SOURCE ) {
		blend_enabled = active;
		blend_method = meth;
	}

	Renderer::VertexDataType	type;
	uint						start, numdraw;
	Vector3f					translation, rotation;
	Color						color;
	bool						ccw;

	bool						blend_enabled;
	BlendMethod					blend_method;
};




#endif