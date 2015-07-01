
#include "physics.hpp"

#include <boost/python.hpp>

using namespace boost::python;
void export_physics() {
	class_< Physics, Physics::pointer_type, bases<Component>,
		boost::noncopyable >( "Physics" )
		.def_readwrite( "mass", &Physics::mass )
		.def_readwrite( "u_friction", &Physics::u_friction )
		.def_readwrite( "velocity", &Physics::velocity )
		.def_readwrite( "acceleration", &Physics::acceleration )
		.def_readwrite( "rotation", &Physics::rotation )
		.def_readwrite( "inertia", &Physics::inertia )
		;

	class_< PhysicsSystem, PhysicsSystem::pointer_type,
		bases<System>, boost::noncopyable >( "PhysicsSystem" )
		;
	
}

const float PhysicsSystem::delta_time = 0.03f;
void PhysicsSystem::update( Entity::pointer_type ent ) {
	if( !ent->has_component( Component::Physics ) ) return;

	Transform& trans = ent->transform();
	Physics& phys = static_cast<Physics&>(
		ent->get_component( Component::Physics ) );
	
	trans.position += ( phys.velocity * delta_time );
	phys.velocity += phys.acceleration * delta_time / phys.mass;
	phys.acceleration = Vector3f();
}

