
#include <boost/python.hpp>
#include "component.hpp"

using namespace boost::python;
struct ComponentWrap: Component, wrapper<Component> {
	typedef boost::shared_ptr<ComponentWrap> pointer_type;

	ComponentWrap( Component::Type t ): 
		Component( t )
	{}

	std::string serialize( pointer_type ptr ) {
		//return call_method<std::string>( self, "serialize", ptr );
		return "";
	}

	std::string deserialize( const std::string& s ) {
		//return call_method<std::string>( self, "deserialize", s );
		return "";
	}

	//PyObject* self;
};

void wrap_component() {
	enum_< Component::Type >( "ComponentType" )
		.value( "Unknown", Component::Unknown )
		.value( "Transform", Component::Transform )
		.value( "Camera", Component::Camera )
		.value( "Program", Component::Program )
		.value( "Light", Component::Light )
		.value( "Mesh", Component::Mesh )
		.value( "MeshRenderer", Component::MeshRenderer )
		.value( "CollisionMesh", Component::CollisionMesh )
		.value( "Physics", Component::Physics )
		.value( "NetworkView", Component::NetworkView )
		.value( "FirstUserComponent", Component::FirstUserComponent )
		.value( "LastUserComponent", Component::LastUserComponent )
		;

	class_<ComponentWrap, ComponentWrap::pointer_type, 
			boost::noncopyable >( "Component",
			init< Component::Type >()	)
		.def_readwrite( "type", &Component::type )
		.def( "serialize", pure_virtual(&ComponentWrap::serialize) )
		.def( "deserialize", pure_virtual(&ComponentWrap::deserialize) )
		;
}


