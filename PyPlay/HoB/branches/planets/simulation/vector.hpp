
#pragma once

#include <cmath>
#include <cassert>
#include <iostream>

void wrap_vector();

template< unsigned N, typename T >
struct Vector {
	T d[N];
	typedef T value_type;

	Vector() {
		for( unsigned i = 0; i < N; ++i )	
			d[i] = 0;
	}

	Vector( const T* data ) {
		for( unsigned i = 0; i < N; ++i )	
			d[i] = data[i];
	}
	
	Vector( T x_, T y_ ) {
		assert( N == 2 );
		d[0] = x_;	d[1] = y_;
	}

	Vector( T x_, T y_, T z_ ) {
		assert( N == 3 );
		d[0] = x_;	d[1] = y_;	d[2] = z_;
	}

	Vector( T x_, T y_, T z_, T w_ ) {
		assert( N == 4 );
		d[0] = x_;	d[1] = y_;	d[2] = z_; d[3] = w_;
	}

	T* ptr() 					{ return d; }
	const T* ptr() const 		{ return d; }
	
	T& operator[]( const unsigned i )		{ return d[i]; }
	T operator[]( const unsigned i ) const	{ return d[i]; }
	T& index( const unsigned i ) 			{ return d[i]; }
	T index( const unsigned i ) const 		{ return d[i]; }

	float length() const {
		return sqrt( length_sq() );
	}

	float length_sq() const {
		float res = 0.f;
		for( unsigned i = 0; i < N; ++i ) 	res += d[i]*d[i];
		return res;
	}

	float dot( const Vector& other ) const {
		float res = 0.f;
		for( unsigned i = 0; i < N; ++i ) 	res += d[i]*other.d[i];
		return res;
	}

	Vector<N,T> cross( const Vector<N, T>& other ) const { 
		assert( N == 3 );
		return Vector<N, T>(
			d[1]*other.d[2] - d[2]*other.d[1],
			d[2]*other.d[0] - d[0]*other.d[2],
			d[0]*other.d[1] - d[1]*other.d[0] 	);
	}

};

template< unsigned N, typename T >
Vector< N, T > operator-( const Vector<N, T>& v ) {
	Vector<N, T> res;
	for( unsigned i = 0; i < N; ++i )	res[i] = -v[i];
	return res;
}

template< unsigned N, typename T >
Vector< N, T >& operator+=( Vector<N,T>& lhs, const Vector<N,T>& rhs ) {
	for( unsigned i = 0; i < N; ++i )	lhs[i] += rhs[i];
	return lhs;
}

template< unsigned N, typename T >
Vector<N, T> operator+( const Vector<N, T>& lhs, const Vector<N, T>& rhs ) {
	Vector<N, T> res;
	for( unsigned i = 0; i < N; ++i ) 	res[i] = lhs[i] + rhs[i];
	return res;
}

template< unsigned N, typename T >
Vector< N, T >& operator-=( Vector<N,T>& lhs, const Vector<N,T>& rhs ) {
	for( unsigned i = 0; i < N; ++i )	lhs[i] -= rhs[i];
	return lhs;
}

template< unsigned N, typename T >
Vector<N, T> operator-( const Vector<N, T>& lhs, const Vector<N, T>& rhs ) {
	Vector<N, T> res;
	for( unsigned i = 0; i < N; ++i ) 	res[i] = lhs[i] - rhs[i];
	return res;
}

template< unsigned N, typename T >
bool operator<( const Vector<N, T>& lhs, const Vector<N, T>& rhs ) {
	for( unsigned i = 0; i < N; ++i ) {
		if( lhs[i] < rhs[i] ) return true;
		else if( lhs[i] > rhs[i] ) return false;
	}
	return false;
}

template< unsigned N, typename T >
Vector< N, T >& operator*=( Vector<N, T>& lhs, const T scale ) {
	for( unsigned i = 0; i < N; ++i )	lhs[i] *= scale;
	return lhs;
}

template< unsigned N, typename T, typename U >
Vector< N, T > operator*( const Vector<N, T>& lhs, const U scale ) {
	Vector<N, T> res;
	for( unsigned i = 0; i < N; ++i ) 	res[i] = lhs[i] * scale;
	return res;
}

template< unsigned N, typename T >
Vector< N, T >& operator/=( Vector<N, T>& lhs, const T div ) {
	float scale = 1.f / (float)div;
	for( unsigned i = 0; i < N; ++i )	lhs[i] = (T)((float)lhs[i] * scale);
	return lhs;
}

template< unsigned N, typename T >
Vector< N, T > operator/( const Vector<N, T>& lhs, const T div ) {
	Vector<N, T> res;
	float scale = 1.f / (float)div;
	for( unsigned i = 0; i < N; ++i ) 	res[i] = (T)((float)lhs[i] * scale);
	return res;
}

template< unsigned N, typename T >
std::ostream& operator <<( std::ostream& os, const Vector<N, T>& v ) {
	os << "(";
	for( unsigned i = 0; i < N-1; ++i ) 
		os << v.d[i] << ", ";
   	os << v.d[N-1] << ")";
	return os;
}

typedef Vector< 2, float > Vector2f;
typedef Vector< 3, float > Vector3f;
typedef Vector< 4, float > Vector4f;
typedef Vector< 3, unsigned char > Vector3ub;
typedef Vector< 4, unsigned char > Vector4ub;

