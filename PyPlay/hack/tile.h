#ifndef TILE__H
#define TILE__H

#include "stdafx.h"

#include "character.h"
#include "item.h"

class TileStatus {
public:
	TileStatus(): wall( false ), wall_crossing( false ), paved( false ), mined( false ), wall_face( NORTH )
	{ }

	const bool& is_wall() const					{ return wall; }
	const bool& is_wall_crossing() const		{ return wall_crossing; }
	const Direction& wall_facing() const		{ return wall_face; }

	const bool& is_paved() const				{ return paved; }
	const bool& is_mined() const				{ return mined; }
	bool is_blocked() const						{ return !paved && !mined; }

	// non const versions
	bool& is_wall()					{ return wall; }
	bool& is_wall_crossing()		{ return wall_crossing; }
	Direction& wall_facing()		{ return wall_face; }

	bool& is_paved()				{ return paved; }
	bool& is_mined()				{ return mined; }

	friend bool operator ==( const TileStatus& s1, const TileStatus& s2 );
private:
	bool		wall, wall_crossing, paved, mined;
	Direction	wall_face;

};

bool operator ==( const TileStatus& s1, const TileStatus& s2 );

class Tile {
public:
	friend class TileVisibility;
	friend class Map;

	TileStatus& status(){
		return tile_status;
	}

	const TileStatus& status() const{
		return tile_status;
	}

	void engrave( const string& e, bool add );

	void dig_into();
	void dig_vertically( bool down );

	void remove_character()									{	character.reset();	}
	void place_character( shared_ptr<Character>& ch )		{	character = ch;	}

	shared_ptr<Character>		character;
	vector< shared_ptr<Item> >	items;

	Trigger		on_enter, on_enter_post;

public:
	string		engraving;
	TileStatus	tile_status;

	Vector2d 	origin, position;
	float 		g_score, h_score, f_score;
  	bool 		closed;
};

class TileVisibility {
public:
	TileStatus& status(){
		return tile_status;
	}

	const TileStatus& status() const {
		return tile_status;
	}

	void update( const Tile& t );
	const bool& is_dirty() const			{ return dirty; }
	bool& is_dirty()						{ return dirty; }

	shared_ptr<Character>		last_character;
	vector< shared_ptr<Item> >	last_items;

private:
	TileStatus			tile_status;
	size_t				update_round;
	bool				dirty;

	TileStatus			last_status;
};

#endif
