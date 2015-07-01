#ifndef MATRIX__H
#define MATRIX__H

#pragma once

#include <string>
#include <iostream>
#include <sstream>

#include <vector>
#include <algorithm>

namespace {

const float epsilon = 1e-5f;
template< typename T > 
T matrix_abs( const T& v ) {
	if (v < 0)		return -v;
	return v;
}

template< typename T >
inline bool matrix_eq( const T& one, const T& two ) {
	return one == two;
}

template <>
inline bool matrix_eq<float>( const float& one, const float& two ) {
	return matrix_abs( one - two ) < epsilon;
}

}

template< typename T >
class matrix_vector {
protected:
	std::vector<T> row;

public:
	size_t cols;
	matrix_vector< T >( size_t cols_ ): row( cols_ ), cols( cols_ ) { 
		for( size_t c = 0; c < cols; ++c )	row[ c ] = T(0);
	}

	matrix_vector< T >( const std::vector<T>& data ): row( data ), cols( data.size() )
	{ }

	template< typename Iterator >
	matrix_vector< T >( Iterator first, Iterator last ) {
		for( ; first != last; ++first )		row.push_back( *first );
		cols = row.size();
	}

	template< typename Iterator, typename UnaryOperator >
	matrix_vector< T >( Iterator first, Iterator last, UnaryOperator op ) {
		for( ; first != last; ++first )		row.push_back( op(*first) );
		cols = row.size();
	}

	matrix_vector< T >( const matrix_vector< T >& other ): row( other.row ), cols( other.row.size() )
	{ }

	static matrix_vector< T > standard_basis( size_t cols, size_t i ) {
		return matrix_vector< T >( cols ).set( i, T(1.0) );
	}

	////////////////////////////////////////////////////////////////////////////////////////////////////
	// Methods to access data in various syntax
	////////////////////////////////////////////////////////////////////////////////////////////////////
	operator std::vector<T>() {
		return row;
	}

	operator T() const {
		//assert( cols == 1 && "Attempt to retrieve scalar from multidimensional data." );
		return row[ 0 ];
	}

	T& operator[]( size_t index ) {
		return row[ index ];
	}

	const T& operator[]( size_t index ) const {
		return row[ index ];
	}

	matrix_vector< T >& set( size_t index, T val ) {
		row[ index ] = val;
		return *this;
	}

	////////////////////////////////////////////////////////////////////////////////////////////////////
	// Simple operations
	////////////////////////////////////////////////////////////////////////////////////////////////////
	matrix_vector< T > extend( const matrix_vector< T >& other ) const {
		matrix_vector< T > result( *this );
		result.row.insert( result.row.end(), other.row.begin(), other.row.end() );
		return result;
	}

	T dot_product( const matrix_vector< T >& other ) const {
		//assert( cols == other.cols && "Attempt to take dot product of vectors of different lengths." );

		T result( 0.0 );
		for( size_t col = 0; col < cols; ++col ) 
			result += row[col]*other[col];

		return result;
	}

	////////////////////////////////////////////////////////////////////////////////////////////////////
	// Friend operations
	////////////////////////////////////////////////////////////////////////////////////////////////////
	template< typename U, typename V >
	friend matrix_vector< U > operator *( const matrix_vector< U >& m, V scalar );

	template< typename U, typename V >
	friend matrix_vector< U > operator /( const matrix_vector< U >& m, V scalar );

	template< typename U >
	friend matrix_vector< U > operator +( const matrix_vector< U >& m1, const matrix_vector< U >& m2 );

	template< typename U >
	void operator +=( const matrix_vector< U >& m ) {
		(*this) = (*this) + m;
	}

	template< typename U >
	friend matrix_vector< U > operator -( const matrix_vector< U >& m1, const matrix_vector< U >& m2 );

	template< typename U >
	void operator -=( const matrix_vector< U >& m ) {
		(*this) = (*this) - m;
	}

	template< typename U >
	friend bool operator ==( const matrix_vector< U >& m1, const matrix_vector< U >& m2 );

	template< typename U >
	const T& operator =( const U& scalar ) {
		//assert( cols == 1 && "Attempt to assign scalar to multidimensional data." );
		(*this)[ 0 ] = scalar;
		return scalar;
	}
};

template< typename T, typename U >
matrix_vector< T > operator *( const matrix_vector< T >& m, U scalar ) {
	matrix_vector< T > result( m.cols );
	for( size_t col = 0; col < m.cols; ++col )
		result[ col ] = scalar*m[ col ];

	return result;
}

template< typename T, typename U >
matrix_vector< T > operator /( const matrix_vector< T >& m, U scalar ) {
	return m * (U(1.0) / scalar);
}

template< typename T >
matrix_vector< T > operator +( const matrix_vector< T >& m1, const matrix_vector< T >& m2 ) {
	//assert( m1.cols == m2.cols && "Attempt to add matrix vectors of unequal dimension." );

	matrix_vector< T > result( m1.cols );
	for( size_t col = 0; col < m1.cols; ++col )
		result[ col ] = m1[ col ] + m2[ col ];

	return result;
}

