
#include <cmath>
#include <numeric>
#include <stack>

#include <string>
#include <iostream>

#include "linear_fit.hpp"
#include "ion_detector.hpp"

#include "boost/assign/list_of.hpp"

#include "fitsio.h"

template< typename T >
struct CFitsIOTypeMap {};
template<> struct CFitsIOTypeMap<float> { 
	const static int image_type = FLOAT_IMG;
	const static int type = TFLOAT; 
};
template<> struct CFitsIOTypeMap<short> { 
	const static int image_type = SHORT_IMG;
	const static int type = TSHORT; 
};

image_type load_file( const std::string& filename ) {
	fitsfile* f;
	int status = 0, naxis;

	fits_open_file( &f, filename.c_str(), READONLY, &status );
	fits_get_img_dim( f, &naxis, &status );
	if( naxis != 2 && naxis != 3 ) {
		std::cout << "Could not read image" << std::endl;
		fits_close_file( f, &status );
		return image_type();
	}

	long dim[3];
	dim[0] = dim[1] = dim[2] = 0;
	fits_get_img_size( f, 3, dim, &status );

	image_type data( image_type::extents_type( dim[0], dim[1] ) );
	typedef CFitsIOTypeMap< image_type::element > map;

	int any_null;
	unsigned short null = 0;
	fits_read_img( f, map::type, 1, data.num_elements(), &null, data.ptr(),
		&any_null, &status );

	fits_close_file( f, &status );
	if( status ) {
		fits_report_error( stderr, status );
		return image_type();
	}		

	return data;
}

void save_file( const std::string& filename, const image_type& img ) {
	fitsfile* f;
	int status = 0;

    std::string fname = "!" + filename;
	fits_create_file( &f, fname.c_str(), &status );
	
	long dims[2];
	dims[0] = img.extents.first;	dims[1] = img.extents.second;

	typedef CFitsIOTypeMap<	image_type::element > map;
	fits_create_img( f, map::image_type, 2, dims, &status );
	fits_write_img( f, map::type, 1, img.num_elements(), 
		(void*)img.ptr(), &status );
        
    fits_close_file( f, &status );

	if( status ) {
		fits_report_error( stderr, status );
	}
}

Kernel Kernel::gaussian( size_t kern_size, float sigma ) {
	int k = (int)kern_size;

	image_type img( image_type::extents_type( 2*k+1, 2*k+1 ) );
	for( int i = -k; i <= k; ++i )
	for( int j = -k; j <= k; ++j ) {
		img( i+k, j+k ) = std::exp( -(i*i + j*j) / 2 / sigma / sigma );
	}
	
	Kernel result( img );
	result.normalize();
	return result;
}

Kernel Kernel::LoG( size_t kern_size, float sigma ) {
	int k = (int)kern_size;

	image_type img( image_type::extents_type( 2*k+1, 2*k+1 ) );
	for( int i = -k; i <= k; ++i )
	for( int j = -k; j <= k; ++j ) {
		img( i+k, j+k ) = -1 / 3.141592654 / sigma / sigma / sigma / sigma *
			( (i*i + j*j) / 2/ sigma / sigma - 1 )*
			std::exp( -(i*i + j*j) / 2 / sigma / sigma );
	}
	
	Kernel result( img );
	result.zero_center();
	return result;
}

void Kernel::normalize() {
	int k = kernel.extents.first / 2;
	float sum = std::accumulate( kernel.ptr(), 
		kernel.ptr()+kernel.num_elements(), 0. );

	for( int i = -k; i <= k; ++i )
	for( int j = -k; j <= k; ++j ) {
		kernel( i+k, j+k ) /= sum;
	}
}

void Kernel::zero_center() {
	int k = kernel.extents.first / 2;
	float sum = std::accumulate( kernel.ptr(), 
		kernel.ptr()+kernel.num_elements(), 0. );

	for( int i = -k; i <= k; ++i )
	for( int j = -k; j <= k; ++j ) {
		kernel( i+k, j+k ) -= sum / (2*k+1) / (2*k+1);
	}
}

