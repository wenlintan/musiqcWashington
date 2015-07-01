#include "resource.h"


map< string, boost::function< Resource* () > >		Resource::Factory;
map< string, weak_ptr<Resource> >					Resource::Loaded;

shared_ptr<Resource> Resource::load( const string& filename, shared_ptr<Renderer> rend )
{
	if( Resource::Loaded.count( filename ) && !Resource::Loaded[ filename ].expired() )
		return shared_ptr<Resource>( Resource::Loaded[ filename ] );

	string::size_type size = filename.find_last_of( "." );
	string ext = filename.substr( size );

	if( Resource::Factory.count( ext ) )
	{
		shared_ptr<Resource> res( Resource::Factory[ ext ]() );
		if( res->BasicType == Resource::STATE &&
			!boost::shared_static_cast<State, Resource>(res)->initialize( filename ) )
		{
			LOG_ERR( "Failed to load state: " + filename );
			return shared_ptr<Resource>();
		}
		else if( res->BasicType == Resource::DRAWN &&
				 !boost::shared_static_cast<Drawn, Resource>(res)->initialize( filename, rend ) )
		{
			LOG_ERR( "Failed to load drawable resource: " + filename );
			return shared_ptr<Resource>();
		}
		else
		{
			LOG_WARN( "Resource could not be initialized." );
		}

		Resource::Loaded[ filename ] = weak_ptr<Resource>(res);
		return res;
	}

	LOG_ERR( "Failed to load resource: " + filename );
	return shared_ptr<Resource>();
}

		
		