template< typename T >
matrix_vector< T > operator -( const matrix_vector< T >& m1, const matrix_vector< T >& m2 ) {
	//assert( m1.cols == m2.cols && "Attempt to subtract matrix vectors of unequal dimension." );

	matrix_vector< T > result( m1.cols );
	for( size_t col = 0; col < m1.cols; ++col )
		result[ col ] = m1[ col ] - m2[ col ];

	return result;
}

template< typename T >
bool operator ==( const matrix_vector< T >& m1, const matrix_vector< T >& m2 ) {
	if( m1.cols != m2.cols )	return false;
	for( size_t i = 0; i < m1.cols; ++i )	if( !matrix_eq<T>( m1[i], m2[i] ) )		return false;
	return true;
}

template< typename T >
class matrix {
protected:
	std::vector< matrix_vector<T> > data;

public:
	typedef T value_type;

	size_t rows, cols;
	matrix(): rows( 0 ), cols( 0 )
	{ }

	matrix( size_t rows_, size_t cols_ ): data( rows_, matrix_vector<T>( cols_ ) ), rows( rows_ ), cols( cols_ )
	{ }

	template< typename Iterator >
	static matrix<T> from_iterator( Iterator begin, Iterator end ) {
		matrix m;
		for( Iterator cur = begin; cur != end; ++ cur )		m.data.push_back( matrix_vector<T>( cur->begin(), cur->end() ) );
		return m;
	}

	template< typename Iterator, typename UnaryOperator >
	static matrix<T> from_iterator( Iterator begin, Iterator end, UnaryOperator op ) {
		matrix m;
		for( Iterator cur = begin; cur != end; ++ cur )		m.data.push_back( matrix_vector<T>( cur->begin(), cur->end(), op ) );
		return m;
	}

	template< typename Container >
	static matrix<T> from_container( Container c ) {
		return from_iterator( c.begin(), c.end() );
	}

	template< typename Container, typename UnaryOperator >
	static matrix<T> from_container( Container c, UnaryOperator op ) {
		return from_iterator( c.begin(), c.end(), op );
	}

	static matrix<T> column_matrix( size_t rows ) {
		return matrix<T>( rows, 1 );
	}

	static matrix<T> column_matrix( const matrix_vector<T>& vec ) {
		if( vec.cols == 0 )		return matrix<T>();
		return matrix<T>( vec.cols, 1 ).column( 0, vec );
	}

	template< typename Iterator >
	static matrix<T> column_from_iterator( Iterator first, Iterator last ) {
		return column_matrix( matrix_vector<T>( first, last ) );
	}

	
	template< typename Iterator, typename UnaryOperator >
	static matrix<T> column_from_iterator( Iterator first, Iterator last, UnaryOperator op ) {
		return column_matrix( matrix_vector<T>( first, last, op ) );
	}

	template< typename Container >
	static matrix<T> column_from_container( Container c ) {
		return column_from_iterator( c.begin(), c.end() );
	}

	template< typename Container, typename UnaryOperator >
	static matrix<T> column_from_container( Container c, UnaryOperator op ) {
		return column_from_iterator( c.begin(), c.end(), op );
	}

	static matrix<T> identity( size_t rows_, size_t cols_ ) {
		return matrix( rows_, cols_ );
	}


	////////////////////////////////////////////////////////////////////////////////////////////////////
	// Accessors to matrix data by row and by column
	////////////////////////////////////////////////////////////////////////////////////////////////////
	matrix_vector< T >& operator []( size_t row ) {
		return data[ row ];
	}

	const matrix_vector< T >& operator []( size_t row ) const {
		return data[ row ];
	}

	matrix_vector< T > column( size_t col ) const {
		matrix_vector<T> column( rows );
		for( size_t row = 0; row < rows; ++row )
			column[ row ] = data[ row ][ col ];

		return column;
	}

	matrix& column( size_t col, const matrix_vector<T>& column ) {
		for( size_t row = 0; row < rows; ++row )
			data[ row ][ col ] = column[ row ];
		return *this;
	}

	matrix_vector< T > row( size_t row ) const {
		return data[ row ];
	}

	matrix< T >& row( size_t r, const matrix_vector<T>& row ) {
		data[ r ] = row;
		return *this;
	}

	////////////////////////////////////////////////////////////////////////////////////////////////////
	// Simple operations
	////////////////////////////////////////////////////////////////////////////////////////////////////
	matrix< T > sub_matrix( size_t row_begin, size_t row_end, size_t col_begin, size_t col_end ) {
		matrix< T > result( row_end - row_begin, col_end - col_begin );
		for( size_t row = row_begin; row < row_end; ++row ) for( size_t col = col_begin; col < col_end; ++col )
			result[ row - row_begin ][ col - col_begin ] = (*this)[row][col];

		return result;
	}

	matrix< T > transpose() {
		matrix< T > result( cols, rows );
		for( size_t row = 0; row < rows; ++row )	result.column( row, data[ row ] );
		return result;
	}