edge_image_type IonDetector::canny_edge( const image_type& img ) {
	image_type::extents_type three( 3, 3 );
	Kernel gaussian( image_type( three, boost::assign::list_of
		( 1./16 )( 2./16 )( 1./16 )
		( 2./16 )( 4./16 )( 2./16 )
		( 1./16 )( 2./16 )( 1./16 ) ) );
	Kernel sobelx( image_type( three, boost::assign::list_of
		(1)(0)(-1)(2)(0)(-2)(1)(0)(-1) ) );
	Kernel sobely( image_type( three, boost::assign::list_of
		(1)(2)(1)(0)(0)(0)(-1)(-2)(-1) ) );

	image_type img_gauss( img.extents ), img_sobelx( img.extents ),
		img_sobely( img.extents );

	//gaussian.apply_kernel( img, img_gauss );
	sobelx.apply_kernel( img, img_sobelx );
	sobely.apply_kernel( img, img_sobely );

	save_file( "orig.fits", img );
	//save_file( "gauss.fits", img_gauss );
	//save_file( "sobelx.fits", img_sobelx );
	//save_file( "sobely.fits", img_sobely );

	image_type img_sobel( img_sobelx.extents );
	edge_image_type edges( img_sobelx.extents );

	image_type::element mean = 0, std_dev = 0;
	for( image_type::index i = 2; i < img_sobelx.extents.first-2; ++i ) 
	for( image_type::index j = 2; j < img_sobelx.extents.second-2; ++j ) {
		image_type::element val = img_sobelx( i, j )*img_sobelx( i, j ) +
			img_sobely( i, j )*img_sobely( i, j );
		img_sobel( i, j ) = val;
		mean += val;
	}

	save_file( "sobel.fits", img_sobel );
	
	mean /= img_sobel.num_elements();	
	for( image_type::index i = 2; i<img_sobelx.extents.first-2; ++i ) 
	for( image_type::index j = 2; j<img_sobelx.extents.second-2; ++j ) {
		std_dev += ( img_sobel( i, j ) - mean )*
			( img_sobel( i, j ) - mean );
	}
			
	std_dev = sqrt(std_dev / img_sobel.num_elements());
	image_type::element thresh = mean + canny_threshold * std_dev;
	image_type::element continue_thresh = mean + 
		canny_continue_threshold * std_dev;

	// First mark off edges with a high threshold
	for( image_type::index i = 2; i<img_sobelx.extents.first-2; ++i ) 
	for( image_type::index j = 2; j<img_sobelx.extents.second-2; ++j ) {
		edge_image_type::position pos( i, j );
		if( edges( pos ) ) continue;
		if(	canny_check( img_sobel, img_sobelx, img_sobely, 
				pos, thresh ) ) {
			std::stack< image_type::position > checks;
			checks.push( pos );

			while( !checks.empty() ) {
				pos = checks.top();
				checks.pop();

				if( edges( pos ) ) continue;
				if( !canny_check( img_sobel, img_sobelx, img_sobely, 
						pos, continue_thresh ) ) 
					continue;

				edges( pos ) = 1.0f;
				pos.first++;	checks.push( pos );
				pos.second++;	checks.push( pos );
				pos.second-=2;	checks.push( pos );
				pos.first--;	checks.push( pos );
				pos.second+=2;	checks.push( pos );
				pos.first--;	checks.push( pos );
				pos.second--;	checks.push( pos );
				pos.second--;	checks.push( pos );
			}
		}
	}

		
	save_file( "edges.fits", edges );
	return edges;
}

IonDetector::result_type IonDetector::hough_transform( image_type& edges ) {
	const unsigned short num_radii = 4;

	std::vector< unsigned short > hough( 
		edges.num_elements()*num_radii, 0 );

	for( size_t r = 2; r < 6; ++r ) 
	for( image_type::index i = r+1; i<edges.extents.first-r-1; ++i ) 
	for( image_type::index j = r+1; j<edges.extents.second-r-1; ++j ) {
		if( edges( i, j ) ) {
			for( float theta = 0.; theta < 6.3; theta += 1. / r ) {
				size_t x = (size_t)( i + (float)r*cos( theta ) + 0.5f);
				size_t y = (size_t)( j + (float)r*sin( theta ) + 0.5f);
				hough[ (r-2)*edges.num_elements() +
					y*edges.extents.first + x ]++;
			}
		}
	}
		
	result_type results;
	for( size_t r = 5; r >= 2; --r )
	for( image_type::index i = 8; i < edges.extents.first-8; ++i ) 
	for( image_type::index j = 8; j < edges.extents.second-8; ++j ) {
		size_t index = (r-2)*edges.num_elements() + 
			j*edges.extents.first + i;
		const unsigned short value = hough[index];
		if( value > (size_t)(hough_threshold * r) ) {
			size_t h = 0;
			for( ;  h < results.size(); ++h ) {
				size_t xsq = (i - results[h].x)*(i - results[h].x);
				size_t ysq = (j - results[h].y)*(j - results[h].y);
				if( xsq + ysq < 36 ) break;
			}
			
			if( h != results.size() ) continue;
			if( hough[index + edges.extents.first] > value ) continue;
			if( hough[index - edges.extents.first] > value ) continue;
			if( hough[index - 1] > value ) continue;
			if( hough[index + 1] > value ) continue;

			results.push_back( IonData( i, j, r ) );
			std::cout<< "Circle " << i << " " << j << " " << r << std::endl;
			std::cout<< value << std::endl;
		}
	}
	
	return results;
}

