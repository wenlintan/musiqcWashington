#ifndef SCRIPTS__H
#define SCRIPTS__H

#pragma once
#include "stdafx.h"

typedef boost::python::object py_object;
typedef boost::python::dict py_dict;
typedef boost::python::str py_str;

class Character;

class ScriptController {
public:
	ScriptController();

	void load_module( const string& name, shared_ptr<Character> ch );
	void register_object( const py_object& obj );

private:
	vector< py_object >		modules;
};

#endif