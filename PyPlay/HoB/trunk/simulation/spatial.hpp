
#include <vector>


template< typename T >
class SpatialSubdivision {
public:
	virtual ~Spatial() {}

	virtual void add_entity( const T& ent ) = 0;
	virtual void remove_entity( const T& ent ) = 0;

	virtual const std::vector<T>& neighbors( 
		const T& ent, float range = 0. ) = 0;

};

template< typename T >
class FakeSpatialSubdivision {
	std::vector<T>	all_entities;

public:
	void add_entity( const T& ent ) {
		all_entities.push_back( ent );
	}
	
	void remove_entity( const T& ent ) {
		all_entities.remove( ent );
	}

	const std::vector<T>& neighbors(
		const T& ent, float range = 0. ) {
		return all_entities;
	}

};

