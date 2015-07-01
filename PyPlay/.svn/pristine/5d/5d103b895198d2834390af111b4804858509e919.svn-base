
#pragma once

#include "system.hpp"

void wrap_event();

class EventSystem: public System {
public:
	typedef boost::shared_ptr<EventSystem> pointer_type;

	void begin();
	void update( Entity::pointer_type ent ) {}

	void set_mouse_pos( int x, int y );

	virtual bool handle_quit() { return false; }
	virtual bool handle_keyboard( int code, bool down ) { return false; }

	virtual bool handle_mouse_move( int x, int y, int dx, int dy ) {
		return false;
	}

	virtual bool handle_mouse_click( int button, int x, int y, bool down ) {
		return false;
	}
};

