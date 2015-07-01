
#include "transform.hpp"

#include <boost/python.hpp>
using namespace boost::python;

void wrap_transform() {
	class_<Transform, Transform::pointer_type, bases<Component>,
		boost::noncopyable>( "Transform" )
		.def( init<const Vector3f&, const Vector3f&>() )
		.def( "translate", &Transform::translate )
		.def( "translate_relative", &Transform::translate_relative )

		.def( "transform", &Transform::transform )
		.def( "right", &Transform::right )
		.def( "up", &Transform::up )
		.def( "forward", &Transform::forward )

		.def( "rotate", &Transform::rotate )
		.def( "rotate_relative", &Transform::rotate_relative )

		.def( "build_matrix", &Transform::build_matrix )

		.def_readwrite( "position", &Transform::position )
		.def_readwrite( "rotation", &Transform::rotation )
		;

}

Transform::Transform(): Component( Component::Transform ) 
{}

Transform::Transform( const Vector3f& pos, const Vector3f& rot ):
	Component( Component::Transform ), position( pos ), rotation( rot )
{}

Vector3f Transform::transform( const Vector3f& in ) {
	Vector4f vec( in.d[0], in.d[1], in.d[2], 1.0 );
	Vector4f result = build_matrix( false ) * vec;
	return Vector3f( result.d[0] / result.d[3], result.d[1] / result.d[3], 
		result.d[2] / result.d[3] );
}

Vector3f Transform::right() {
	Matrix4f m = build_matrix( true );
	return Vector3f( m[0], m[1], m[2] );
}
	
Vector3f Transform::up() {
	Matrix4f m = build_matrix( true );
	return Vector3f( m[4], m[5], m[6] );
}
	
Vector3f Transform::forward() {
	Matrix4f m = build_matrix( true );
	return Vector3f( m[8], m[9], m[10] );
}


void Transform::translate( const Vector3f& v ) {
	position += v;
}

void Transform::translate_relative( const Vector3f& v ) {
	Matrix4f m = build_matrix( true );
	//position += Vector3f( m[0], m[4], m[8] ) * v[0];
	//position += Vector3f( m[1], m[5], m[9] ) * v[1];
	//position += Vector3f( m[2], m[6], m[10] ) * v[2];
	position += Vector3f( m[0], m[1], m[2] ) * v[0];
	position += Vector3f( m[4], m[5], m[6] ) * v[1];
	position += Vector3f( m[8], m[9], m[10] ) * v[2];
}

void Transform::rotate( const Vector3f& v ) {
	rotation += v;
}

void Transform::rotate_relative( const Vector3f& v ) {

}
	
Matrix4f Transform::build_matrix( bool trans_first ) const {
	Matrix4f zrot = Matrix4f::rotation( 
		Vector3f( 0., 0., 1. ), rotation[2] );
	Matrix4f yrot = Matrix4f::rotation( 
		Vector3f( 0., 1., 0. ), rotation[0] );
	Matrix4f xrot = Matrix4f::rotation(
		Vector3f( 1., 0., 0. ), rotation[1] );
	Matrix4f trans = Matrix4f::translation( position );

	if( trans_first )
		return zrot * yrot * xrot * trans;
	return trans * zrot * yrot * xrot;
}

