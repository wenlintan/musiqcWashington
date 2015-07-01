
#include <gtest/gtest.h>
#ifdef _DEBUG
#  pragma comment( lib, "gtestd-dll.lib" )
#else
#  pragma comment( lib, "gtest-dll.lib" )
#endif

#include "map.h"

class MoveActionMapTest: public ::testing::Test {
public:
	MoveActionMapTest()
	{ }

	virtual void SetUp() {
		MapRandomConstraints constraints;
		MapRandomResults results;

		map = shared_ptr<Map>( new Map(Map::generate_random( constraints, results )) );
		shared_ptr< Character > pc( new Character() );
		map->place( pc, results.player_location );
	}

	shared_ptr<Character>	pc;
	shared_ptr<Map>			map;
};

shared_ptr<Action> move_only_south( shared_ptr<Action> a ) {
	shared_ptr<MoveAction> ma = boost::shared_static_cast<MoveAction,Action>(a);
	ma->direction = SOUTH;
	return ma;
}

shared_ptr<Action> move_random( shared_ptr<Action> a ) {
	shared_ptr<MoveAction> ma = boost::shared_static_cast<MoveAction,Action>(a);
	ma->direction = (Direction)( dn(8) - 1 );
	return ma;
}

TEST_F( MoveActionMapTest, SimpleTest ) {
	shared_ptr<EntityPosition> orig_pos = pc->position();

	pc->on_move.add_trigger( Trigger::cb_type( boost::bind( &move_only_south, _1 ) ) );
	map->apply( shared_ptr<Action>( new MoveAction( pc, WEST ) ) );
	EXPECT_EQ( *pc->position(), orig_pos->move( SOUTH ) );
}

