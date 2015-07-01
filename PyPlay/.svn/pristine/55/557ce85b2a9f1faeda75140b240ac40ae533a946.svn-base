#include "sdlrenderer.h"

void export_sdlrenderer()
{
	/*
	class_<SDLRenderer, bases<Renderer> >( "sdlrenderer", init< const Vector2d&, bool >() )
		.def( "initialize", &SDLRenderer::initialize )
		.def( "start_frame", &SDLRenderer::start_frame )
		.def( "end_frame", &SDLRenderer::end_frame );

	register_ptr_to_python< shared_ptr<SDLRenderer> >();
	*/
}

void export_sdlfont()
{
	/*
	class_<SDLFont, bases<Font> >( "sdlfont", init< const string&, shared_ptr<Renderer> >() )
		.def( "add_color", &SDLFont::add_color )
		.def( "select_color", (void (SDLFont::*)(const string&))(&SDLFont::select_color) )
		.def( "write", &SDLFont::print );
	
	register_ptr_to_python< shared_ptr<SDLFont> >();
	*/
}

bool SDLRenderer::initialize(const Vector2d &screendim, bool fullscreen)
{
	if(SDL_Init( SDL_INIT_VIDEO | SDL_INIT_TIMER | SDL_INIT_NOPARACHUTE ) == -1)
	{
		LOG_ERR("Could not initialize SDL");
		LOG_ERR(SDL_GetError());
		return false;
	}

    if(!(_Screen = SDL_SetVideoMode(screendim.x, screendim.y, 0, SDL_HWSURFACE | SDL_ANYFORMAT | SDL_DOUBLEBUF)))
		throw g5Exception("display", "no sdl display: " + string(SDL_GetError()), false);

    SDL_WM_SetCaption("C2", "app.ico");

    //make things easy for us, have sdl send us key repeat signals
    SDL_EnableKeyRepeat(SDL_DEFAULT_REPEAT_DELAY, SDL_DEFAULT_REPEAT_INTERVAL);

    //give us the correct mapped keys with shift, we just ignore 2byte characters
    SDL_EnableUNICODE(1);

	_Dimensions.x = _Screen->w;
    _Dimensions.y = _Screen->h;

	return true;
}

void SDLRenderer::shutdown()
{
	if( _Screen )
		SDL_Quit();

	_Screen = NULL;
}

void SDLRenderer::start_frame()
{
	SDL_FillRect(_Screen, NULL, 0);		//fill the entire screen black
}

void SDLRenderer::end_frame()
{
	SDL_Flip( _Screen );
}

void SDLRenderer::draw_simple_quad_ortho( const Vertex &vert1, const Vertex &vert2 )
{
	Vector2d screenpos( (short)vert1.Coordinates.x, (short)vert1.Coordinates.y );
	Vector2d screendim( (short)vert2.Coordinates.x, (short)vert2.Coordinates.y );
	screendim = screendim - screenpos;

	Vector2d texstart( (ushort)vert1.TexCoordinates.x, (ushort)vert1.TexCoordinates.y );
	draw_simple_quad_ortho( screenpos, screendim, texstart );
}

void SDLRenderer::draw_simple_quad_ortho( const Vector2d &screenpos, const Vector2d &screendim, const Vector2d &texstart )
{
	SDL_Rect dest;
	dest.x = screenpos.x;	dest.y = screenpos.y;

	if( _UseColor )
	{
		dest.w = screendim.x;	dest.h = screendim.y;
		int res = SDL_FillRect( _Screen, &dest, _DrawColor );
		res += 3;
	}
	else
	{
		SDL_Rect src;
		src.x = texstart.x;				src.y = texstart.y;
		src.w = screendim.x;			src.h = screendim.y;
		int res = SDL_BlitSurface( _DrawTextureRaw, &src, _Screen, &dest );
		res += 3;
	}

#ifdef _DEBUG
	const char* err = SDL_GetError();
	if( strlen(err) )
		LOG_ERR( err );
#endif
}

void SDLRenderer::draw_simple_quad_ortho( const Vector2d &screenpos, const Vector2d &screendim )
{
	Vector2d texstart;
	draw_simple_quad_ortho( screenpos, screendim, texstart );
}

void SDLRenderer::apply_render_state( const shared_ptr<State> state )
{
	if( state->SpecType == Resource::TEXTURE && state->RenderData )
	{
		_DrawTexture = boost::shared_static_cast<Texture, State>( state );
		if( !_DrawTexture->RenderData ) return;
		_UseColor = false;

		shared_ptr<SDLTexture> raw = boost::shared_static_cast<SDLTexture, Resource>( _DrawTexture->RenderData );
		_DrawTextureRaw = raw->Surface;
	}
	else if( state->SpecType == Resource::FLAT_COLOR )
	{
		_UseColor = true;
		shared_ptr<Color> c = boost::shared_static_cast<Color, State>( state );

		Vector3ub color = c->RawColor;
		_DrawColor = SDL_MapRGB( _Screen->format, color.r, color.g, color.b );
	}
}

void SDLRenderer::load_texture( boost::shared_ptr<State> data)
{
	shared_ptr<Resource> sdltex( new SDLTexture( data ) );
	data->RenderData = sdltex;
}

