
#include <boost/python.hpp>

#include "entity.hpp"

using namespace boost::python;
class EntityWrapper: public Entity, public wrapper<Entity> {
public:
	CollGeometry& collision_geometry() {
		return call<CollGeometry&>(
			this->get_override( "collision_geometry" ).ptr() );
	}

	void resolve( Entity& other, Collision& coll ) {
		this->get_override( "resolve" )( other, coll );
	}

	State& state() {
		return call<State&>( this->get_override( "state" ).ptr() );
	}
};

BOOST_PYTHON_MODULE( simulation ) {
	wrap_vector();
	wrap_collision();
	wrap_network();

	class_<EntityWrapper, std::auto_ptr<EntityWrapper>,
		boost::noncopyable>( "Entity", no_init ) 
		.def( "collision_geometry", 
				pure_virtual(&EntityWrapper::collision_geometry),
		   		return_internal_reference<1>() )
		.def( "resolve", pure_virtual(&EntityWrapper::resolve) )
		.def( "state", pure_virtual(&EntityWrapper::state),
		   		return_internal_reference<1>() )
		;

}

