
#include <vector>
#include <boost/variant.hpp>

#include "vector.hpp"
#include "component.hpp"

void wrap_collision();
struct CollAABB {
	CollAABB() {}
	CollAABB( const Vector3f& pos_, const Vector3f& dim_ ):
		pos( pos_ ), dim( dim_ )
	{}

	Vector3f 	pos, dim;
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

struct Collision {
	bool 			collided, in_contact;
	unsigned short 	approx_time;
	Vector3f		offset, normal;

	Collision( bool coll = false ): collided( coll )
	{}

	operator bool() 		{ return collided; }
};

struct CollisionMesh: Component {
	typedef boost::shared_ptr<CollisionMesh> pointer_type;

	bool		geometry;
	CollData	data;

public:
	CollisionMesh(): Component( Component::CollisionMesh ), geometry( false ) 
	{}

	void add_geometry( CollAABB coll );

	Collision collide( const CollisionMesh& other );
	Collision collide_ray( const Vector3f& pos, const Vector3f& dir );

};


