#ifndef RENDERER__H
#define RENDERER__H

#pragma once

#include "map.h"

class Renderer {
public:
	virtual void render( const MapVisibility& m ) = 0;
};

struct Glyph {
	uchar	symbol;
	Color	fg_color, bg_color;
};

class TextRenderer: public Renderer {
public:
	virtual void render( const MapVisibility& m );

private:
	Glyph glyph_map( const TileVisibility& t );
	Glyph monster_glyph_map( const weak_ptr<Character>& ch );
	Glyph tile_glyph_map( const TileStatus& s );
	
	virtual void clear_screen() = 0;
	virtual void show_cursor( bool vis ) = 0;

	virtual void put_cursor( ushort x, ushort y ) = 0;
	virtual void put_glyph( const Glyph& g, ushort x, ushort y ) = 0;
	virtual void put_string( const string& s, ushort x, ushort y ) = 0;
	vector<Glyph>	glyphs;
};

class WindowsTextRenderer: public TextRenderer {
public:
	WindowsTextRenderer()
	{ }

private:
	virtual void clear_screen();
	virtual void show_cursor( bool vis );

	virtual void put_cursor( ushort x, ushort y );
	virtual void put_glyph( const Glyph& g, ushort x, ushort y );
	virtual void put_string( const string& s, ushort x, ushort y );
};

class X11TextRenderer: public TextRenderer {
public:
	X11TextRenderer()
	{ }

private:
	virtual void clear_screen();
	virtual void show_cursor( bool vis );

	virtual void put_cursor( ushort x, ushort y );
	virtual void put_glyph( const Glyph& g, ushort x, ushort y );
	virtual void put_string( const string& s, ushort x, ushort y );
};

#endif
