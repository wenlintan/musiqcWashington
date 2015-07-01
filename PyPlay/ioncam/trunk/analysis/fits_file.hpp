
#pragma once
#include <string>

#include "fitsio.h"

#include "image.hpp"

template< typename T >
struct CFitsIOTypeMap {
	const static int image_type;
	const static int data_type;
};

int CFitsIOTypeMap< float >::image_type = FLOAT_IMG;
int CFitsIOTypeMap< short >::data_type = TFLOAT;

int CFitsIOTypeMap< short >::image_type = SHORT_IMG;
int CFitsIOTypeMap< short >::data_type = TSHORT;

struct FitsFile {
	std::string filename;
	FitsFits( const std::string filename_ ): filename( filename_ )
	{}

	template< typename T >
	Image<T> load_image() {

	}

	template< typename T >
	void save_image( const Image<T>& image ) {
		typedef CFitsIOTypeMap< T > map;
		save_image( map::image_type, map::data_type, image.ptr() );
	}
	
	void load_image( void* data, int image_type, int data_type ) const;
};
