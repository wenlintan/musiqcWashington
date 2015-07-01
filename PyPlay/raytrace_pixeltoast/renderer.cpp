
#include "renderer.h"

#include <cmath>
#include "collision.h"
#include "Toaster1.4/PixelToaster.h"

Renderer::Renderer( const Vector2d& screen_dim, float field_of_view ):
	screen_size( screen_dim ), distortion( (float)screen_dim.x / screen_dim.y ), 
	fov( field_of_view ), tan_fov( (float)tan( field_of_view * G_PI / 180.0 / 2.0 ) ),
	display( "Raytracer", screen_dim.x, screen_dim.y ), pixels( screen_dim.x*screen_dim.y )
{
	place_camera( Vector3f( ), Vector3f( 0.0f, 0.0, -1.0 ), Vector3f( 0.0, 1.0f, 0.0f ) );
}

void Renderer::place_camera( const Vector3f& pos, const Vector3f& look, const Vector3f& up ) {
	pos = pos; look = look; up = up;
	right = look.cross_product( up );
}

Vector3f Renderer::render_ray( const Scene& scene, float dx, float dy ) {

	Vector3f dir = look + right*dx*tan_fov + up*(-dy)*tan_fov;
	Ray r( pos, dir );

	Collision c = scene.collide( r );
	if( !c ) 	return Vector3f();

	return c.color();
}

void Renderer::render( const Scene& scene ) {
	float dxfactor = distortion / screen_dim.x, dyfactor = 1.0f / screen_dim.y;
	Vector2d hscr = screen_dim / 2;

	for( size_t y = 0; y < screen_dim.y; ++y ) {
		for( size_t x = 0; x < screen_dim.x; ++x ) {

			float dx = ( x - hsc.x ) * dxfactor, dy = ( y - hsc.y ) * dyfactor;
			Vector3f color = render_ray( scene, dx, dy );
			pixels[ y*screen_dim.x + x ] = FloatingPointPixel( color.r, color.g, color.b );
		}

		display.update( pixels );
	}
}

