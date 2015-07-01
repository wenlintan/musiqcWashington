
#include "vector.hpp"
#include "component.hpp"
#include "system.hpp"


struct Physics: public Component {
	typedef boost::shared_ptr< Physics > pointer_type;
	Physics(): Component( Component::Physics )
	{}

	float mass, u_friction;
	Vector3f velocity, acceleration, rotation, inertia;
};


class PhysicsSystem: public System {
public:
	typedef boost::shared_ptr< PhysicsSystem > pointer_type;
	const static float delta_time;

	void update( Entity::pointer_type ent );
};


