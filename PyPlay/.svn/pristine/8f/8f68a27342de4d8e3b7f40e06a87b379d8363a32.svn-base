
#include <boost/python.hpp>
#include "system.hpp"

using namespace boost::python;
struct SystemWrap: System, wrapper<System> {
	typedef boost::shared_ptr<SystemWrap> pointer_type;

	void begin() {
		if( override f = this->get_override("begin") ) {
			f();
			return;
		}
		System::begin();
	}

	void default_begin() 	{ this->System::begin(); }

	void update( Entity::pointer_type ent ) {
		if( override f = this->get_override("update") ) {
			f( ent );
			return;
		}
		System::update( ent );
	}

	void default_update( Entity::pointer_type ent )	{ 
		this->System::update( ent );
	}

	void end() {
		if( override f = this->get_override("end") ) {
			f();
			return;
		}
		System::end();
	}

	void default_end() {
		this->System::end();
	}
};

void wrap_system() {
	class_<SystemWrap, SystemWrap::pointer_type, 
		boost::noncopyable >( "System" )
		.def( "begin", &System::begin, &SystemWrap::default_begin )
		.def( "update", &System::update, &SystemWrap::default_update )
		.def( "end", &System::end, &SystemWrap::default_end )
		;
}

