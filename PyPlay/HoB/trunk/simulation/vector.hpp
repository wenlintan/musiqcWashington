
#include <cmath>
#include <iostream>

void wrap_vector();

template< typename T >
struct Vector3 {
	T d[3];
	typedef T value_type;

	Vector3() {
		d[0] = d[1] = d[2] = static_cast<T>(0);
	}

	Vector3( T data[3] ) {
		d[0] = data[0];	d[1] = data[1];	d[2] = data[2];
	}

	Vector3( T x_, T y_, T z_ ) {
		d[0] = x_;	d[1] = y_;	d[2] = z_;
	}

	operator T* () {
		return d;
	}

	operator const T* () const {
		return d;
	}
	
	Vector3 operator-() {
		return Vector3<T>( -d[0], -d[1], -d[2] );
	}

	Vector3& operator+=( const Vector3& other ) {
		d[0] += other.d[0];	d[1] += other.d[1];	d[2] += other.d[2];
		return *this;
	}

	Vector3 operator+( const Vector3& other ) const {
		return Vector3<T>( d[0] + other.d[0], d[1] + other.d[1],
				d[2] + other.d[2] );
	}

	Vector3& operator-=( const Vector3& other ) {
		d[0] -= other.d[0];	d[1] -= other.d[1];	d[2] -= other.d[2];
		return *this;
	}

	Vector3 operator-( const Vector3& other ) const {
		return Vector3<T>( d[0] - other.d[0], d[1] - other.d[1],
				d[2] - other.d[2] );
	}

	Vector3& operator*=( T scale ) {
		d[0] *= scale;	d[1] *= scale;	d[2] *= scale;
		return *this;
	}

	Vector3 operator*( T scale ) const {
		return Vector3<T>( d[0]*scale, d[1]*scale, d[2]*scale );
	}

	T index( size_t i ) const {
		return d[i];
	}

	float length() const {
		return sqrt( (float)d[0]*d[0] + d[1]*d[1] + d[2]*d[2] );
	}

	float dot( const Vector3& other ) {
		return d[0]*other.d[0] + d[1]*other.d[1] + d[2]*other.d[2];
	}

	friend std::ostream& operator <<( std::ostream& os,
		const Vector3<T>& v ) {
		os << "(" << v.d[0] << ", " << v.d[1] << ", " << v.d[2] << ")";
		return os;
	}
};

typedef Vector3< float > Vector3f;
typedef Vector3< unsigned char > Vector3ub;

