
#include "objects.h"

Collision Plane::collide( const Ray& ray ) {
	Collision coll( ray );

	float to_plane_onto_n = ( ray.start - point ).dot_product( norm );
	float dir_onto_n = ray.dir.dot_product( norm );

	if( fabs(dir_onto_n) < G_EPSILON )	return coll.miss();

	float t = -to_plane_onto_n / dir_onto_n;
	if( t < 0 )							return coll.miss();

	return coll.collide( t );
}

Collision Sphere::collide( const Ray& ray ) {
	Collision coll( ray );

	Vector3f to_sphere = ray.start - center;
	float b = to_sphere.dot_product( ray.dir );

	//final expression for t implies that if b is positive
	//then t will never be positive
	if( b > 0.0 )			return coll.miss();

	float c = to_sphere.length_sq() - radius_sq;
	float det = b*b - c;

	if( det < 0.0 )			return coll.miss();

	float t = -b - sqrt( det );
	if( t < 0.0 )			return coll.miss();

	return coll.collide( t );
}
