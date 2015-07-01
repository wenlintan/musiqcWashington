
#pragma once

#include <vector>
#include <list>
#include <map>

#include "system.hpp"

void wrap_world();

class World {
	typedef std::vector< System::pointer_type > system_container;
	system_container systems;

	typedef std::list< Entity::pointer_type > entity_update_list;
	entity_update_list added, removed;

	typedef std::map< size_t, Entity::pointer_type > entity_container;
	entity_container entities;

public:
	void add_system( System::pointer_type sys );

	void add_entity( Entity::pointer_type ent );
	void remove_entity( Entity::pointer_type ent );

	void update();
};

