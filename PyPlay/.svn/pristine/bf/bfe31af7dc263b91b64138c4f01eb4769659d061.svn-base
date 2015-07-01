
#include <boost/smart_ptr/shared_ptr.hpp>
#pragma once

void wrap_component();

struct Component {
	typedef boost::shared_ptr< Component > pointer_type;

	enum Type {
		Unknown, Transform, Camera, Program, Light, Texture, Color, Mesh, ROAM,
		Framebuffer, MeshRenderer, CollisionMesh, Physics, NetworkView,
		GUIWindow,
		FirstUserComponent = 100, LastUserComponent = 1100
		};

	Type type;
	Component( Type type_ ): type( type_ )
	{}

	virtual ~Component() {}

	virtual std::string serialize( pointer_type prev_comp ) {
		return "";
	}

	virtual std::string deserialize( const std::string& data ) {
		return data;
	}
};

