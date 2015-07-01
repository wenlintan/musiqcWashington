
#include "map.h"

bool Room::contains( const Vector2d& pt ) const {
	if( pt.x >= min_pt.x && pt.x <= max_pt.x && pt.y >= min_pt.y && pt.y <= max_pt.y ) 
		return true;
	return false;
}

bool Room::overlaps( const Room& other ) const {
	if( intersects( other.min_pt, other.min_pt + Vector2d( 0, other.dim.y ) ) ||
		intersects( other.min_pt, other.min_pt + Vector2d( other.dim.x, 0 ) ) ||
		intersects( other.max_pt, other.max_pt - Vector2d( 0, other.dim.y ) ) || 
		intersects( other.max_pt, other.max_pt - Vector2d( other.dim.x, 0 ) ) ||
		other.contains( min_pt ) )
		 return true;
	return false;
}
	
bool Room::intersects( const Vector2d& point1, const Vector2d& point2 ) const {
	if( contains(point1) || contains(point2) ) return true;
	if( (point1.x >= min_pt.x && point1.x <= max_pt.x && point1.y <= min_pt.y && point2.y >= max_pt.y) ||
		(point1.x >= min_pt.x && point1.x <= max_pt.x && point2.y <= min_pt.y && point1.y >= max_pt.y) ||
		(point1.y >= min_pt.y && point1.y <= max_pt.y && point1.x <= min_pt.x && point2.x >= max_pt.x) ||
		(point1.y >= min_pt.y && point1.y <= max_pt.y && point2.x <= min_pt.x && point1.x >= max_pt.x) )
		 return true; 
	return false;

}

MapPath Map::pathfind( Vector2d start, Vector2d goal ){
	set< pair < float , Vector2d > > open;

	Tile& start_tile = (*this)[ start ];
	start_tile.position = start;
	start_tile.g_score = 0;
	start_tile.h_score = h_score( start_tile, goal );
	start_tile.f_score = start_tile.h_score;

	open.insert( make_pair( (*this)[ start ].f_score, start ) );
	size_t icount = 0;
	  
	while( !open.empty() ) {
		if( icount++ > 100 ) 	break;

		Tile& current = (*this)[ open.begin()->second ]; 
		open.erase( open.begin() );
		current.closed = true;

		if( current.position == goal ) 		break;
		if( current.status().is_blocked() ) 	continue;

		Vector2d diffs[] = { Vector2d(1,0), Vector2d(-1,0), Vector2d(0,1), Vector2d(0,-1) };
		for( int i = 0; i < sizeof(diffs)/sizeof(Vector2d); ++i ) {
			Vector2d new_position = current.position + diffs[i];
			Tile& new_tile = (*this)[ new_position ];

			if( new_tile.closed ) continue;

			float new_g = current.g_score + 1;
			bool better_g = false;

			if( new_tile.g_score < 0 ){
				new_tile.h_score = h_score( (*this)[ new_position ], goal );
				better_g = true;

			} else if( new_g < new_tile.g_score ) {
				open.erase( make_pair( new_tile.f_score, new_position ) );
				better_g = true;
			}

			if( better_g ) {
				new_tile.g_score = new_g;
				new_tile.f_score = new_tile.h_score + new_tile.g_score;
				new_tile.origin = current.position;
				open.insert( make_pair( new_tile.f_score, new_position ) );
			}
		}
	}

	MapPath path;
	Vector2d pos = goal;

	while( pos != start ) {
		path.push_back( pos );
		pos = (*this)[ pos ].origin;
	}

	return path;
}

float Map::h_score( Tile open, Vector2d goal ){
	return (goal - open.position).length();
}


EntityPosition& MapEntityPosition::move( Direction dir ) {
	position += DirectionOffsets[ dir ];
	return *this;
}

void MapEntityPosition::place( const Vector2d& p ) {
	position = p;
}

void MapEntityPosition::write( ostream& o ) const {
	o << position;
}

bool MapEntityPosition::operator ==( const EntityPosition& other ) const {
	const MapEntityPosition* conv = dynamic_cast<const MapEntityPosition*>( &other );
	if( !conv )		return false;

	return position == conv->position;
}

void Map::resolve() {
	for( size_t i = 0; i < pending_actions.size(); ++i )
		apply( pending_actions[ i ] );

	pending_actions.resize( 0 );
}

void Map::apply( shared_ptr<Action> act ) {
	act->apply( act, *this );
}

