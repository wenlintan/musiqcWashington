
#ifndef OBJECTS__H
#define OBJECTS__H

#include "collision.h"
class Material;

class Object {
private:
	const Material& material;
public:
	Object( const Material& mat ): material( mat ) {}
	virtual ~Object() {}

	virtual Collision collide( const Ray& ray ) = 0;		//collide with given ray, return collision object
	virtual Vector3f normal( const Vector3f& point ) = 0;	//get normal at given point, canassume point is on object surface

	Vector3f color( const Scene& scene, const Collision& coll ) {
		return material.color( scene, *this, coll );
	}

};

class Plane: public Object {
private:
	Vector3f point, norm;

public:
	Plane( const Vector3f& p, const Vector3f& n, const Material& mat ): Object(mat), point( p ), norm( n ) {}

	virtual Collision collide( const Ray& ray );
	virtual Vector3f normal( const Vector3f& point )	{ return norm; }

};

class Sphere: public Object {
private:
	Vector3f center;
	float radius, radius_sq;

public:
	Sphere( const Vector3f& c, float r, const Material& mat ): Object( mat ), center( c ), radius( r ), radius_sq( r*r ) {}

	Collision collide( const Ray& ray );
	Vector3f normal( const Vector3f& point )	{ return (point - center) / radius; }

};

#endif
