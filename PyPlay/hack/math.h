#ifndef MATH__H
#define MATH__H

#include <cmath>
#include <fstream>

const double G_PI = 3.141592654;
const double G_EPSILON = 0.000001;
void export_math();

template< typename T >
class Vector2
{
public:
	union
	{
		T val[2];
		struct{	T x,y;	};
	};

	Vector2() : x(0), y(0)									{}
	Vector2(const Vector2<T>& vec) : x(vec.x), y(vec.y)		{}
	Vector2(T _x, T _y) : x(_x), y(_y)						{}
	Vector2(T _val[2]): x(_val[0]), y(_val[1])				{}

	~Vector2()												{}

	inline operator T*()
	{
		return &x;
	}

	template< typename U >
	inline Vector2< U > convert() const						{ return Vector2< U >( (U)x, (U)y ); }

	inline bool operator ==(const Vector2<T>& vec) const
	{
		return (	fabs( (double)(x-vec.x) ) < G_EPSILON &&
					fabs( (double)(y-vec.y) ) < G_EPSILON );
	}

	inline Vector2<T> operator -() const					{ return Vector2<T>( -x, -y ); }
	inline void operator+=(const Vector2<T>& o)				{ x+=o.x; y+=o.y; }
	inline void operator-=(const Vector2<T>& o)				{ x-=o.x; y-=o.y; }

	inline Vector2<T> operator+(const Vector2<T>& o) const	{ return Vector2<T>( x+o.x, y+o.y ); }
	inline Vector2<T> operator-(const Vector2<T>& o) const	{ return Vector2<T>( x-o.x, y-o.y ); }

	//scalars
	inline void operator*=(const Vector2<T>& o)				{ x*=o.x; y*=o.y; }
	inline void operator*=(T s)								{ x*=s; y*=s; }

	inline void operator/=(const Vector2<T>& o)				{ x/=o.x; y/=o.y; }
	inline void operator/=(T s)								{ x/=s; y/=s; }


	inline Vector2<T> operator*(const Vector2<T>& o) const	{ return Vector2<T>( x*o.x, y*o.y ); }
	inline Vector2<T> operator*(T s) const					{ return Vector2<T>( x*s, y*s ); }

	//use float scalar, used on non-fp types to scale and then recast
	inline Vector2<T> scale( float s ) const				{ return Vector2<T>( (T)(x*s), (T)(y*s) ); }

	inline Vector2<T> operator/(const Vector2<T>& o) const	{ return Vector2<T>( x/o.x, y/o.y ); }
	inline Vector2<T> operator/(T s) const					{ return Vector2<T>( x/s, y/s ); }

	inline void zero()										{ x=0; y=0; }
	inline float length() const								{ return sqrtf((float)x*(float)x + (float)y*(float)y); }
	inline T length_sq() const								{ return x*x + y*y; }
	inline Vector2<T> normalize() const						{ return (*this)*(T)(1.f/length()); }
	inline void make_normalized()							{ (*this) = normalize(); }

	inline T dot_product(const Vector2<T>& o) const			{ return x*o.x + y*o.y; }

};
typedef Vector2<double> Vector2f8;
typedef Vector2<float> Vector2f;
typedef Vector2<long> Vector2i;
typedef Vector2<short> Vector2d;
typedef Vector2<char> Vector2b;
typedef Vector2<unsigned char> Vector2ub;

template <typename T>
inline bool operator <(const Vector2<T>& v1, const Vector2<T>& v2)
{
	if(v1.x < v2.x) return true;
	if(v2.x < v1.x)	return false;

	if(v1.y < v2.y) return true;
	else			return false;
}

template <typename T>
inline std::ifstream& operator >>( std::ifstream& i, Vector2<T>& v ) {
	i >> v.x; i >> v.y;
	return i;
}

template <typename T>
inline std::ostream& operator <<( std::ostream& o, const Vector2<T>& v ) {
	o << "(" << v.x << ", " << v.y << ")";
	return o;
}


template< typename T >
class Vector3
{
public:
	union
	{
		T val[3];
		struct {	T x, y, z;	};
		struct {	T r, g, b;	};
	};

