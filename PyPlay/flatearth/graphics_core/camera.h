#ifndef CAMERA__H
#define CAMERA__H

#include "stdafx.h"
#include "resource.h"

class Frustum
{
public:
	//order: left, right, up, down, near, far
	Plane		ClipPlanes[6];

	Vector3f	CameraPosition;
	Vector3f	LookVector;

};

class Ortho: public State
{
	friend class Renderer;
	friend class SDLRenderer;
	friend class GLRenderer;

public:

	Ortho(): State(Resource::ORTHO)	{}
	Ortho(uint w, uint h, float nearz, float farz):
							State(Resource::ORTHO),
							_Width(w), _Height(h),
							_NearZ(nearz), _FarZ(farz)
	{}

	void set( uint w, uint h, float nearz, float farz )
	{
		_Width = w;		_Height = h;
		_NearZ = nearz;	_FarZ = farz;
	}

private:
	uint	_Width, _Height;
	float	_NearZ, _FarZ;
};
	

class Camera: public State
{
	friend class Renderer;
	friend class SDLRenderer;
	friend class GLRenderer;

public:
	Camera(): State(Resource::CAMERA), _FOV(0) {}
	Camera(const Vector2d& dim, const Vector3f& pos, const Vector3f& look, 
		const Vector3f& up, float FOV, float nearz, float farz): 
														State(Resource::CAMERA),
														_FOV(FOV), _NearZ(nearz),
														_FarZ(farz), _Width(dim.x),
														_Height(dim.y) 
	{
		//make sure everything is normalized
		_Position = pos;
		_Look = (look-pos).normalize() + pos;
		_Up = up.normalize();
	}
	~Camera()	{}

	void set(const Vector2d& dim, const Vector3f& pos, const Vector3f& look, 
		const Vector3f& up, float FOV, float nearz, float farz)
	{
		_Position = pos;
		_Look = (look-pos).normalize() + pos;
		_Up = up.normalize();

		_FOV = FOV;
		_NearZ = nearz;
		_FarZ = farz;

		_Width = dim.x;
		_Height = dim.y;
	}

	void set( const Vector3f& pos, const Vector3f& look, const Vector3f& up ) {
		_Position = pos;
		_Look = (look-pos).normalize() + pos;
		_Up = up.normalize();
	}

	shared_ptr<Frustum> build_frustum();			//builds the six planes representing viewing frustum
	shared_ptr<Frustum> get_frustum_boundaries();	//returns lines along frustum boundaries

	Vector3f	project_screen_coordinates(int x, int y);

	//all camera transformation are not actually in world space x,y, and z
	//they operate in camera space x=_Right, y=_Up, z=(_Look-_Position)

	//manipulate camera position and orientation
	void translate(Vector3f trans);
	void translateX(float dist);
	void translateY(float dist);
	void translateZ(float dist);

	void rotate(Vector3f comps);
	void rotateX(float theta);
	void rotateY(float theta);
	void rotateZ(float theta);

private:

	void rotate(float theta, Vector3f axis);

	Vector3f		_Position;
	Vector3f		_Look;
	Vector3f		_Up;

	float			_FOV;
	float			_NearZ;
	float			_FarZ;

	uint			_Width;
	uint			_Height;

	
};

#endif