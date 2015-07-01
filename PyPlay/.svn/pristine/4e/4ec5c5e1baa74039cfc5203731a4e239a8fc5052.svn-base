
#ifndef SHADER__H
#define SHADER__H

#include "stdafx.h"
#include "resource.h"

class Shader: public State {
public:
	Shader():	State( Resource::SHADER )
	{}

	Shader( const string& filename ) {
		if( !initialize( filename ) )
			throw g5Exception("Shader", "Could not open shader", true);
	}

	~Shader() {
		shutdown();
	}

	bool initialize( const string& filename );
	void shutdown();

	string	Source;

};


struct ShaderVariable {
	enum VariableType { INT, INT_ARRAY, FLOAT, FLOAT_ARRAY, VECTOR3F, VECTOR3F_ARRAY, MATRIX44, MATRIX44_ARRAY };
	enum VariableModifier{ GLOBAL, PER_VERTEX, VARYING };

	template< typename ValueType >
	ShaderVariable( VariableModifier mod, VariableType t, const string& name, ValueType data ):
			Modifier( mod ), Type( t ), Name( name ), Data( data )
	{}

	VariableModifier	Modifier;
	VariableType		Type;
	string				Name;
	boost::any			Data;
};

class Program: public State {
public:
	Program():	State( Resource::PROGRAM )
	{}

	Program( shared_ptr<Shader> vert, shared_ptr<Shader> frag ):	State( Resource::PROGRAM )
	{
		if( !initialize( vert, frag ) )
			throw g5Exception("Program", "Could not build shader program", true);
	}

	bool initialize( shared_ptr<Shader> vert, shared_ptr<Shader> frag );
	void shutdown();

	shared_ptr<Shader>		Vertex, Frag;
};

#endif