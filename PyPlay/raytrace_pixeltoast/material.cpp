
#include "material.h"
#include "scene.h"

float PointLight::get_shade( const Scene& s, const Vector3f& point ) {
	if( s.collided( pos, point ) )
		return 0.0f;

	return 1.0f;
}

float ParametrizedLight2D::get_shade( const Scene& s, const Vector3f& point ) {

}


