
#pragma once

#include "system.hpp"
#include "renderer.hpp"

void wrap_rocket();

struct RocketDocumentInternals;
namespace Rocket{ namespace Core { class Element; } }

struct RocketDocument: public Component {
	typedef boost::shared_ptr<RocketDocument> pointer_type;

	RocketDocument( const std::string& fname );
	Rocket::Core::Element* get_element_by_id( const std::string& id );
	bool contains_point( const Vector2f& pt );

	RocketDocumentInternals* internals;
	std::string		filename;
};

struct RocketSystemInternals;
class RocketSystem: public System {
	RocketSystemInternals* internals;

public:
	static RocketSystemInternals* context;
	typedef boost::shared_ptr<RocketSystem> pointer_type;

	RocketSystem();
	~RocketSystem();

	void load_font( const std::string& name );
	Rocket::Core::Element* get_root_element();

	void update( Entity::pointer_type ent );
	void end();

	bool handle_keyboard( int code, bool down );
	bool handle_mouse_move( int x, int y, int dx, int dy );
	bool handle_mouse_click( int button, int x, int y, bool down );
};


