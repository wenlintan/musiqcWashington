#include "camera.h"

shared_ptr<Frustum> Camera::build_frustum()
{
	shared_ptr<Frustum> F( new Frustum() );
	F->CameraPosition = _Position;
	F->LookVector = _Look;

	//we need a point and a normal for each plane
	//we can get this from the FOV and camera vectors

	//set up look to be normalized in front of cam position
	Vector3f Look = _Look - _Position;
	Vector3f Up = _Up;

	float scaledtan = (float)tan((G_PI/180.0f) * (_FOV * 0.5f));
	Vector3f Right = Look.cross_product(_Up).normalize();

	Vector3f tempRight = (-Right) * scaledtan;
	F->ClipPlanes[0].point = tempRight + Look;
	F->ClipPlanes[0].normal = F->ClipPlanes[0].point.normalize();				//normal is now a normalized vector pointing down the plane
	F->ClipPlanes[0].normal = (F->ClipPlanes[0].normal.cross_product(Up));		//cross product with up gives normal of the plane
	F->ClipPlanes[0].point += _Position;		//set point
	//left clip plane built

	tempRight = Right * scaledtan;		//same thing with positive right
	F->ClipPlanes[1].point = tempRight + Look;
	F->ClipPlanes[1].normal = F->ClipPlanes[1].point.normalize();
	F->ClipPlanes[1].normal = -(F->ClipPlanes[1].normal.cross_product(Up));
	F->ClipPlanes[1].point += _Position;

	//now we need to build the up and down clip planes
	Vector3f tempUp = Up * scaledtan;
	F->ClipPlanes[2].point = tempUp + Look;
	F->ClipPlanes[2].normal = F->ClipPlanes[2].point.normalize();
	F->ClipPlanes[2].normal = (F->ClipPlanes[2].normal.cross_product(Right));
	F->ClipPlanes[2].point += _Position;

	//and down
	tempUp = (-Up) * scaledtan;
	F->ClipPlanes[3].point = tempUp + Look;
	F->ClipPlanes[3].normal = F->ClipPlanes[3].point.normalize();
	F->ClipPlanes[3].normal = -(F->ClipPlanes[3].normal.cross_product(Right));
	F->ClipPlanes[3].point += _Position;

	//now for the easy ones the near and far planes
	Vector3f normLook = Look.normalize();
	F->ClipPlanes[4].normal = normLook;
	F->ClipPlanes[4].point = _Position + (normLook * _NearZ);

	F->ClipPlanes[5].normal = -normLook;
	F->ClipPlanes[5].point = _Position + (normLook * _FarZ);

	return F;
}

shared_ptr<Frustum> Camera::get_frustum_boundaries()
{
	//normal in Frustum planes is really vector on plane not normal
	//of the plane
	//just avoids the crossproduct used to get the normal in the above function
	shared_ptr<Frustum> F( new Frustum() );
	F->CameraPosition = _Position;
	F->LookVector = _Look;

	//we need a point and a normal for each plane
	//we can get this from the FOV and camera vectors

	//set up look to be normalized in front of cam position
	Vector3f Look = _Look - _Position;
	Vector3f Up = _Up;

	float scaledtan = (float)tan((G_PI/180.0f) * (_FOV * 0.5f));
	Vector3f Right = Look.cross_product(_Up).normalize();

	Vector3f tempRight = (-Right) * scaledtan;
	F->ClipPlanes[0].point = tempRight + Look;
	F->ClipPlanes[0].normal = F->ClipPlanes[0].point.normalize();//	//normal is now a normalized vector pointing down the plane
	F->ClipPlanes[0].point += _Position;		//set point
	//left clip plane built

	tempRight = Right * scaledtan;		//same thing with positive right
	F->ClipPlanes[1].point = tempRight + Look;
	F->ClipPlanes[1].normal = F->ClipPlanes[1].point.normalize();
	F->ClipPlanes[1].point += _Position;

	//now we need to build the up and down clip planes
	Vector3f tempUp = Up * scaledtan;
	F->ClipPlanes[2].point = tempUp + Look;
	F->ClipPlanes[2].normal = F->ClipPlanes[2].point.normalize();
	F->ClipPlanes[2].point += _Position;

	//and down
	tempUp = (-Up) * scaledtan;
	F->ClipPlanes[3].point = tempUp + Look;
	F->ClipPlanes[3].normal = F->ClipPlanes[3].point.normalize();
	F->ClipPlanes[3].point += _Position;

	return F;
}