IonDetector::image_type IonDetector::hot_pixels( const image_type& img ) {
	image_type result( img );

	for( image_type::index i = 1; i < img.extents.first-1; ++i ) 
	for( image_type::index j = 1; j < img.extents.second-1; ++j ) {
		if( result( i, j ) > result( i-1, j ) / 2.5 &&
			result( i, j ) > result( i+1, j ) / 2.5 &&
			result( i, j ) > result( i, j-1 ) / 2.5 &&
			result( i, j ) > result( i, j+1 ) / 2.5 )

			result( i, j ) = ( result(i-1, j) + result(i+1, j) +
				result(i, j-1) + result( i, j+1) ) / 4;		
	}
	return result;
}

IonDetector::result_type IonDetector::blob_detector( const image_type& img ) {
	Kernel logs[3];
	float sigmas[3];

	logs[0] = Kernel::LoG( 4, 0.6 );
	sigmas[0] = 0.85;

	logs[1] = Kernel::LoG( 6, 1.0 );
	sigmas[1] = 1.0;

	logs[2] = Kernel::LoG( 20, 5.0 );
	sigmas[2] = 2.;

	image_type img_result( img.extents );
	result_type results;

	const size_t hsize = 2000;
	std::vector< size_t > histogram( hsize, 0 );

	size_t g = 2;
	logs[g].apply_kernel( img, img_result );
	save_file( "log.fits", img_result );

	float img_max = *std::max_element( img_result.ptr(), 
		img_result.ptr() + img.num_elements() );
	for( 	float* iter = img_result.ptr(); 
			iter != img_result.ptr() + img.num_elements(); 
			++iter ) {

		int p = (size_t)( ( *iter + img_max ) / 2 / img_max * hsize ); 
		if( p >= (int)hsize ) 	p = hsize-1;
		if( p < 0 )				p = 0;
		histogram[ p ] ++;
	}

	size_t nelems = 0, counter = hsize-1;
	while( nelems < (size_t)blob_threshold )
		nelems += histogram[ counter-- ];

	float thresh = (float)counter / hsize * img_max - img_max / 2.;
	for( image_type::index i = 12; i < img.extents.first-12; ++i ) 
	for( image_type::index j = 12; j < img.extents.second-12; ++j ) {
		if( img_result( i, j ) > thresh &&
			img_result( i, j ) > img_result( i+1, j ) &&
			img_result( i, j ) > img_result( i-1, j ) &&
			img_result( i, j ) > img_result( i, j+1 ) &&
			img_result( i, j ) > img_result( i, j-1 ) &&
			img_result( i, j ) > img_result( i+1, j+1 ) &&
			img_result( i, j ) > img_result( i+1, j-1 ) &&
			img_result( i, j ) > img_result( i-1, j+1 ) &&
			img_result( i, j ) > img_result( i-1, j-1 ) ) {

			results.push_back( IonData( i, j, sigmas[g] ) );
		}
	}

	return results;
}


IonDetector::result_type IonDetector::gaussian_fit( 
		const image_type& img, result_type& data ) {

	return data;
	result_type new_results;
	for( size_t d = 0; d < data.size(); ++d ) {
		int r = (int)( data[d].r + 0.5f );
		vector< float > fitx( (size_t)(r*2+5), 0.f );
		vector< float > fity( (size_t)(r*2+5), 0.f );

		size_t x = data[d].x, y = data[d].y;
		for( int i = -r-2; i <= r+2; ++i )
		for( int j = -r-2; j <= r+2; ++j ) {
			fitx[i + r+2] += img( i + x, j + y );
			fity[j + r+2] += img( i + x, j + y );
		}			

		vector< float > xparams( 4, 0. );
		xparams( 0 ) = r+2;				// mean
		xparams( 1 ) = r;				// sigma
		xparams( 2 ) = fitx( r+2 );		// ampl
		xparams( 3 ) = fitx( 0 );		// base
		vector< float > yparams( xparams );

		FitFunction< GaussianFunction<float> > fitter;
		if( fitter( fitx, xparams ) < 0 || fitter( fity, yparams ) < 0 )
			continue;

		new_results.push_back( IonData(
			data[d].x + -r-2 + xparams( 0 ),
			data[d].y + -r-2 + yparams( 0 ),
			( xparams(1) + yparams(1) ) / 2. ) );
	}
    
    return new_results;
}

