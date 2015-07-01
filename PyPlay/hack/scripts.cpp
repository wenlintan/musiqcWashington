
#include "scripts.h"
#include <Python.h>

#include "map.h"

BOOST_PYTHON_MODULE(hack) {
	export_stdafx();

	export_action();
	export_trigger();

	export_character();
}

ScriptController::ScriptController() {
	Py_Initialize();
	inithack();
}

void ScriptController::load_module( const string& name, shared_ptr<Character> ch ) {
	try {
		py_object o = boost::python::import( py_str( name ) );
		py_dict d = py_dict( o.attr( "__dict__" ) );
		d[ "hack_init" ]( ch );

		modules.push_back( d );

	} catch( boost::python::error_already_set const& ) {
		PyErr_Print();
	};
}