Vector3f Camera::project_screen_coordinates(int x, int y)
{
	//the visualization
	//\	    |	   /
	// \    | tan /
	//  \   |----/
	//   \ 1|   /
	//    \ |  /
	//	   \| /
	//	    \/

	//get scalar from -1 to 1
	float xpos, ypos;
	float scaledtan = tanf((float)((G_PI/180.0f)*(_FOV*0.5f)));

	xpos = (float)((x-((float)_Width/2))/(_Width/2))*((float)_Width/(float)_Height);
	ypos = (float)(y-((float)_Height/2))/(_Height/2);

	Vector3f right = (_Look-_Position).cross_product(_Up);
	Vector3f up = _Up;

	Vector3f projected = _Look-_Position;
	projected += right*(scaledtan * xpos) + up*(scaledtan * ypos);
	return projected.normalize();
}

void Camera::rotate(float theta, Vector3f axis)
{
	/*
	Quaternion rotation, view, result;

	float sinhtheta = sin(theta/2);
	rotation.x = axis.x * sinhtheta;
	rotation.y = axis.y * sinhtheta;
	rotation.z = axis.z * sinhtheta;
	rotation.w = cos(theta/2);

	view.x = m_Look.x - m_Position.x;
	view.y = m_Look.y - m_Position.y;
	view.z = m_Look.z - m_Position.z;
	view.w = 0;
	view.Normalize();

	Quaternion rotconj = rotation.Conjugate();
	result = rotation * view;
	result = result * rotconj;

	m_Look.x = result.x + m_Position.x;
	m_Look.y = result.y + m_Position.y;
	m_Look.z = result.z + m_Position.z;
	*/
	Quaternion rotation, view;

	float sinhtheta = sin(theta/2);
	rotation.x = axis.x * sinhtheta;
	rotation.y = axis.y * sinhtheta;
	rotation.z = axis.z * sinhtheta;
	rotation.w = cos(theta/2);

	view.x = _Look.x - _Position.x;
	view.y = _Look.y - _Position.y;
	view.z = _Look.z - _Position.z;
	view.w = 0;
	view.make_normalized();

	Quaternion rotconj = rotation.conjugate();
	Quaternion result( rotation * view * rotconj );

	_Look.x = result.x + _Position.x;
	_Look.y = result.y + _Position.y;
	_Look.z = result.z + _Position.z;
}

void Camera::translate(Vector3f trans)
{
	_Position += trans;
	_Look += trans;
}

void Camera::translateX(float dist)
{
	Vector3f cross = (_Look - _Position).cross_product(_Up);
	translate( cross * dist );
}

void Camera::translateY(float dist)
{
	translate( _Up * dist );
}

void Camera::translateZ(float dist)
{
	translate( (_Look - _Position) * dist );
}

void Camera::rotate(Vector3f components)
{
	rotateX( components.x );
	rotateY( components.y );
	rotateZ( components.z );
}

void Camera::rotateX(float theta)
{
	Vector3f cross = (_Look - _Position).cross_product(_Up);
	rotate(theta, cross);

	//recreate up vector, normalize to stop what appears to be rounding errors
	Vector3f right = (_Look - _Position).cross_product(_Up);
	_Up = right.cross_product(_Look-_Position).normalize();
}

void Camera::rotateY(float theta)
{
	rotate(theta, _Up);
	//don't need to renormalize up vector ... we rotated around it
}

void Camera::rotateZ(float theta)
{
	rotate(theta, _Look - _Position);

	//recreate up vector
	Vector3f right = (_Look - _Position).cross_product(_Up);
	_Up = right.cross_product(_Look-_Position).normalize();
}