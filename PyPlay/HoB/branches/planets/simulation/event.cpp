
#include <boost/python.hpp>

#include <sdl.h>

#include "event.hpp"

using namespace boost::python;
class EventSystemWrapper: public EventSystem, public wrapper<EventSystem> {
public:
	typedef boost::shared_ptr<EventSystemWrapper> pointer_type;

	void begin() {
		if( override f = this->get_override("begin") ) {
			f();
			return;
		}
		EventSystem::begin();
	}

	void default_begin() 	{ this->EventSystem::begin(); }

	void update( Entity::pointer_type ent ) {
		if( override f = this->get_override("update") ) {
			f( ent );
			return;
		}
		EventSystem::update( ent );
	}

	void default_update( Entity::pointer_type ent )	{ 
		this->EventSystem::update( ent );
	}

	bool handle_quit() {
		return this->get_override("handle_quit")();
	}

	bool handle_keyboard( int code, bool down ) {
		return this->get_override("handle_keyboard")( code, down );
	}

	bool handle_mouse_move( int x, int y, int dx, int dy ) {
		return this->get_override("handle_mouse_move")( x, y, dx, dy );
	}

	bool handle_mouse_click( int button, int x, int y, bool down ) {
		return this->get_override("handle_mouse_click")( button, x, y, down );
	}
};

void wrap_event() {
	enum_< SDL_Scancode >( "Scancode" )
		.value( "KI_BACKSPACE", SDL_SCANCODE_BACKSPACE )
		.value( "KI_TAB", SDL_SCANCODE_TAB )
		.value( "KI_CLEAR", SDL_SCANCODE_CLEAR )
		.value( "KI_RETURN", SDL_SCANCODE_RETURN )
		.value( "KI_PAUSE", SDL_SCANCODE_PAUSE )
		.value( "KI_ESCAPE", SDL_SCANCODE_ESCAPE )
		.value( "KI_SPACE", SDL_SCANCODE_SPACE )
		.value( "KI_OEM_7", SDL_SCANCODE_APOSTROPHE )
		.value( "KI_OEM_PLUS", SDL_SCANCODE_EQUALS )
		.value( "KI_OEM_COMMA", SDL_SCANCODE_COMMA )
		.value( "KI_OEM_MINUS", SDL_SCANCODE_MINUS )
		.value( "KI_OEM_PERIOD", SDL_SCANCODE_PERIOD )
		.value( "KI_OEM_2", SDL_SCANCODE_SLASH )
		.value( "KI_OEM_1", SDL_SCANCODE_SEMICOLON )
		.value( "KI_OEM_4", SDL_SCANCODE_LEFTBRACKET )
		.value( "KI_OEM_5", SDL_SCANCODE_BACKSLASH )
		.value( "KI_OEM_6", SDL_SCANCODE_RIGHTBRACKET )
		.value( "KI_OEM_3", SDL_SCANCODE_GRAVE )

		.value( "KI_0", SDL_SCANCODE_0 )
		.value( "KI_1", SDL_SCANCODE_1 )
		.value( "KI_2", SDL_SCANCODE_2 )
		.value( "KI_3", SDL_SCANCODE_3 )
		.value( "KI_4", SDL_SCANCODE_4 )
		.value( "KI_5", SDL_SCANCODE_5 )
		.value( "KI_6", SDL_SCANCODE_6 )
		.value( "KI_7", SDL_SCANCODE_7 )
		.value( "KI_8", SDL_SCANCODE_8 )
		.value( "KI_9", SDL_SCANCODE_9 )

		.value( "KI_A", SDL_SCANCODE_A )
		.value( "KI_B", SDL_SCANCODE_B )
		.value( "KI_C", SDL_SCANCODE_C )
		.value( "KI_D", SDL_SCANCODE_D )
		.value( "KI_E", SDL_SCANCODE_E )
		.value( "KI_F", SDL_SCANCODE_F )
		.value( "KI_G", SDL_SCANCODE_G )
		.value( "KI_H", SDL_SCANCODE_H )
		.value( "KI_I", SDL_SCANCODE_I )
		.value( "KI_J", SDL_SCANCODE_J )
		.value( "KI_K", SDL_SCANCODE_K )
		.value( "KI_L", SDL_SCANCODE_L )
		.value( "KI_M", SDL_SCANCODE_M )
		.value( "KI_N", SDL_SCANCODE_N )
		.value( "KI_O", SDL_SCANCODE_O )
		.value( "KI_P", SDL_SCANCODE_P )
		.value( "KI_Q", SDL_SCANCODE_Q )
		.value( "KI_R", SDL_SCANCODE_R )
		.value( "KI_S", SDL_SCANCODE_S )
		.value( "KI_T", SDL_SCANCODE_T )
		.value( "KI_U", SDL_SCANCODE_U )
		.value( "KI_V", SDL_SCANCODE_V )
		.value( "KI_W", SDL_SCANCODE_W )
		.value( "KI_X", SDL_SCANCODE_X )
		.value( "KI_Y", SDL_SCANCODE_Y )
		.value( "KI_Z", SDL_SCANCODE_Z )
		;

	class_< EventSystemWrapper, EventSystemWrapper::pointer_type,
		boost::noncopyable, bases<System> >( "EventSystem" )
		.def( "begin", &EventSystem::begin,
			&EventSystemWrapper::default_begin )
		.def( "update", &EventSystem::update,
			&EventSystemWrapper::default_update )

		.def( "set_mouse_pos", &EventSystem::set_mouse_pos )

		.def( "handle_quit", pure_virtual(&EventSystem::handle_quit) )
		.def( "handle_keyboard", 
			pure_virtual(&EventSystem::handle_keyboard) )
		.def( "handle_mouse_move", 
			pure_virtual(&EventSystem::handle_mouse_move) )
		.def( "handle_mouse_click",
			pure_virtual(&EventSystem::handle_mouse_click) )
		;
}

void EventSystem::begin() {
	SDL_Event event;
	while( SDL_PollEvent(&event) ) {
		switch( event.type ) {
		case SDL_QUIT:
			handle_quit();
			break;
		case SDL_KEYDOWN:
			handle_keyboard( event.key.keysym.scancode, true );
			break;
		case SDL_KEYUP:
			handle_keyboard( event.key.keysym.scancode, false ); 
			break;
		case SDL_MOUSEMOTION:
			handle_mouse_move( event.motion.x, event.motion.y,
				event.motion.xrel, event.motion.yrel );
			break;
		case SDL_MOUSEBUTTONDOWN:
			handle_mouse_click( event.button.button, 
				event.button.x, event.button.y, true );
			break;
		case SDL_MOUSEBUTTONUP:
			handle_mouse_click( event.button.button, 
				event.button.x, event.button.y, false );
			break;
		default:
			break;
		}
	}
}

void EventSystem::set_mouse_pos( int x, int y ) {
	// NULL Window means currently focused
	SDL_WarpMouseInWindow( 0, x, y );
}

