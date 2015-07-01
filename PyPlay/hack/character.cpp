
#include "character.h"

void export_character() {
	using namespace boost::python;
	class_< Character, shared_ptr<Character> >( "Character" )
		.def_readwrite( "on_move", &Character::on_move )
	;
}
