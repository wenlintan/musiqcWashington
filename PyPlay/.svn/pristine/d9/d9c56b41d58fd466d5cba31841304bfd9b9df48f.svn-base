#ifndef SDL_RENDERER__H
#define SDL_RENDERER__H

#include "stdafx.h"

#include "renderer.h"
#include "texture.h"

#include <sdl.h>
#pragma comment(lib, "sdlmain.lib")
#pragma comment(lib, "sdl.lib")

void export_sdlrenderer();
void export_sdlfont();

class SDLRenderer: public Renderer
{
public:
	SDLRenderer(): _Screen(NULL), _UseColor( false )	
	{}

	SDLRenderer( const Vector2d& screendim, bool fullscreen ): _Screen(NULL), _UseColor( false )
	{
		if( !initialize( screendim, fullscreen ) )
			throw g5Exception("SDLRenderer", "Failed to initialize renderer", true);
	}

	~SDLRenderer()
	{
		shutdown();
	}

	//basic maintenance
	virtual bool initialize( const Vector2d& screendim, bool fullscreen );
	virtual void shutdown();
	
	virtual void start_frame();
	virtual void end_frame();

	//standard simple operations
	virtual void draw_simple_quad_ortho( const Vertex &vert1, const Vertex &vert2 );
	virtual void draw_simple_quad_ortho( const Vector2d &screenpos, const Vector2d &screendim, const Vector2d &texstart );
	virtual void draw_simple_quad_ortho( const Vector2d &screenpos, const Vector2d &screendim );

	virtual void apply_render_state( const shared_ptr<State> state );
	virtual void set_texture_color_key( shared_ptr<State> tex, uint color );

	virtual void load_texture( shared_ptr<State> data );

private:

	bool					_UseColor;
	uint					_DrawColor;

	shared_ptr<Texture>		_DrawTexture;
	SDL_Surface*			_DrawTextureRaw;


	SDL_Surface*	_Screen;
	Vector2d		_Dimensions;

};

class SDLTexture: public Resource
{
public:
	SDLTexture(): Surface(NULL)
	{}

	SDLTexture( const shared_ptr<Resource> res ): Surface(NULL)
	{
		if( !initialize( res ) )
			throw g5Exception("SDLTexture", "Failed to load data into texture", true);
	}

	virtual ~SDLTexture()
	{
		shutdown();
	}

	virtual bool initialize( const string& filename, shared_ptr<Renderer> rend );
	virtual bool initialize( const shared_ptr<Resource> res );
	virtual void shutdown();

	SDL_Surface*	Surface;
};

class SDLFont: public Font
{
public:
	const static ushort TEX_WIDTH = 256;
	const static ushort TEX_HEIGHT = 256;

	const static ushort FONT_WIDTH = 12;
	const static ushort FONT_HEIGHT = 16;

	SDLFont(): _CurrentIndex(-1)
	{}

	SDLFont( shared_ptr<Renderer> rend ): Font( rend ), _CurrentIndex(-1)
	{}

	SDLFont( const string& name, shared_ptr<Renderer> rend ): Font( rend ), _CurrentIndex(-1)
	{
		if( !initialize( name ) )
			throw g5Exception("SDLFont", "Failed to load font", true);
	}

	~SDLFont()
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

	virtual ushort get_height();
	virtual ushort get_width();

private:
	string		_Name;

	uchar						_CurrentIndex;
	shared_ptr<State>			_Current;

	map<string, uint>				_Indices;
	vector< shared_ptr<State> >		_Colors;
};

#endif