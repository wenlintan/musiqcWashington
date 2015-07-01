
#ifndef COLLISION__H
#define COLLISION__H

#include "math.h"

class Ray {
public:
	Vector3f	start, dir;

	Ray( const Vector3f& pos, const Vector3f& d ): start( pos ), dir( d.normalize() )	{}
	Vector3f at( float t ) const 	 {	return start + dir*t;	}
};

class Collision {
private:
	const Ray&	ray;
	float		t;

	bool		collided;

public:
	Collision( const Ray& r ): ray( r )		{}
	Collision( const Collision& c ): t( c.t ), collided( c.collided )		{}

	Collision& collide( float t )			{ this->t = t; collided = true; return *this; }
	Collision& miss()				{ collided = false; return *this; }

	Vector3f impact() const				{ if( *this ) return ray.at( t ); return Vector3f(); }
	float impact_param() const			{ if( *this ) return t; return -1.0f; }
	operator bool()	const				{ return collided; }

	friend bool operator <( const Collision& one, const Collision& two );
};
bool operator <( const Collision& one, const Collision& two );


#endif