void Map::apply( shared_ptr<MoveAction> act ) {

	shared_ptr<Character> ch = boost::shared_static_cast<Character,Entity>( act->actor );
	vector< shared_ptr<Character> >::iterator i = std::find( master_characters.begin(), master_characters.end(), ch );
	if( i == master_characters.end() )		return;	

	if( !act->triggered ) {
		shared_ptr<Action> base_act( act );
		base_act = ch->on_move.invoke( base_act );
		base_act = character_adjacent_tile( ch, act->direction ).on_enter.invoke( base_act );

		pending_actions.push_back( base_act );
	} else {
		if( is_move_possible( ch, act->direction ) ) {
			character_tile( ch ).remove_character();
			ch->position()->move( act->direction );

			character_tile( ch ).place_character( ch );
			character_tile( ch ).on_enter_post.invoke( act );
		}
	}
}

void Map::apply( shared_ptr<AttackAction> act ) {
}

Tile& Map::character_tile( shared_ptr< Character >& ch ) {
	Vector2d pos = boost::shared_static_cast<MapEntityPosition>( ch->position() )->position;
	return data[ pos.y ][ pos.x ];
}

Tile& Map::character_adjacent_tile( shared_ptr< Character >& ch, Direction dir ) {
	Vector2d pos = boost::shared_static_cast<MapEntityPosition>( ch->position() )->position + DirectionOffsets[ dir ];
	return data[ pos.y ][ pos.x ];
}

bool Map::is_move_possible( shared_ptr< Character >& ch, Direction dir ) {
	Vector2d pos = boost::shared_static_cast<MapEntityPosition>( ch->position() )->position + DirectionOffsets[ dir ];
	return !data[ pos.y ][ pos.x ].status().is_blocked();
}

void Map::place( shared_ptr< Character >& ch, const Vector2d& pos ) {
	ch->position() = shared_ptr<MapEntityPosition>( new MapEntityPosition( pos ) );
	character_tile( ch ).place_character( ch );

	master_characters.push_back( ch );
}

void Map::generate_room( const Room& r ){

	int x_min = r.min_pt.x, x_max = r.max_pt.x, y_min = r.min_pt.y, y_max = r.max_pt.y;
	for( int i = y_min; i <= y_max; i++) for( int j = x_min; j <= x_max; j++) {
		if( i == y_min || i == y_max ) {
			data[i][j].status().is_wall() = true;
			if ( i == x_min )						data[i][j].status().wall_facing() = SOUTH;
			if ( i == x_max )						data[i][j].status().wall_facing() = NORTH;
		} 
		else if( j == x_min || j == x_max ) {
			data[i][j].status().is_wall() = true;
			if ( j == x_min )						data[i][j].status().wall_facing() = EAST;
			if ( j == x_max )						data[i][j].status().wall_facing() = WEST;
		} 
		else {
			data[i][j].status().is_paved() = true;
		}
	}

	data[y_min][x_min].status().is_wall_crossing() = true;			data[y_min][x_min].status().wall_facing() = SOUTH_EAST;
	data[y_max][x_min].status().is_wall_crossing() = true;			data[y_max][x_min].status().wall_facing() = NORTH_EAST;
	data[y_min][x_max].status().is_wall_crossing() = true;			data[y_min][x_max].status().wall_facing() = SOUTH_WEST;
	data[y_max][x_max].status().is_wall_crossing() = true;			data[y_max][x_max].status().wall_facing() = NORTH_WEST;
}

Map Map::generate_random( const MapRandomConstraints& c, MapRandomResults& res ) {

	const int x_dimension = 75, y_dimension = 20;
	Map m( y_dimension, x_dimension );
	vector< Room > room_vector;

	size_t n_rooms = hack_range( 5, 12 );
	for( size_t i = 0; i < n_rooms; i++){

		Vector2d dim( hack_range( 5, 9 ), hack_range( 4, 8 ) );
		size_t tries = 0, j;

		while( tries < 20 ) {
			++ tries;

			Vector2d min_pt( hack_range( 1, x_dimension-dim.x-2 ), hack_range( 1, y_dimension-dim.y-2 ) );
			Vector2d max_pt = min_pt + dim;
			Room r( min_pt, max_pt );
			
			if( i != 0 ) {
				for( j = 0; j < room_vector.size(); j++ ) {
					if( r.overlaps( room_vector[j] ) )
						break;
				}

				if( j != room_vector.size() )	continue;
			}

			if( !room_vector.size() )
				res.player_location = r.min_pt + Vector2d( 2, 2 );

			room_vector.push_back( r );
			m.generate_room( r );
			break;
		}
	}

	return m;
}

Map Map::load( const string& file ) {
	return Map( 20, 75 );
}

void MapVisibility::update( const Map& m, const shared_ptr<Character>& c ) {
	for( size_t r = 0; r < m.rows && r < rows; ++r ) for( size_t c = 0; c < m.cols && c < cols; ++c )
		(*this)[ r ][ c ].update( m[ r ][ c ] );
}

