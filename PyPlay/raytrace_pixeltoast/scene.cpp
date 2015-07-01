
#include "scene.h"

bool Scene::collided( const Vector3f& start, const Vector3f& end ) const {
	float l = (start-end).length_sq();
	Ray ray( start, end-start );

	size_t s = objects.size();
	for( size_t i = 0; i < s; i++ ) {
		Collision new_coll = objects[i]->collide( ray );

		float t = new_coll.impact_param();
		if( new_coll && t*t < l )
			return true;
	}

	return false;
}

Collision Scene::collide( const Ray& ray ) const {
	
	Collision result( ray );
	result.miss();

	size_t s = objects.size();
	for( size_t i = 0; i < s; i++ ) {
		Collision new_coll = objects[i]->collide( ray );
		if( new_coll && ( !result || new_coll < result ) )
			result.collide( new_coll.impact_param() );
	}

	return result;	
};
