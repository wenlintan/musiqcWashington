
#include "vector.hpp"

void wrap_matrix();

template< unsigned N, typename T >
struct Matrix {
	T d[ N*N ];
	typedef T value_type;

	Matrix() {
		for( unsigned i = 0; i < N*N; ++i )		
			d[i] = 0;
	}

	T* ptr() 					{ return d; }
	const T* ptr() const 		{ return d; }
	
	T& operator[]( const unsigned i )		{ return d[i]; }
	T operator[]( const unsigned i ) const	{ return d[i]; }
	T& index( const unsigned i ) 			{ return d[i]; }
	T index( const unsigned i ) const 		{ return d[i]; }

	static Matrix identity() {
		Matrix res;
		res[0] = res[5] = res[10] = res[15] = 1;
		return res;
	}

	static Matrix rotation( const Vector<3, T>& v, float theta ) {
		assert( N == 3 || N == 4 );

		Matrix res;
		float c = cos( theta ), s = sin( theta );
		res[0*N + 0] = c + (1 - c)*v[0]*v[0];
		res[0*N + 1] = s*v[2] + (1 - c)*v[1]*v[0];
		res[0*N + 2] = -s*v[1] + (1 - c)*v[2]*v[0];

		res[1*N + 0] = -s*v[2] + (1 - c)*v[0]*v[1];
		res[1*N + 1] = c + (1 - c)*v[1]*v[1];
		res[1*N + 2] = s*v[0] + (1 - c)*v[2]*v[1];

		res[2*N + 0] = s*v[1] + (1 - c)*v[0]*v[2];
		res[2*N + 1] = -s*v[0] + (1 - c)*v[1]*v[2];
		res[2*N + 2] = c + (1 - c)*v[2]*v[2];

		if( N == 4 ) res[15] = 1;
		return res;
	}

	static Matrix rotation( const Vector<3, T>& euler ) {
		assert( N == 3 );

		Matrix res;
		return res;
	}

	static Matrix translation( const Vector<3, T>& trans ) {
		assert( N == 4 );
		Matrix res = Matrix::identity();
		res[12] = trans[0];
		res[13] = trans[1];
		res[14] = trans[2];
		return res;
	}

	static Matrix perspective( float fov, float aspect,
		float nearz, float farz ) {
		assert( N == 4 );

		Matrix res;
		float f = 1.f / tan( fov / 2 );
		res[0] = f / aspect;
		res[5] = f;
		res[10] = (farz + nearz) / (nearz - farz);
		res[11] = -1.f;
		res[14] = 2.f*nearz*farz / (nearz - farz);
		return res;
	}

	static Matrix ortho( float minx, float maxx, float miny, float maxy,
		float nearz, float farz ) {
		assert( N == 4 );

		Matrix res;
		float tx = -(minx + maxx) / (maxx - minx);
		float ty = -(miny + maxy) / (maxy - miny);
		float tz = -(nearz + farz) / (farz - nearz);

		res[0] = 2.f / (maxx - minx);
		res[5] = 2.f / (maxy - miny);
		res[10] = -2.f / (farz - nearz);
		res[12] = tx;
		res[13] = ty;
		res[14] = tz;
		res[15] = 1.f;
		return res;
	}

};


template< unsigned N, typename T >
Matrix<N, T> operator+( const Matrix<N, T>& lhs, const Matrix<N, T>& rhs ) {
	Matrix<N, T> res;
	for( unsigned i = 0; i < N*N; ++i ) 	res[i] = lhs[i] + rhs[i];
	return res;
}

template< unsigned N, typename T >
Matrix<N, T>& operator+=( Matrix<N, T>& lhs, const Matrix<N, T>& rhs ) {
	for( unsigned i = 0; i < N*N; ++i ) 	lhs[i] += rhs[i];
	return lhs;
}

template< unsigned N, typename T >
Matrix<N, T> operator-( const Matrix<N, T>& lhs, const Matrix<N, T>& rhs ) {
	Matrix<N, T> res;
	for( unsigned i = 0; i < N*N; ++i ) 	res[i] = lhs[i] - rhs[i];
	return res;
}

template< unsigned N, typename T >
Matrix<N, T>& operator-=( Matrix<N, T>& lhs, const Matrix<N, T>& rhs ) {
	for( unsigned i = 0; i < N*N; ++i ) 	lhs[i] -= rhs[i];
	return lhs;
}

template< unsigned N, typename T >
Matrix<N, T> operator*( const Matrix<N, T>& lhs, const Matrix<N, T>& rhs ) {
	Matrix<N, T> res;
	for( unsigned i = 0; i < N; ++i ) for( unsigned j = 0; j < N; ++j )
		for( unsigned k = 0; k < N; ++k )
			res[ j*N + i ] += lhs[ k*N + i ] * rhs[ j*N + k ];
	return res;
}

template< unsigned N, typename T >
Matrix<N, T>& operator*=( Matrix<N, T>& lhs, const Matrix<N, T>& rhs ) {
	return (lhs = lhs * rhs);
}

template< unsigned N, typename T >
Vector<N, T> operator*( const Matrix<N, T>& lhs, const Vector<N, T>& rhs ) {
	Vector<N, T> res;
	for( unsigned i = 0; i < N; ++i )
		for( unsigned k = 0; k < N; ++k )
			res[ i ] += lhs[ k*N + i ] * rhs[ k ];
	return res;
}

typedef Matrix< 4, float > Matrix4f;

