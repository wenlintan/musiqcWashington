
#include "trigger.h"
#include "py_boost_function.hpp"

void export_trigger() {
	using namespace boost::python;
	def_function< Trigger::arg_type( Trigger::arg_type ) >( "Trigger_t", "Callback type used with triggers." );

	class_<Trigger>( "Trigger" )
		.def( "add_trigger", &Trigger::add_trigger, with_custodian_and_ward<1,2>() )
	;
}

Trigger::arg_type Trigger::invoke( Trigger::arg_type arg ) {
	if( running ) return arg_type();
	running = true;

	arg_type result = arg, new_result;
	try {
		for( size_t i = 0; i < callbacks.size(); ++i ) {
			new_result = callbacks[i].second( result );

			if( new_result->type == result->type )	result = new_result;
			else if( !new_result )					return new_result;									
		}

		result->trigger();
	} catch( boost::python::error_already_set const& ) {
		PyErr_Print();
	}

	running = false;
	return result;
}

bool Trigger::callback_compare( const pair<int,cb_type>& one, const pair<int,cb_type>& two ) {
	return one.first < two.first;
}