void SDLRenderer::set_texture_color_key( shared_ptr<State> tex, uint color )
{
	if( !tex->RenderData )		return;

	shared_ptr<SDLTexture> raw = boost::shared_static_cast<SDLTexture, Resource>( tex->RenderData );
	SDL_SetColorKey( raw->Surface, SDL_SRCCOLORKEY | SDL_RLEACCEL, color );
}


/////////////////////////////////////////////////////////////////////////////////////////
//SDLTexture

bool SDLTexture::initialize( const shared_ptr<Resource> res )
{
	if( res->SpecType != Resource::TEXTURE )
		return false;

	const shared_ptr<Texture> tex = boost::static_pointer_cast<Texture, Resource>( res );

	tex->reverse_data();
	Surface = SDL_CreateRGBSurfaceFrom( tex->PixelData, tex->Width, tex->Height, tex->Bpp, tex->Width * 3,
										tex->RMASK, tex->GMASK, tex->BMASK, tex->AMASK );
	//Surface = SDL_LoadBMP( tex->Name.c_str() );

	if( !Surface )
		return false;
	return true;
}

bool SDLTexture::initialize( const string& filename, shared_ptr<Renderer> rend )
{
	shared_ptr<Resource> res = Resource::load( filename, rend );
	if( !res )	return false;

	return initialize( res );
}

void SDLTexture::shutdown()
{
	if( Surface )
		SDL_FreeSurface( Surface );
}

/////////////////////////////////////////////////////////////////////////////////////////
//SDLFont
bool SDLFont::initialize( const std::string &name )
{
	_Name = name;

	shared_ptr<Resource> res = Resource::load( name, _Renderer );
	_Current = boost::shared_static_cast<State, Resource>( res );
	if( !_Current ) return false;

	_Renderer->load_texture( _Current );
	_Renderer->set_texture_color_key( _Current, 0 );		//black = transparent
	
	_Indices["white"] = 0;
	_CurrentIndex = 0;
	_Colors.push_back(_Current);

	return true;
}

void SDLFont::shutdown()
{
}

void SDLFont::print( const Vector2d& screenpos_, const string& strtext )
{
	_Renderer->apply_render_state( _Current );
	const char* text = strtext.c_str();

	uint textlength = static_cast<uint>(strlen(text));

	Vector2d screenpos = screenpos_;
	Vector2d screendim( FONT_HEIGHT - 1, FONT_HEIGHT );

	for(uint pos=0; pos<textlength; ++pos)
	{
		char val = text[pos]-32;
		
		Vector2d tex(	(val % (TEX_HEIGHT/FONT_HEIGHT)) * FONT_HEIGHT + 1,
						(val / (TEX_HEIGHT/FONT_HEIGHT)) * FONT_HEIGHT );

		_Renderer->draw_simple_quad_ortho( screenpos, screendim, tex );
		screenpos.x += FONT_WIDTH;
	}
	
}

uchar SDLFont::add_color( const string& name, float r, float g, float b )
{
	shared_ptr<Resource> res = Resource::load( name, _Renderer );
	shared_ptr<State> color = boost::shared_static_cast<State, Resource>( res );

	//check if we've cached this color before to save time
	if( color )
	{
		_Renderer->load_texture( color );
		_Renderer->set_texture_color_key( color, 0 );				//black = transparent

		_Indices[name] = static_cast<uchar>(_Colors.size());
		_Colors.push_back(color);
		return _Indices[name];
	}

	//load teh default and modify
	res = Resource::load( _Name, _Renderer );
	color = boost::shared_static_cast<State, Resource>( res );
	if( !color )
		return -1;

	shared_ptr<Texture> tex = boost::shared_static_cast<Texture, Resource>( color );
	uchar* pixels = tex->PixelData;
	for(int x=0; x < tex->Height * tex->Width; ++x)
	{
		uint index = x * tex->Bpp;
		if( pixels[index] != 0 || pixels[index+1] != 0 || pixels[index+2] != 0 )
		{
			pixels[index]   = static_cast<uchar>(pixels[index]   *r);
			pixels[index+1] = static_cast<uchar>(pixels[index+1] *g);
			pixels[index+2] = static_cast<uchar>(pixels[index+2] *b);
		}
	}

	//save this color out as a file to save time if possible
	tex->save( name + ".bmp" );

	//allow the sdl renderer to do some stuff here
	_Renderer->load_texture( color );
	_Renderer->set_texture_color_key( color, 0 );					//black = transparent;

	_Indices[name] = static_cast<uchar>(_Colors.size());
	_Colors.push_back(color);
	return _Indices[name];
}

void SDLFont::select_color( const string& name )
{
	if(_Indices.count(name) > 0)
	{
		_CurrentIndex = _Indices[name];
		_Current = _Colors[_CurrentIndex];
	}
}

void SDLFont::select_color( uchar index )
{
	_CurrentIndex = index;
	_Current = _Colors[index];
}	

uchar SDLFont::get_color()
{
	return _CurrentIndex;
}

ushort SDLFont::get_height()
{
	return FONT_HEIGHT;
}

ushort SDLFont::get_width()
{
	return FONT_WIDTH;
}

