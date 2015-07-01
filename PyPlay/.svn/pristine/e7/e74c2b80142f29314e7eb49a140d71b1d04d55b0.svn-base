
#include "controller.h"

void PlayerController::control( Map& m ) {
	KB_INPUT in = input->keys_pressed();

	// these directions correspond to the order of the keyboard arrow constants
	Direction arrow_dir_map[] = { WEST, NORTH, EAST, SOUTH };
	if( in >= K_LEFT && in <= K_DOWN )	m.apply( shared_ptr<Action>(new MoveAction( character, arrow_dir_map[ in - K_LEFT ] )) );

	// these directions correspond to order of numeric constants
	Direction num_dir_map[] = { SOUTH_WEST, SOUTH, SOUTH_EAST, WEST, SELF, EAST, NORTH_WEST, NORTH, NORTH_EAST };
	if( in >= K_1 && in <= K_9 )		m.apply( shared_ptr<Action>(new MoveAction( character, num_dir_map[ in - K_1 ] )) );
}
