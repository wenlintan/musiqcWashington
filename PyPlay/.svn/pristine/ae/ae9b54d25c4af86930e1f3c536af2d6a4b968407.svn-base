
#include <vector>

#include <boost/variant.hpp>

#include "vector.hpp"

void wrap_collision();
struct CollAABB {
	CollAABB() {}
	CollAABB( const Vector3f& min_, const Vector3f& max_ ):
		min( min_ ), max( max_ )
	{}

	Vector3f 	min, max;
};

struct CollOBB {
	CollOBB() {}
	CollOBB( const Vector3f& pos_, const Vector3f& dim_,
		const Vector3f& up_, const Vector3f& right_ ):
		pos( pos_ ), dim( dim_ ), up( up_ ), right( right_ )
	{}

	Vector3f 	pos, dim, up, right;
};

struct CollTri {
	Vector3f	pt, u, v;
};

struct CollCompound;
typedef boost::variant< CollAABB, CollOBB, CollTri,
	boost::recursive_wrapper<CollCompound> >	CollData;

struct CollCompound {
	CollCompound() {}

	template< typename T >
	CollCompound( T begin, T end ): geometry( begin, end )
	{}

	std::vector< CollData >		geometry;
};

struct CollState {
	CollState() {}
	CollState( const Vector3f& t ): translation( t )
	{}

	Vector3f	translation;
};

struct Collision {
	bool 			collided, in_contact;
	unsigned short 	approx_time;
	Vector3f		offset, normal;

	Collision( bool coll = false ): collided( coll )
	{}

	operator bool() 		{ return collided; }
};

class CollGeometry {
	bool		geometry;
	CollData	data;
	CollState	current_state;

public:
	CollGeometry(): geometry( false ) 
	{}

	void add_geometry( CollAABB coll );

	CollGeometry& state( const CollState& s );
	Collision collide( const CollGeometry& other );
};


