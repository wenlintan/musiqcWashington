
#include <boost/python.hpp>
#include <boost/assign/list_of.hpp>

#include "collision.hpp"

using namespace boost::python;

void wrap_collision() {
	class_< CollAABB >( "CollAABB", init< const Vector3f&, const Vector3f& >() )
		.def_readwrite( "min", &CollAABB::min )
		.def_readwrite( "max", &CollAABB::max )
		;

	class_< CollOBB >( "CollOBB", 
		init< const Vector3f&, const Vector3f&, const Vector3f&,
			const Vector3f& >() )
		.def_readwrite( "pos", &CollOBB::pos )
		.def_readwrite( "dim", &CollOBB::dim )
		.def_readwrite( "up", &CollOBB::up )
		.def_readwrite( "right", &CollOBB::right )
		;

	class_< CollState >( "CollState", init<const Vector3f&>() )
		.def_readwrite( "translation", &CollState::translation )
		;

	class_< Collision >( "Collision" )
		.def_readwrite( "collided", &Collision::collided )
		.def_readwrite( "in_contact", &Collision::in_contact )
		.def_readwrite( "approx_time", &Collision::approx_time )
		.def_readwrite( "offset", &Collision::offset )
		.def_readwrite( "normal", &Collision::normal )
		;

	class_< CollGeometry >( "CollGeometry" )
		.def( "add_geometry", &CollGeometry::add_geometry )
		.def( "collide", &CollGeometry::collide )
		.def( "state", &CollGeometry::state,
			return_internal_reference<1>()	)
		;
}

void CollGeometry::add_geometry( CollAABB coll ) {
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

CollGeometry& CollGeometry::state( const CollState& s ) {
	current_state = s;
	return *this;
}

#include <iostream>
struct CollideVisitor:
	public boost::static_visitor< Collision > {

	const CollState &lstate, &rstate;
	CollideVisitor( const CollState& l, const CollState& r ): 
		lstate( l ), rstate( r )
	{}

	Collision operator()( const CollAABB& l, const CollAABB& r ) const {
		Vector3f lmin = l.min + lstate.translation, 
			lmax = l.max + lstate.translation;
		Vector3f rmin = r.min + rstate.translation, 
			rmax = r.max + rstate.translation;

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

Collision CollGeometry::collide( const CollGeometry& other ) {
	CollideVisitor cv( current_state, other.current_state );
	return boost::apply_visitor( cv, data, other.data );
}


