
#ifndef MATERIAL__H
#define MATERIAL__H

#include "math.h"
class Scene;
class Object;

struct LightModelData {
	Vector3f 	diffuse, specular;
	float 		falloff, falloff_sq;
};

class Light {
private:
	float		falloff_dist, falloff_dist_sq;
	Vector3f	diffuse, specular;

public:
	Light( const LightModelData& data ):
		diffuse( data.diffuse ), specular( data.specular ), falloff_dist( data.falloff ), falloff_dist_sq( data.falloff_sq )
	{}

	virtual ~Light() 
	{}

	virtual float get_shade( const Scene& s, const Vector3f& point ) = 0;
};

class PointLight: public Light {
private:
	Vector3f 	pos;

public:
	PointLight( const LightModelData& data, const Vector3f& position ):
		Light( data ), pos( position )
	{}

	float get_shade( const Scene& s, const Vector3f& point );

};

class ParametrizedLight2D: public Light {
public:
	ParametrizedLight2D( const LightModelData& data ): Light( data )
	{}

	virtual ~ParametrizedLight2D()
	{}

	virtual void parametrize( float u, float v, Vector3f& pos, Vector3f& norm ) = 0;
	float get_shade( const Scene& s, const Vector3f& point );
};

class RectangleLight: public ParametrizedLight2D {
private:
	Vector3f pos, l, w, norm;

public:
	RectangleLight( const LightModelData& data, const Vector3f& position, const Vector3f& length, const Vector3f& width ):
		ParametrizedLight2D( data ), pos( position ), l( length ), w( width ), norm( length.cross_product( width ) )
	{}

	void parametrize( float u, float v, Vector3f& position, Vector3f& normal ) {
		position = pos + l*u + w*v;
		normal = norm;
	}

};

class CircularlLight: public ParametrizedLight2D {

};

class ParametrizedLight3D: public Light {
public:
	ParametrizedLight3D( const LightModelData& data ): Light( data )
	{}

	virtual ~ParametrizedLight3D()
	{}

	virtual void parametrize( float u, float v, float w, Vector3f& pos, Vector3f& norm ) = 0;
	float get_shade( const Scene& s, const Vector3f& point );
};

class SphericalLight: public ParametrizedLight3D {

};

struct MaterialModelData {
	Vector3f emissive, ambient, diffuse, specular;
	int shininess;
	float reflectivity;
};

class Material {
private:
	MaterialModelData data;

public:
	Material( const MaterialModelData& model_data ): data( model_data )
	{}

	Vector3f color( const Scene& scene, const Object& obj, const Collision& coll );

};

#endif
