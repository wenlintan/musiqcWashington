
#ifndef SCENE__H
#define SCENE__H

#include "collision.h"
#include "objects.h"

#include <vector>
#include <boost/shared_ptr.hpp>

class Scene {
private:
	std::vector< boost::shared_ptr< Object > >	objects;

public:
	
	void add_object( const boost::shared_ptr<Object>& obj ) {
		objects.push_back( obj );
	}


	bool collided( const Vector3f& start, const Vector3f& end ) const;
	Collision collide( const Ray& ray ) const;

};


#endif