	Vector3() : x(0), y(0), z(0)												{}
	Vector3(const Vector3<T>& vec) : x(vec.x), y(vec.y), z(vec.z)				{}
	Vector3(T _x, T _y, T _z) : x(_x), y(_y), z(_z)								{}
	Vector3(T _val[3]): x(_val[0]), y(_val[1]), z(_val[2])						{}

	~Vector3()																	{}

	inline operator T*()
	{
		return &x;
	}

	template< typename U >
	inline Vector3<U> convert()	const						{ return Vector3<U>( (U)x, (U)y, (U)z ); }

	inline bool operator ==(const Vector3<T>& vec) const
	{
		return (	fabs( (double)(x-vec.x) ) < G_EPSILON &&
					fabs( (double)(y-vec.y) ) < G_EPSILON &&
					fabs( (double)(z-vec.z) ) < G_EPSILON );
	}

	inline bool operator <(const Vector3<T>& vec) const
	{
		if( x < vec.x ) return true;	else return false;
		if( y < vec.y ) return true;	else return false;
		if( z < vec.z ) return true;	else return false;
		return false;
	}

	inline Vector3<T> operator -() const					{ return Vector3<T>( -x, -y, -z ); }
	inline void operator+=(const Vector3<T>& o)				{ x+=o.x; y+=o.y; z+=o.z; }
	inline void operator-=(const Vector3<T>& o)				{ x-=o.x; y-=o.y; z-=o.z; }

	inline Vector3<T> operator+(const Vector3<T>& o) const	{ return Vector3<T>( x+o.x, y+o.y, z+o.z ); }
	inline Vector3<T> operator-(const Vector3<T>& o) const	{ return Vector3<T>( x-o.x, y-o.y, z-o.z ); }

	//scalars
	inline void operator*=(const Vector3<T>& o)				{ x*=o.x; y*=o.y; z*=o.z; }
	inline void operator*=(T s)								{ x*= s; y*=s; z*=s; }

	inline void operator/=(const Vector3<T>& o)				{ x/=o.x; y/=o.y; z/=o.z; }
	inline void operator/=(T s)								{ x/= s; y/=s; z/=s; }


	inline Vector3<T> operator*(const Vector3<T>& o) const	{ return Vector3<T>( x*o.x, y*o.y, z*o.z ); }
	inline Vector3<T> operator*(T s) const					{ return Vector3<T>( x*s, y*s, z*s ); }

	//use float scalar, used on non-fp types to scale and then recast
	inline Vector3<T> scale( float s ) const				{ return Vector3<T>( (T)(x*s), (T)(y*s), (T)(z*s) ); }

	inline Vector3<T> operator/(const Vector3<T>& o) const	{ return Vector3<T>( x/o.x, y/o.y, z/o.z ); }
	inline Vector3<T> operator/(T s) const					{ return Vector3<T>( x/s, y/s, z/s ); }

	inline void zero()										{ x=0; y=0; z=0; }
	inline T length() const									{ return (T)sqrt((double)x*x + (double)y*y + (double)z*z); }
	inline T length_sq() const								{ return x*x + y*y + z*z; }
	inline Vector3<T> normalize() const						{ return (*this)*(T)(1./length()); }
	inline void make_normalized()							{ (*this) = normalize(); }

	inline T dot_product(const Vector3<T>& o) const			{ return x*o.x + y*o.y + z*o.z; }
	Vector3<T> cross_product(const Vector3<T>& o) const		{ return Vector3<T>( y*o.z-z*o.y, z*o.x-x*o.z, x*o.y-y*o.x ); }
};
typedef Vector3<double> Vector3f8;
typedef Vector3<float> Vector3f;
typedef Vector3<int> Vector3i;
typedef Vector3<short> Vector3d;
typedef Vector3<char> Vector3b;
typedef Vector3<unsigned char> Vector3ub;

template <typename T>
inline std::ifstream& operator >>( std::ifstream& i, Vector3<T>& v ) {
	i >> v.x; i >> v.y; i >> v.z;
	return i;
}

template <typename T>
inline std::ostream& operator <<( std::ostream& o, Vector3<T>& v ) {
	o << "(" << v.x << ", " << v.y << ", " << v.z << ")";
}
	