struct CompareSecond {
	bool operator ()( const std::pair<size_t, IonData>& lhs,
		const std::pair<size_t, IonData>& rhs ) const {
		return lhs.second < rhs.second;
	}
};

int main( int argc, char** argv ) {
	if( argc < 6 || argc & 1) {
		std::cout << "usage: " << argv[0] 
			<< " <threshold> <nions> <nbright> [<n> <template> ...]" 
			<< std::endl;
		return -1;
	}

	size_t threshold = 0, nimages = 0, nions = 0, nbright = 0;
	std::stringstream s( argv[1] );
	s >> threshold;

	std::stringstream s3( argv[2] );
	s3 >> nions;

	std::stringstream s4( argv[3] );
	s4 >> nbright;

	std::vector<IonDetector::result_type> res;

	size_t argc_i = 4;
	while( argc_i < argc ) {
	std::stringstream s2( argv[argc_i++] );
	s2 >> nimages;
	for( size_t i = 0; i < nimages; ++i ) {

		char image_name[1024];
		sprintf( image_name, argv[argc_i], i );

		image_type data = load_file( image_name );
		if( !data.extents.first ) { 	// Failed to load image
			return -1;
		}
		
		IonDetector det;
		det.blob_threshold = threshold;
		image_type result = det.hot_pixels( data );
		save_file( "hot.fits", result );

		IonDetector::result_type results = det( result );
		res.push_back( results );
		
		if( results.size() > nbright ) {
			std::cout << "Too many ions in: " << image_name << std::endl;
		} else if( results.size() < nbright ) {
			std::cout << "Too few ions in: " << image_name << std::endl;
		}

	}
	++argc_i;
	}

	std::vector< std::pair< size_t, IonData > > positions;
	for( size_t i = 0; i < res.size(); ++i ) {
		if( res[i].size() != nbright )
			continue;

		for( size_t ion = 0; ion < res[i].size(); ++ion ) {
			size_t pos = 0;
			for( ; pos < positions.size(); ++pos ) {
				if( fabs( positions[pos].second.x - res[i][ion].x ) < 6 &&
					fabs( positions[pos].second.y - res[i][ion].y ) < 6 ) {
					++ positions[pos].first;
					break;
				}
			}
			if( pos == positions.size() )
				positions.push_back( std::make_pair( 1, res[i][ion] ) );
		}
	}

	std::sort( positions.begin(), positions.end() );
	std::reverse( positions.begin(), positions.end() );
	if( positions.size() > nions )
		positions.resize( nions );

	std::sort( positions.begin(), positions.end(), CompareSecond() );
	std::cout << "Detected ion locations: " << std::endl;
	for( size_t i = 0; i < positions.size(); ++i ) {
		std::cout << positions[i].second.x << ", " << positions[i].second.y
			<< std::endl;
	}

	std::cout << std::endl;
	std::cout << "Ion patterns: " << std::endl;
	std::vector< std::string > bits;
	for( size_t i = 0; i < res.size(); ++i ) {
		bits.push_back( "" );
		for( size_t pos = 0; pos < positions.size(); ++pos ) {
			size_t ion = 0;
			for( ; ion < res[i].size(); ++ion ) {
				if( fabs( positions[pos].second.x - res[i][ion].x ) < 6 &&
					fabs( positions[pos].second.y - res[i][ion].y ) < 6 ) {
					bits.back() += "1";
					break;
				}
			}

			if( ion == res[i].size() )
				bits.back() += "0";
		}

		std::cout << i << ":\t" << bits.back() << std::endl;
	}	

	size_t reorder = 0;
	std::string order = bits[0];
	for( size_t i = 1; i < bits.size(); ++i ) {
		if( bits[i] != order ) {
			++reorder;
			order = bits[i];
		}	
	}
	
	std::cout << "Reordered " << reorder << " times." << std::endl;
	std::cout << "Probability: " << (float)reorder / (nimages-1) << std::endl;
	return 0;
}