	////////////////////////////////////////////////////////////////////////////////////////////////////
	// RREF and inverse operations
	////////////////////////////////////////////////////////////////////////////////////////////////////
	matrix< T > inverse() {
		//assert( rows == cols && "Attempt to invert non-square matrix." );

		matrix< T > extended( *this );
		for( size_t row = 0; row < rows; ++row ) {
			extended[ row ] = extended[ row ].extend( matrix_vector< T >::standard_basis( cols, row ) );
		}

		extended.cols += cols;
		matrix< T > rref_ext = extended.rref();

		return rref_ext.sub_matrix( 0, rows, rows, 2*rows );
	}

	matrix< T > rref() {

		matrix< T > result( *this );
		for( size_t row = 0; row < rows && row < cols; ++row ) {

			size_t best_row = row;

			float abs_val = matrix_abs( result[ row ][ row ] );
			T best_score = abs_val < T(1.0)? T(1.0) / abs_val: abs_val;

			for( size_t row_check = row+1; row_check < rows; ++row_check ) {

				float abs_val = matrix_abs( result[ row_check ][ row ] );
				float score = ( abs_val < T(1.0) )? T(1.0) / abs_val: abs_val;

				if( score < best_score )
					best_score = score, best_row = row_check;
			}

			if( matrix_abs( result[ best_row ][ row ] ) < T( 0.00001 ) )
				return matrix<T>( rows, cols );

			std::swap( result[ best_row ], result[ row ] );
			result[ row ] = result[ row ] / result[ row ][ row ];

			for( size_t row_change = 0; row_change < row; ++row_change ) {
				result[ row_change ] -= result[ row ] * result[ row_change ][ row ]; 
			}

			for( size_t row_change = row+1; row_change < rows; ++row_change ) {
				result[ row_change ] -= result[ row ] * result[ row_change ][ row ]; 
			}
		}

		return result;
	}

	////////////////////////////////////////////////////////////////////////////////////////////////////
	// Friend operators
	////////////////////////////////////////////////////////////////////////////////////////////////////
	template< typename U >
	friend matrix< U > operator *( const matrix< U >& m1, const matrix< U >& m2 );

	template< typename U >
	friend matrix< U > operator +( const matrix< U >& m1, const matrix< U >& m2 );

	template< typename U >
	void operator +=( const matrix< U >& m ) {
		(*this) = (*this) + m;
	}

	template< typename U >
	friend matrix< U > operator -( const matrix< U >& m1, const matrix< U >& m2 );

	template< typename U >
	void operator -=( const matrix< U >& m ) {
		(*this) = (*this) - m;
	}

	template< typename U >
	friend bool operator ==( const matrix< U >& m1, const matrix< U >& m2 );

	////////////////////////////////////////////////////////////////////////////////////////////////////
	// Conversion to string and output operators
	////////////////////////////////////////////////////////////////////////////////////////////////////
	template< typename U >
	friend std::ostream& operator <<( std::ostream& o, const matrix< U >& m );

	std::string to_string() const {

		std::stringstream o;
		o << "[";
		for( size_t row = 0; row < rows; ++row ) {
			for( size_t col = 0; col < cols; ++col )
				o << " " << data[ row ][ col ];
			o << ";";
		}

		o << " ]";
		return o.str();
	}
};

template< typename T >
matrix< T > operator *( const matrix< T >& m1, const matrix< T >& m2 ) {
	//assert( m1.cols == m2.rows && "Attempt to multiply matrices of incompatable dimensions." );

	matrix< T > result( m1.rows, m2.cols );
	for( size_t row = 0; row < m1.rows; ++row ) for( size_t col = 0; col < m2.cols; ++col )
		result[ row ][ col ] = m1[ row ].dot_product( m2.column( col ) );

	return result;
}

template< typename T >
matrix< T > operator +( const matrix< T >& m1, const matrix< T >& m2 ) {
	//assert( m1.rows == m2.rows && m1.cols == m2.cols && "Attempt to add matrices of incompatible dimensions." );

	matrix< T > result( m1.rows, m1.cols );
	for( size_t row = 0; row < m1.rows; ++row )
		result[row] = m1[row] + m2[row];

	return result;
}

template< typename T >
matrix< T > operator -( const matrix< T >& m1, const matrix< T >& m2 ) {
	//assert( m1.rows == m2.rows && m1.cols == m2.cols && "Attempt to subtract matrices of incompatible dimensions." );

	matrix< T > result( m1.rows, m1.cols );
	for( size_t row = 0; row < m1.rows; ++row )
		result[row] = m1[row] - m2[row];

	return result;
}

template< typename T >
bool operator ==( const matrix< T >& m1, const matrix< T >& m2 ) {
	if( m1.rows != m2.rows )	return false;
	for( size_t i = 0; i < m1.rows; ++i )	if( m1[i] != m2[i] )	return false;
	return true;
}

template< typename T >
std::ostream& operator <<( std::ostream& o, const matrix< T >& m ) {
	o << m.to_string();
	return o;
}

#endif
