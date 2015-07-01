#ifndef MAP__H
#define MAP__H

#pragma once

#include "stdafx.h"
#include "action.h"
#include "tile.h"

/////////////////////////////////////////////////////////////////////////////////////////
// Random map generation control structures
/////////////////////////////////////////////////////////////////////////////////////////
struct MapRandomConstraints {

};

struct MapRandomResults {
	Vector2d	player_location;
};

/////////////////////////////////////////////////////////////////////////////////////////
// Map utility structures
/////////////////////////////////////////////////////////////////////////////////////////
struct MapEntityPosition: public EntityPosition {
	MapEntityPosition( const Vector2d& p ): position( p )
	{ }

	virtual EntityPosition& move( Direction dir );
	virtual void place( const Vector2d& p );

	virtual void write( ostream& o ) const;
	virtual bool operator ==( const EntityPosition& other ) const;
	Vector2d	position;
};
ostream& operator <<( ostream& o, const EntityPosition& p );

struct Room {
	Room( const Vector2d& min_, const Vector2d& max_ ): min_pt( min_ ), max_pt( max_ ), dim( max_ - min_ )
	{ }

	bool overlaps( const Room& other) const;
	bool contains( const Vector2d& point ) const;
	bool intersects( const Vector2d& point1, const Vector2d& point2 ) const;

	Vector2d	min_pt, max_pt, dim;
	vector< Vector2d >	doors;
};

typedef std::vector<Vector2d> MapPath;

/////////////////////////////////////////////////////////////////////////////////////////
// Map data, represents actual state of world
/////////////////////////////////////////////////////////////////////////////////////////
class MapRow {
public:
	MapRow( size_t cols ): tiles( cols )
	{ }

	Tile& operator[]( size_t col ) {
		return tiles[ col ];
	}

	const Tile& operator[]( size_t col ) const {
		return tiles[ col ];
	}

private:
	vector< Tile >	tiles;
};

class Map {
public:
	Map( size_t rows_, size_t cols_ ): rows( rows_ ), cols( cols_ ), data( rows_, MapRow( cols_ ) )
	{ }

	MapRow& operator[]( size_t row ) {
		return data[ row ];
	}

	const MapRow& operator[]( size_t row ) const {
		return data[ row ];
	}

	Tile& operator[]( const Vector2d& pos ) {
		return data[ pos.x ][ pos.y ];
	}

	const Tile& operator[]( const Vector2d& pos ) const {
		return data[ pos.x ][ pos.y ];
	}

	void resolve();
	void apply( shared_ptr<Action> act );
	void apply( shared_ptr<MoveAction> act );
	void apply( shared_ptr<AttackAction> act );

	Tile& character_tile( shared_ptr< Character >& ch );
	Tile& character_adjacent_tile( shared_ptr< Character >& ch, Direction dir );
	bool is_move_possible( shared_ptr< Character >& ch, Direction dir );

	void place( shared_ptr< Character >& ch, const Vector2d& pos );

	static Map generate_random( const MapRandomConstraints& c, MapRandomResults& results );
	static Map load( const string& file );
	float h_score( Tile open, Vector2d goal);
	MapPath pathfind( Vector2d start, Vector2d end );

	size_t				rows, cols;
private:

	void generate_room( const Room& r );
	vector< MapRow >			data;
	vector< shared_ptr<Action> >	pending_actions;

	vector< shared_ptr<Item> >		master_items;
	vector< shared_ptr<Character> >	master_characters;	
};

/////////////////////////////////////////////////////////////////////////////////////////
// Visibility data per chracter, represents what they see and remember
/////////////////////////////////////////////////////////////////////////////////////////
class MapVisibilityRow {
public:
	MapVisibilityRow( size_t cols ): tiles( cols )
	{ }

	TileVisibility& operator[]( size_t col ) {
		return tiles[ col ];
	}

	const TileVisibility& operator[]( size_t col ) const {
		return tiles[ col ];
	}

private:
	vector< TileVisibility >	tiles;
};

class MapVisibility {
public:
	MapVisibility( const Map& m ): rows( m.rows ), cols( m.cols ), data( m.rows, MapVisibilityRow( m.cols ) )
	{ }

	MapVisibilityRow& operator[]( size_t row ) {
		return data[ row ];
	}

	const MapVisibilityRow& operator[]( size_t row ) const {
		return data[ row ];
	}

	void update( const Map& m, const shared_ptr<Character>& c );

	size_t						rows, cols;
private:
	vector< MapVisibilityRow >	data;
};

#endif
