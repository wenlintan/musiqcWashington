#ifndef RESOURCE__H
#define RESOURCE__H

#include "stdafx.h"

class Renderer;
class Resource;

template< typename T >
Resource* make_type()
{
	return (Resource*)new T();
}

class Resource
{
public:

	enum BaseType { BASEGENERIC = 0, STATE, DRAWN };

	enum Type { GENERIC = 0, TEXTURE = 1, FLAT_COLOR, DATA_TEXTURE, MULTI_TEXTURE, CULLING, LIGHT, SHADER, PROGRAM, RENDER_TARGET, 
				MODEL, HEIGHTMAP, CAMERA, ORTHO };

	static map< string, boost::function< Resource* () > >		Factory;
	static map< string, weak_ptr<Resource> >					Loaded;

	static shared_ptr<Resource> load( const string& filename, shared_ptr<Renderer> rend );
	template< typename T > static void register_type( const string& ext )
	{
		Resource::Factory[ ext ] = boost::function< Resource* () >( &make_type<T> );
	}

	BaseType	BasicType;
	Type		SpecType;

	Resource(BaseType base = BASEGENERIC, Type type = GENERIC):		BasicType( base ), SpecType( type )
	{}

	virtual ~Resource()
	{}
	
};

class State: public Resource
{
public:
	State(Type type = Resource::GENERIC):	Resource( Resource::STATE, type )
	{}

	virtual bool initialize( const string& filename )	{ return true; }
	virtual void shutdown()								{}

	shared_ptr<Resource>	RenderData;
};

class Drawn: public Resource
{
public:
	Drawn(Type type = Resource::GENERIC):	Resource( Resource::DRAWN, type )
	{}

	virtual bool initialize( const string& filename, shared_ptr<Renderer> rend )	{ return true; }
	virtual void shutdown()															{}

	virtual void draw() = 0;
};



#endif
