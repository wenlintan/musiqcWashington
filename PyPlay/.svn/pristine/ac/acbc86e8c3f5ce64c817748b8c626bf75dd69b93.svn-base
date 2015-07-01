
#include "action.h"

#include "map.h"
#include "entity.h"

void export_action() {
	using namespace boost::python;
	enum_< Action::ActionType >( "ActionType" )
		.value( "MOVE", Action::MOVE )
		.value( "ATTACK", Action::ATTACK )
		.export_values()
	;

	class_< Action, shared_ptr<Action>, boost::noncopyable >( "Action", no_init )
		.def_readwrite( "type", &Action::type )
		.def_readwrite( "actor", &Action::actor )
	;

	class_< MoveAction, shared_ptr<MoveAction>, bases<Action> >( "MoveAction", init<const shared_ptr<Entity>&, Direction>() )
		.def_readwrite( "direction", &MoveAction::direction )
	;

	class_< AttackAction, shared_ptr<AttackAction>, bases<Action> >( "AttackAction", init<const shared_ptr<Entity>&, const shared_ptr<Entity>&>() )
		.def_readwrite( "other", &AttackAction::other )
	;

}

#define DEFINE_MAP_VISITOR( type )		void type::apply( shared_ptr<Action> act, Map& m ) { \
	m.apply( boost::shared_static_cast<type,Action>(act) ); \
}

DEFINE_MAP_VISITOR( MoveAction );
DEFINE_MAP_VISITOR( AttackAction );
