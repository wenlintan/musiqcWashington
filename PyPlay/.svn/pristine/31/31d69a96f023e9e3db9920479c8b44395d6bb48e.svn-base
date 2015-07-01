
#pragma once

#include <iostream>
#include <vector>

#include "image.hpp"

struct Kernel {
	typedef Image< float > image_type;
	image_type kernel;

	Kernel() {}
	Kernel( image_type kern ): kernel( kern )
	{}

	static Kernel gaussian( size_t kernel_radius, float sigma );
	static Kernel LoG( size_t kernel_radius, float sigma );

	void normalize();
	void zero_center();

	void operator()( const image_type& img, image_type& out ) {
		apply_kernel( img, out );
	}

	void apply_kernel( const image_type& img, image_type& out ) {
		image_type::index i, j;
		char oi, oj, offi = kernel.extents.first/2, 
			offj = kernel.extents.second/2;

		for( i = offi; i < img.extents.first - offi; ++i )
		for( j = offj; j < img.extents.second - offj; ++j ) {
			for( oi = -offi; oi <= offi; ++oi ) 
			for( oj = -offj; oj <= offj; ++oj ) {
				out(i,j) += img(i+oi, j+oj) * kernel(offi+oi, offj+oj);
			}
		}
	}

};

struct IonData {
	float x, y, r;
	IonData(): x( 0.f ), y( 0.f ), r( 1.f )
	{}

	IonData( float x_, float y_, float r_ ): x( x_ ), y( y_ ), r( r_ )
	{}

	bool operator <( const IonData& rhs ) const {
		return x < rhs.x;
	}
};

struct IonDetector {
	typedef Image< float > image_type;
	typedef Image< float > edge_image_type;
	typedef std::vector< IonData > result_type;

	float canny_threshold, canny_continue_threshold;
	float hough_threshold;
    float blob_threshold;

	IonDetector(): canny_threshold( 4.f ), canny_continue_threshold( 1.f ),
		hough_threshold( 4.f ), blob_threshold( 10.f )
	{}

	result_type operator()( const image_type& img ) {
		//edge_image_type edges = canny_edge( img );
		//result_type result = hough_transform( edges );
		result_type result = blob_detector( img );
		return gaussian_fit( img, result );
	}
		
	result_type operator()( const Image<unsigned short>& raw_data ) {
		image_type data( raw_data.extents );
		std::copy( raw_data.ptr(), 
			raw_data.ptr()+raw_data.num_elements(), 
			data.ptr() );
		return (*this)( data );
	}

	inline bool canny_check( const image_type& mag, const image_type& x, 
		const image_type& y, const image_type::position pos, 
		const float threshold ) {

		float size = mag( pos );
		if( size < threshold )	return false;

		float angle = atan2( y(pos), x(pos) );
		if( angle < 0 ) angle += 3.141592654f;

		image_type::position compare1( pos ), compare2( pos );
		if( angle < 1*3.141592/8 ) {
			compare1.first++, compare2.first--;
		} else if( angle < 3*3.141592/8 ) {
			compare1.first++, compare1.second++;
			compare2.first--, compare2.second--;
		} else if( angle < 5*3.141592/8 ) {
			compare1.second++, compare2.second--;
		} else if( angle < 7*3.141592 ) {
			compare1.first--, compare1.second++;
			compare2.first++, compare2.second--;
		} else {
			compare1.first++, compare2.first--;
		}

		if( size > mag( compare1 ) && size > mag( compare2 ) )
			return true;
		return false;
	}

	edge_image_type canny_edge( const image_type& img );
	result_type hough_transform( image_type& edges );

	result_type blob_detector( const image_type& img );
	image_type hot_pixels( const image_type& img );

	result_type gaussian_fit( const image_type& img, result_type& data );
};

