#ifndef GEOMETRY__H
#define GEOMETRY__H

#include "stdafx.h"
#include "resource.h"
#include "renderer.h"

struct Collision {
public:
	bool		collision;
	float		t;
	size_t		index;

	Vector3f	normal;
	Ray<float>	colliding_ray, hit_ray;

	Collision(): collision(false), t(-1)
	{}

	operator bool() {
		return collision;
	}
};

class Geometry: public Drawn {
public:
	vector<Vertex>		Vertices;
	vector<ushort>		Indices;
	int					Enabled;

	Vector3f			Translation, Rotation;
	Vector3f			Velocity, Acceleration;

	Geometry(): Drawn(Resource::MODEL), Enabled(true)
	{}

	virtual ~Geometry()
	{}

	bool initialize( const string& filename, shared_ptr<Renderer> rend );
	void set_renderer( shared_ptr<Renderer> rend );

	void create_plane( Vector3f& p1, Vector3f& p2, Vector3f& p3, Vector3f& p4 );
	void create_cube( float w, float l, float d );
	void create_tetrahedra( float h );
	void create_cone( float radius, float h, uint tesselation );

	bool load_model( const string& filename );

	void generate_normals();
	vector<float> build_collision_data( ushort resolution, ushort max_collision_per_step = 2 );

	void draw();

	virtual Collision collide( const Geometry& other ) const;
	virtual Collision collide( const Ray<float>& ray ) const;
	virtual Collision collide( const Vector3f& point ) const;

private:
	shared_ptr<Renderer>	_Renderer;
	
};

#endif