class Matrix33
{
public:
	union
	{
		float	m[9];

		struct
		{
			//column-major form for ogl
			float m00, m10, m20;
			float m01, m11, m21;
			float m02, m12, m22;
		};
	};

	Matrix33(): m00(1), m01(0), m02(0), m10(0), m11(1), m12(0), m20(0), m21(0), m22(1) {}
	Matrix33(float _m00, float _m01, float _m02, float _m10, float _m11, float _m12, 
		float _m20, float _m21, float _m22) :
						m00(_m00), m01(_m01), m02(_m02), m10(_m10), m11(_m11), m12(_m12), 
							m20(_m20), m21(_m21), m22(_m22) {}

	~Matrix33() {}

	inline operator float*()
	{
		return &m00;
	}

	inline Matrix33 operator*(Matrix33& mat)
	{
		Matrix33 ret;
		ret.m00 = m00 * mat.m00 + m01 * mat.m10 + m02 * mat.m20;
		ret.m01 = m00 * mat.m01 + m01 * mat.m11 + m02 * mat.m21;
		ret.m02 = m00 * mat.m02 + m01 * mat.m12 + m02 * mat.m22;

		ret.m10 = m10 * mat.m00 + m11 * mat.m10 + m12 * mat.m20;
		ret.m11 = m10 * mat.m01 + m11 * mat.m11 + m12 * mat.m21;
		ret.m12 = m10 * mat.m02 + m11 * mat.m12 + m12 * mat.m22;

		ret.m20 = m20 * mat.m00 + m21 * mat.m10 + m22 * mat.m20;
		ret.m21 = m20 * mat.m01 + m21 * mat.m11 + m22 * mat.m21;
		ret.m22 = m20 * mat.m02 + m21 * mat.m12 + m22 * mat.m22;
		return ret;
	}

	inline Matrix33 operator*(float scale)
	{
		Matrix33 ret;
		ret.m[0] = m[0]*scale;
		ret.m[1] = m[1]*scale;
		ret.m[2] = m[2]*scale;
		ret.m[3] = m[3]*scale;
		ret.m[4] = m[4]*scale;
		ret.m[5] = m[5]*scale;
		ret.m[6] = m[6]*scale;
		ret.m[7] = m[7]*scale;
		ret.m[8] = m[8]*scale;
	}

	inline void operator*=(float scale)
	{
		m[0] *= scale;
		m[1] *= scale;
		m[2] *= scale;
		m[3] *= scale;
		m[4] *= scale;
		m[5] *= scale;
		m[6] *= scale;
		m[7] *= scale;
		m[8] *= scale;
	}

	inline Matrix33 operator/(float scale)
	{
		Matrix33 ret;
		ret.m[0] = m[0]/scale;
		ret.m[1] = m[1]/scale;
		ret.m[2] = m[2]/scale;
		ret.m[3] = m[3]/scale;
		ret.m[4] = m[4]/scale;
		ret.m[5] = m[5]/scale;
		ret.m[6] = m[6]/scale;
		ret.m[7] = m[7]/scale;
		ret.m[8] = m[8]/scale;
	}

	inline void operator/=(float scale)
	{
		m[0] /= scale;
		m[1] /= scale;
		m[2] /= scale;
		m[3] /= scale;
		m[4] /= scale;
		m[5] /= scale;
		m[6] /= scale;
		m[7] /= scale;
		m[8] /= scale;
	}

	template< typename T >
	inline Vector3<T> operator*(const Vector3<T>& o)
	{
		return Vector3<T> (	(m00*o.x + m01*o.y + m02*o.z),
							(m10*o.x + m11*o.y + m12*o.z),
							(m20*o.x + m21*o.y + m22*o.z) );
	}

	static inline Matrix33 build_rotation_matrix(float anglex, float angley, float anglez)
	{
		float cosx = (float)cos(anglex), sinx = (float)sin(anglex);
		Matrix33 x(1.0f, 0.0f, 0.0f, 0.0f, cosx, sinx, 0.0f, -sinx, cosx);

		float cosy = (float)cos(angley), siny = (float)sin(angley);
		Matrix33 y(cosy, 0.0f, -siny, 0.0f, 1.0f, 0.0f, siny, 0.0f, cosy);

		float cosz = (float)cos(anglez), sinz = (float)sin(anglez);
		Matrix33 z(cosz, sinz, 0.0f, -sinz, cosz, 0.0f, 0.0f, 0.0f, 1.0f);

		Matrix33 ret = (x*y)*z;
		return ret;
	}

