
#include <boost/python.hpp>

#include "world.hpp"

using namespace boost::python;
void wrap_world() {
	class_< World >( "World" )
		.def( "add_system", &World::add_system )
		.def( "add_entity", &World::add_entity )
		.def( "remove_entity", &World::remove_entity )
		.def( "update", &World::update )
		;
}

void World::add_system( System::pointer_type sys ) {
	systems.push_back( sys );
}

void World::add_entity( Entity::pointer_type ent ) {
	added.push_back( ent );
}

void World::remove_entity( Entity::pointer_type ent ) {
	removed.push_back( ent );
}

void World::update( ) {
	for( system_container::iterator sys = systems.begin(); 
		sys != systems.end(); ++sys ) {
		(*sys)->begin();
	}

	entity_update_list::iterator update;
	for( update = added.begin(); update != added.end(); ++update )
		entities[ (*update)->id() ] = *update;
	for( update = removed.begin(); update != removed.end(); ++update )
		entities.erase( (*update)->id() );

	for( entity_container::iterator ent = entities.begin();
		ent != entities.end(); ++ent )
	for( system_container::iterator sys = systems.begin(); 
		sys != systems.end(); ++sys ) {
		(*sys)->update( ent->second );
	}

	system_container::iterator sys = systems.end(); 
	do {
		--sys;
		(*sys)->end();
	} while( sys != systems.begin() );
}

