
#pragma once

#include "vector.hpp"
#include "matrix.hpp"
#include "component.hpp"

void wrap_transform();

struct Transform: public Component {
	typedef boost::shared_ptr<Transform> pointer_type;

	Transform();
	Transform( const Vector3f& pos, const Vector3f& rot );

	Vector3f transform( const Vector3f& in );
	Vector3f right();
	Vector3f up();
	Vector3f forward();

	void translate( const Vector3f& vec );
	void translate_relative( const Vector3f& vec );

	void rotate( const Vector3f& vec );
	void rotate_relative( const Vector3f& vec );

	Matrix4f build_matrix( bool trans_first = false ) const;
	Vector3f position, rotation;
};