	static inline Matrix33 build_rotation_matrix(float* rot)
	{
		return build_rotation_matrix(rot[0], rot[1], rot[2]);
	}
};

class Matrix44
{
public:
	union
	{
		struct
		{
			float m[16];
		};
		struct
		{
			float m00, m10, m20, m30;
			float m01, m11, m21, m31;
			float m02, m12, m22, m32;
			float m03, m13, m23, m33;
		};
	};

	Matrix44(): m00(1), m01(0), m02(0), m03(0), m10(0), m11(1), m12(0), m13(0), m20(0), m21(0), m22(1), m23(0), m30(0), m31(0), m32(0), m33(1) {}
	Matrix44(float _m00, float _m01, float _m02, float _m03, float _m10, float _m11, float _m12, float _m13,
		float _m20, float _m21, float _m22, float _m23, float _m30, float _m31, float _m32, float _m33) :
					m00(_m00), m01(_m01), m02(_m02), m03(_m03), m10(_m10), m11(_m11), m12(_m12), m13(_m13), 
					m20(_m20), m21(_m21), m22(_m22), m23(_m23), m30(_m30), m31(_m31), m32(_m32), m33(_m33) {}
	Matrix44(const Matrix33& mat): m00(mat.m00), m01(mat.m01), m02(mat.m02), m10(mat.m10), m11(mat.m11), m12(mat.m12), m20(mat.m20), 
		m21(mat.m21), m22(mat.m22), m03(0), m13(0), m23(0), m33(1), m30(0), m31(0), m32(0) {}

	~Matrix44() {}

	inline void set_translation(float trans[3])
	{
		m03 = trans[0];
		m13 = trans[1];
		m23 = trans[2];
	}
	inline void set_rotation(const Matrix33& mat)
	{
		m00 = mat.m00;
		m01 = mat.m01;
		m02 = mat.m02;

		m10 = mat.m10;
		m11 = mat.m11;
		m12 = mat.m12;

		m20 = mat.m20;
		m21 = mat.m21;
		m22 = mat.m22;
	}


	inline operator float*()
	{
		return &m00;
	}

	inline Matrix44 operator*(Matrix44& mat)
	{
		Matrix44 ret;
		ret.m00 = (m00 * mat.m00) + (m01 * mat.m10) + (m02 * mat.m20) + (m03 * mat.m30);
		ret.m01 = (m00 * mat.m01) + (m01 * mat.m11) + (m02 * mat.m21) + (m03 * mat.m31);
		ret.m02 = (m00 * mat.m02) + (m01 * mat.m12) + (m02 * mat.m22) + (m03 * mat.m32);
		ret.m03 = (m00 * mat.m03) + (m01 * mat.m13) + (m02 * mat.m23) + (m03 * mat.m33);

		ret.m10 = (m10 * mat.m00) + (m11 * mat.m10) + (m12 * mat.m20) + (m13 * mat.m30);
		ret.m11 = (m10 * mat.m01) + (m11 * mat.m11) + (m12 * mat.m21) + (m13 * mat.m31);
		ret.m12 = (m10 * mat.m02) + (m11 * mat.m12) + (m12 * mat.m22) + (m13 * mat.m32);
		ret.m13 = (m10 * mat.m03) + (m11 * mat.m13) + (m12 * mat.m23) + (m13 * mat.m33);

		ret.m20 = (m20 * mat.m00) + (m21 * mat.m10) + (m22 * mat.m20) + (m23 * mat.m30);
		ret.m21 = (m20 * mat.m01) + (m21 * mat.m11) + (m22 * mat.m21) + (m23 * mat.m31);
		ret.m22 = (m20 * mat.m02) + (m21 * mat.m12) + (m22 * mat.m22) + (m23 * mat.m32);
		ret.m23 = (m20 * mat.m03) + (m21 * mat.m13) + (m22 * mat.m23) + (m23 * mat.m33);

		ret.m30 = (m30 * mat.m00) + (m31 * mat.m10) + (m32 * mat.m20) + (m33 * mat.m30);
		ret.m31 = (m30 * mat.m01) + (m31 * mat.m11) + (m32 * mat.m21) + (m33 * mat.m31);
		ret.m32 = (m30 * mat.m02) + (m31 * mat.m12) + (m32 * mat.m22) + (m33 * mat.m32);
		ret.m33 = (m30 * mat.m03) + (m31 * mat.m13) + (m32 * mat.m23) + (m33 * mat.m33);
		
		return ret;
	}

