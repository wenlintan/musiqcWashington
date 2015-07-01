
#include "tile.h"

bool operator ==( const TileStatus& s1, const TileStatus& s2 ) {
	return s1.wall == s2.wall && s1.wall_crossing == s2.wall_crossing &&
		s1.paved == s2.paved && s1.mined == s2.mined && s1.wall_face == s2.wall_face;
}

void TileVisibility::update( const Tile& t ) {
	if( status() == t.status() && last_character == t.character && last_items == t.items ) {
		dirty = false;
		return;
	}

	dirty = true;
	status() = t.status();

	last_character = t.character;
	last_items = t.items;
}
