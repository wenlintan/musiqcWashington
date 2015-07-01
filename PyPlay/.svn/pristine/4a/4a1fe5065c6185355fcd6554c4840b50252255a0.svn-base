
#include "objects.h"
#include "material.h"

#include "scene.h"
#include "renderer.h"

#include <boost/shared_ptr.hpp>

int main( int argc, char** argv ) {

	Scene s;

	MaterialModelData data = { Vector3f(), Vector3f(), Vector3f( 1.0f, 0.0f, 0.0f ), Vector3f( 1.0f, 1.0f, 1.0f ), 5, 0.0f };
	Material red_mat( data );

	s.add_object( boost::shared_ptr<Plane>( new Plane( Vector3f( 0.0f, -5.0f, 0.0f ), Vector3f( 0.0f, 1.0f, 0.0f ), red_mat ) ) );
	s.add_object( boost::shared_ptr<Plane>( new Plane( Vector3f( 0.0f, 5.0f, 0.0f ), Vector3f( 0.0f, -1.0f, 0.0f ), red_mat ) ) );
	s.add_object( boost::shared_ptr<Plane>( new Plane( Vector3f( -5.0f, 0.0f, 0.0f ), Vector3f( 1.0f, 0.0f, 0.0f ), red_mat ) ) );
	s.add_object( boost::shared_ptr<Plane>( new Plane( Vector3f( 5.0f, 0.0f, 0.0f ), Vector3f( -1.0f, 0.0f, 0.0f ), red_mat ) ) );
	s.add_object( boost::shared_ptr<Plane>( new Plane( Vector3f( 0.0f, 0.0f, -10.0f ), Vector3f( 0.0f, 0.0f, 1.0f ), red_mat ) ) );
	s.add_object( boost::shared_ptr<Plane>( new Plane( Vector3f( 0.0f, 0.0f, 10.0f ), Vector3f( 0.0f, 0.0f, -1.0f ), red_mat ) ) );

	Renderer r( Vector2d( 800, 600 ), 70.0f );
	r.render( s );

	return 0;
}