	template< typename T >
	inline Vector3<T> operator*(const Vector3<T>& o)
	{
		return Vector3<T> (	(m00*o.x + m01*o.y + m02*o.z) + m03,
							(m10*o.x + m11*o.y + m12*o.z) + m13,
							(m20*o.x + m21*o.y + m22*o.z) + m23 );
	}

	inline Matrix44 operator*(float scale)
	{
		Matrix44 ret;
		ret.m[0] = m[0]*scale;
		ret.m[1] = m[1]*scale;
		ret.m[2] = m[2]*scale;
		ret.m[3] = m[3]*scale;
		ret.m[4] = m[4]*scale;
		ret.m[5] = m[5]*scale;
		ret.m[6] = m[6]*scale;
		ret.m[7] = m[7]*scale;
		ret.m[8] = m[8]*scale;
		ret.m[9] = m[9]*scale;
		ret.m[10] = m[10]*scale;
		ret.m[11] = m[11]*scale;
		ret.m[12] = m[12]*scale;
		ret.m[13] = m[13]*scale;
		ret.m[14] = m[14]*scale;
		ret.m[15] = m[15]*scale;
	}

	inline void operator*=(float scale)
	{
		m[0] *= scale;
		m[1] *= scale;
		m[2] *= scale;
		m[3] *= scale;
		m[4] *= scale;
		m[5] *= scale;
		m[6] *= scale;
		m[7] *= scale;
		m[8] *= scale;
		m[9] *= scale;
		m[10] *= scale;
		m[11] *= scale;
		m[12] *= scale;
		m[13] *= scale;
		m[14] *= scale;
		m[15] *= scale;
	}

	inline Matrix44 operator/(float scale)
	{
		Matrix44 ret;
		ret.m[0] = m[0]/scale;
		ret.m[1] = m[1]/scale;
		ret.m[2] = m[2]/scale;
		ret.m[3] = m[3]/scale;
		ret.m[4] = m[4]/scale;
		ret.m[5] = m[5]/scale;
		ret.m[6] = m[6]/scale;
		ret.m[7] = m[7]/scale;
		ret.m[8] = m[8]/scale;
		ret.m[9] = m[9]/scale;
		ret.m[10] = m[10]/scale;
		ret.m[11] = m[11]/scale;
		ret.m[12] = m[12]/scale;
		ret.m[13] = m[13]/scale;
		ret.m[14] = m[14]/scale;
		ret.m[15] = m[15]/scale;
	}

	inline void operator/=(float scale)
	{
		m[0] /= scale;
		m[1] /= scale;
		m[2] /= scale;
		m[3] /= scale;
		m[4] /= scale;
		m[5] /= scale;
		m[6] /= scale;
		m[7] /= scale;
		m[8] /= scale;
		m[9] /= scale;
		m[10] /= scale;
		m[11] /= scale;
		m[12] /= scale;
		m[13] /= scale;
		m[14] /= scale;
		m[15] /= scale;
	}
};


class Quaternion
{
public:
	union
	{
		float val[4];
		struct {	float x, y, z, w;	};
	};

	Quaternion(): x(0), y(0), z(0), w(0)													{}
	Quaternion(const Quaternion& quat): x(quat.x), y(quat.y), z(quat.z), w(quat.w)			{}
	Quaternion(float _x, float _y, float _z, float _w): x(_x), y(_y), z(_z), w(_w)			{}
	~Quaternion()																			{}

