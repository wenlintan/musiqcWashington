
#include <boost/python.hpp>

#include "perlin.hpp"
#include "entity.hpp"

// Included to expose to python
#include "system.hpp"
#include "renderer.hpp"
#include "event.hpp"
#include "roam.hpp"
#include "rocket_system.hpp"

#include "world.hpp"

using namespace boost::python;
static list wrap_get_components( Entity::pointer_type e, Component::Type t ) {
	Entity::component_range range = e->get_components( t );

	list result;
	Entity::component_iterator iter = range.first;
	while( iter != range.second ) {
		result.append( iter->second );
		++iter;
	}

	return result;
}

BOOST_PYTHON_MODULE( simulation ) {
	wrap_vector();
	wrap_matrix();

	wrap_perlin();
	wrap_component();

	wrap_transform();
	wrap_mesh();
	wrap_renderer_components();
	wrap_collision();
	wrap_network();

	class_<Entity, Entity::pointer_type, boost::noncopyable>( "Entity" ) 
		.def( "transform", &Entity::transform,
				return_internal_reference<1>() )
		.def( "camera", &Entity::camera,
				return_internal_reference<1>() )
		.def( "mesh", &Entity::mesh,
		   		return_internal_reference<1>() )
		.def( "collision_mesh", &Entity::collision_mesh,
		   		return_internal_reference<1>() )
		.def( "network_view", &Entity::network_view,
		   		return_internal_reference<1>() )
		.def( "get_component", &Entity::get_component,
		   		return_internal_reference<1>() )

		.def( "has_component", &Entity::has_component )
		.def( "get_components", &wrap_get_components )
		.def( "add_component", &Entity::add_component )
		;

	wrap_system();
	wrap_renderer();
	wrap_event();
	wrap_roam();
	wrap_rocket();

	wrap_world();
}

size_t Entity::current_identifier = 0;
Entity::Entity(): identifier( current_identifier++ )
{}

Transform& Entity::transform() {
	return static_cast<Transform&>(
		get_component( Component::Transform ) );
}

Camera& Entity::camera() {
	return static_cast<Camera&>(
		get_component( Component::Camera ) );
}

Mesh& Entity::mesh() {
	return static_cast<Mesh&>(
		get_component( Component::Mesh ) );
}

CollisionMesh& Entity::collision_mesh() {
	return static_cast<CollisionMesh&>(
		get_component( Component::CollisionMesh ) );
}

NetworkView& Entity::network_view() {
	return static_cast<NetworkView&>(
		get_component( Component::NetworkView ) );
}

bool Entity::has_component( Component::Type type ) {
	return storage.count( type );
}

Component& Entity::get_component( Component::Type type ) {
	return *storage.lower_bound( type )->second;
}

Entity::component_range Entity::get_components( Component::Type type ) {
	return storage.equal_range( type );
}

void Entity::add_component( Component::pointer_type component ) {
	storage.insert( std::make_pair( component->type, component ) );
}



