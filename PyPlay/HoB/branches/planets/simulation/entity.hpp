
#pragma once

#include <map>

#include "transform.hpp"
#include "mesh.hpp"
#include "renderer_components.hpp"

#include "network.hpp"
#include "collision.hpp"

class Entity {
public:
	typedef boost::shared_ptr<Entity> pointer_type;
	typedef std::multimap< Component::Type, Component::pointer_type >
		component_storage_type;
	typedef component_storage_type::iterator component_iterator;
	typedef std::pair< component_iterator, component_iterator >
		component_range;

	Transform&		transform();
	Camera&			camera();
	Mesh&			mesh();

	CollisionMesh&	collision_mesh();
	NetworkView&	network_view();

	bool			has_component( Component::Type type );
	Component&		get_component( Component::Type type );
	component_range	get_components( Component::Type type );

	Entity();
	size_t	id() 	{ return identifier; }

	void 	add_component( Component::pointer_type component );
	void	remove_component( Component::pointer_type component );

private:
	static size_t current_identifier;

	size_t identifier;
	component_storage_type storage;
};