	inline Quaternion conjugate() const							{ return Quaternion( -x, -y, -z, w ); }
	inline void make_conjugate()								{ x=-x; y=-y; z=-z; }

	inline Quaternion operator+(const Quaternion& o) const		{ return Quaternion(x+o.x, y+o.y, z+o.z, w+o.w); }

	inline void operator*=(float s)								{ x*=s; y*=s; z*=s; w*=s; }
	inline Quaternion operator*(float s) const					{ return Quaternion(x*s, y*s, z*s, w*s); }

	inline void operator/=(float s)								{ x/=s; y/=s; z/=s; w/=s; }
	inline Quaternion operator/(float s) const					{ return Quaternion(x/s, y/s, z/s, w/s); }

	inline float length() const					{ return sqrt(x*x + y*y + z*z + w*w); }
	inline float length_sq() const				{ return (x*x + y*y + z*z + w*w); }
	inline Quaternion normalize() const			{ return (*this) / length(); }
	inline void make_normalized()				{ (*this) /= length(); }

	/*inline void operator*=(const Quaternion& quat)
	{
		x = w*quat.x + x*quat.w + y*quat.z - z*quat.y;
		y = w*quat.y - x*quat.z + y*quat.w + z*quat.x;
		z = w*quat.z + x*quat.y - y*quat.x + z*quat.w;
		w = w*quat.w - x*quat.x - y*quat.y - z*quat.z;
	}*/

	inline Quaternion operator*(const Quaternion& q) const
	{
		Quaternion C;

		C.w = w*q.w - x*q.x - y*q.y - z*q.z;
		C.x = w*q.x + x*q.w + y*q.z - z*q.y;
		C.y = w*q.y + y*q.w + z*q.x - x*q.z;
		C.z = w*q.z + z*q.w + x*q.y - y*q.x;

		return C;
	}

	inline Matrix33 build_rotation_matrix() const
	{
		float xx = x * x;
		float xy = x * y;
		float xz = x * z;
		float xw = x * w;

		float yy = y * y;
		float yz = y * z;
		float yw = y * w;

		float zz = z * z;
		float zw = z * w;

		return Matrix33 (	1 - 2*(yy + zz), 2*(xy - zw), 2*(xz + yw),
							2*(xy + zw), 1 - 2*(xx + zz), 2*(yz - xw),
							2*(xz - yw), 2*(yz + xw), 1 - 2*(xx + yy)		);
	}

	static inline Quaternion build_from_euler_angles(float x, float y, float z)
	{
		Quaternion qx(sin(x/2.0f), 0.0f, 0.0f, cos(x/2.0f));
		Quaternion qy(0.0f, sin(y/2.0f), 0.0f, cos(y/2.0f));
		Quaternion qz(0.0f, 0.0f, sin(z/2.0f), cos(z/2.0f));

		Quaternion ret = (qx*qy)*qz;
		return ret.normalize();
	}

	static inline Quaternion build_from_euler_angles(float* angles)
	{
		return Quaternion::build_from_euler_angles(angles[0], angles[1], angles[2]);
	}

	static inline Quaternion slerp(const Quaternion& A, const Quaternion& B, float t)
	{
		if( fabsf(A.x-B.x) < G_EPSILON && fabsf(A.y-B.y) < G_EPSILON && 
			fabsf(A.z-B.z) < G_EPSILON && fabsf(A.w-B.w) < G_EPSILON )
			return A;

		float dp = (A.x*B.x) + (A.y*B.y) + (A.z*B.z) + (A.w*B.w);
		float theta = acos(dp);

		if(fabs(theta) < G_EPSILON)
			return A;

		float sintheta = sin(theta);
		float invsintheta = (float)1.0 / sintheta;
 
		float pdt1 = sin( (1.0f-t)*theta ) * invsintheta;
		float pdt2 = sin( t*theta ) * invsintheta;

		if(dp < 0.0f) 
		{
			//rotate one 180 degrees
			pdt1 = -pdt1;
			Quaternion ret(A*pdt1 + B*pdt2);
			return ret.normalize();
		}
		
		Quaternion ret(A*pdt1 + B*pdt2);
		return ret.normalize();
	}
};


#endif //defined math.h

