
#include "renderer.h"

void TextRenderer::render( const MapVisibility& m ) {
	show_cursor( false );
	for( size_t r = 0; r < m.rows; ++r ) for( size_t c = 0; c < m.cols; ++c )
		if( m[r][c].is_dirty() )	put_glyph( glyph_map( m[r][c] ), c, r );
	show_cursor( true );
}

Glyph TextRenderer::glyph_map( const TileVisibility& t ) {
	if( t.last_character )	return monster_glyph_map( t.last_character );
	return tile_glyph_map( t.status() );
}

Glyph TextRenderer::monster_glyph_map( const weak_ptr<Character> &ch ) {
	Glyph result;
	result.bg_color = BLACK;	result.fg_color = WHITE;
	result.symbol = '@';

	return result;
}

Glyph TextRenderer::tile_glyph_map( const TileStatus& s ) {
	Glyph result;
	result.bg_color = BLACK;	result.fg_color = WHITE;

	if( s.is_wall() ) {
		if( s.is_wall_crossing() ) {
			switch( s.wall_facing() ) {
				case EAST:		result.symbol = 195;		break;
				case WEST:		result.symbol = 180;		break;
				case NORTH:		result.symbol = 193;		break;
				case SOUTH:		result.symbol = 194;		break;

				case NORTH_EAST:	result.symbol = 192;	break;
				case NORTH_WEST:	result.symbol = 217;	break;
				case SOUTH_WEST:	result.symbol = 191;	break;
				case SOUTH_EAST:	result.symbol = 218;	break;
			}
		} else {
			switch( s.wall_facing() ) {
				case EAST:		
				case WEST:		result.symbol = 179;		break;
				case NORTH:		
				case SOUTH:		result.symbol = 196;		break;
			}
		}
	} else {
		if( s.is_paved() )		result.symbol = 250;
		else if( s.is_mined() )	result.symbol = 178;
		else					result.symbol = ' ';
	}

	return result;
}
