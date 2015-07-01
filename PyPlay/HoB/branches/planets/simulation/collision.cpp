
#include <boost/python.hpp>
#include <boost/assign/list_of.hpp>

#include "collision.hpp"

using namespace boost::python;
struct ListVisitor:
	public boost::static_visitor< > {

	list& l;
	ListVisitor( list& l_ ): l( l_ )
	{}

	template< typename T >
	void operator()( const T& t ) const {
		l.append( t );
	}

	void operator()( const CollCompound& compound ) const {
		list result;
		for( size_t i = 0; i < compound.geometry.size(); ++i ) 
			boost::apply_visitor( ListVisitor(result), compound.geometry[i] );
		l.append( result );
	}
};

static object wrap_get_geometry( CollisionMesh::pointer_type mesh ) {
	list result;
	boost::apply_visitor( ListVisitor(result), mesh->data );
	return result[0];
}

void wrap_collision() {
	class_< CollAABB >( "CollAABB", init< const Vector3f&, const Vector3f& >() )
		.def_readwrite( "pos", &CollAABB::pos )
		.def_readwrite( "dim", &CollAABB::dim )
		;

	class_< CollOBB >( "CollOBB", 
		init< const Vector3f&, const Vector3f&, const Vector3f&,
			const Vector3f& >() )
		.def_readwrite( "pos", &CollOBB::pos )
		.def_readwrite( "dim", &CollOBB::dim )
		.def_readwrite( "up", &CollOBB::up )
		.def_readwrite( "right", &CollOBB::right )
		;

	class_< Collision >( "Collision" )
		.def_readwrite( "collided", &Collision::collided )
		.def_readwrite( "in_contact", &Collision::in_contact )
		.def_readwrite( "approx_time", &Collision::approx_time )
		.def_readwrite( "offset", &Collision::offset )
		.def_readwrite( "normal", &Collision::normal )
		;

	class_< CollisionMesh, bases<Component>,
	   	CollisionMesh::pointer_type, boost::noncopyable	>( "CollisionMesh" )
		.def( "add_geometry", &CollisionMesh::add_geometry )
		.def( "get_geometry", &wrap_get_geometry )
		.def( "collide", &CollisionMesh::collide )
		;
}

void CollisionMesh::add_geometry( CollAABB coll ) {
	if( CollCompound* comp = boost::get<CollCompound>( &data ) ) {
		comp->geometry.push_back( coll );
		return;
	} else if( !geometry ) {
		data = coll;
		geometry = true;
	} else {
		data = CollCompound( boost::assign::list_of( data )( coll ) );
	}
}

struct CollState {
	CollState() {}
	CollState( const Vector3f& t ): translation( t )
	{}

	Vector3f	translation;
};

#include <iostream>
struct CollideVisitor:
	public boost::static_visitor< Collision > {

	const CollState &lstate, &rstate;
	CollideVisitor( const CollState& l, const CollState& r ): 
		lstate( l ), rstate( r )
	{}

	Collision operator()( const CollAABB& l, const CollAABB& r ) const {
		Vector3f lmin = l.pos + lstate.translation, 
			lmax = l.pos + l.dim + lstate.translation;
		Vector3f rmin = r.pos + rstate.translation, 
			rmax = r.pos + r.dim + rstate.translation;

		Collision coll( true );
		float min_overlap = 1.e6;

		for( unsigned char i = 0; i < 3; ++i ) {
			if( lmax.d[i] < rmin.d[i] || lmin.d[i] > rmax.d[i] )
				return Collision();

			if( fabsf( lmin.d[i] - rmax.d[i] ) < min_overlap ) {
				min_overlap = fabsf( lmin.d[i] - rmax.d[i] );
				coll.normal = Vector3f(float(i==0), float(i==1), float(i==2));
			} 

			if( fabs( lmax.d[i] - rmin.d[i] ) < min_overlap ) {
				min_overlap = fabsf( lmax.d[i] - rmin.d[i] );
				coll.normal = Vector3f(
					-float(i==0), -float(i==1), -float(i==2) );
			}
		}

		coll.offset = coll.normal * min_overlap ;
		return coll;
	}

	template< typename T >
	Collision operator()( T t, const CollCompound& compound ) const {
		Collision coll;
		for( size_t i = 0; i < compound.geometry.size(); ++i ) {
			const CollData& d = compound.geometry[i];
			if( coll = boost::apply_visitor( *this, CollData( t ), d ) )
				return coll;
		}

		return Collision();
	}

	template< typename T, typename U >
 	Collision operator() ( T t, U u ) const {
		return boost::apply_visitor( CollideVisitor( rstate, lstate ), 
			CollData( u ), CollData( t ) );
	}
};

struct RayCollideVisitor:
	public boost::static_visitor<Collision> {

	const CollState& state;
	Vector3f pos, dir;

	RayCollideVisitor( CollState& state_,
		const Vector3f& pos_, const Vector3f& dir_	): 
		state( state_ ), pos( pos_ ), dir( dir_ )
	{}

	Collision operator()( const CollAABB& coll ) const {
		Vector3f min = coll.pos + state.translation,
			max = coll.pos + coll.dim + state.translation;
		Vector3f off = min - pos;

		for( size_t i = 0; i < 3; ++i ) {
			if( fabs( dir.d[i] ) < 1.e-10 ) continue;
			float t = off.d[i] / dir.d[i];
			Vector3f pt = pos + dir*t;

			for( size_t j = (i+1)%3; j != i; j=(j+1)%3 ) {
				float v = pt.d[j] - min.d[j];
				if( v < 0. || v > max.d[i] - min.d[i] )
					continue;

				Collision coll( true );
			}


		}

		return Collision();
	}

	template< typename T >
	Collision operator()( const T& t ) {
		return Collision();
	}
};

Collision CollisionMesh::collide( const CollisionMesh& other ) {
	//TODO: Use Transform from entity in proper system to get state
	//CollideVisitor cv( current_state, other.current_state );
	//return boost::apply_visitor( cv, data, other.data );
	return Collision();
}


Collision CollisionMesh::collide_ray( 
	const Vector3f& pos, const Vector3f& dir ) {
	//RayCollideVisitor cv( current_state, pos, dir );
	//return boost::apply_visitor( cv, data );
	return Collision();
}

