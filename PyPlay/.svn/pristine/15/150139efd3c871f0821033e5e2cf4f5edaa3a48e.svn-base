
#ifndef RENDERER__H
#define RENDERER__H

#include "scene.h"
class PixelToaster::Display;
class PixelToaster::Pixel;

class Renderer {
private:
	Vector3f pos, look, right, up;

	Vector2d screen_size;
	float distortion, fov, tan_fov;

	PixelToaster::Display display;
	vector<PixelToaster::Pixel> pixels;

	Vector3f render_ray( const Scene& scene, float dx, float dy );

public:
	Renderer( const Vector2d& screen_dim, float field_of_view );

	void place_camera( const Vector3f& pos, const Vector3f& look, const Vector3f& up );
	void render( const Scene& scene );

};

#endif


