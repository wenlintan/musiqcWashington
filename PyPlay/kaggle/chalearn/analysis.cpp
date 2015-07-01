
#include "analysis.hpp"
#include "utils.hpp"

#include <iostream>
#include <fstream>
#include <algorithm>

using namespace CL;


Analyzer::Analyzer( 
		const std::string& n,
		const Analyzer::FileList_t example_files, 
		const Analyzer::FileList_t tests ): name( n ) {

	cv::Mat data;
	MotionHistory mh;
	MeanBackgroundRemover bg;

	std::cout << "Loading examples." << std::endl;
	for( FileList_t::const_iterator i = example_files.begin(); 
		i != example_files.end(); 
		++i ) {

		std::cout << *i << std::endl;

		cv::VideoCapture cv( *i );
		starts.push_back( examples.size() );

		while( cv.grab() && cv.retrieve( data ) ) {
			cv::Mat cdata = data.clone();
			examples.push_back( mh( bg( cdata ) ) );
		}
	}
	starts.push_back( examples.size() );

	std::cout << "Analyzing examples." << std::endl;
	principle_components();

	std::vector< cv::Mat > test;
	std::ofstream f( (n + ".txt").c_str() );
	for( FileList_t::const_iterator i = tests.begin();
		 i != tests.end();
		 ++i ) {

		test.resize( 0 );
		cv::VideoCapture cv( *i );
		while( cv.grab() && cv.retrieve( data ) ) {
			cv::Mat cdata = data.clone();
			test.push_back( mh( bg( cdata ) ) );
		}

		std::vector<size_t> gestures = time_warp_pca( test );
		f << *i << std::endl;
		
		if( gestures.size() ) {
			for( size_t j = 0; j < gestures.size()-1; ++j )
				f << gestures[ j ] << ", ";
			f << gestures[ gestures.size() -1 ] << std::endl;
		} else {
			f << "No gestures." << std::endl;
		}
	}
}

void dfs( PoseElement& p, cv::Mat& m ) {
	float w = m.cols, h = m.rows;
	cv::Point pt( (p.position.x / p.position.z)*w + w/2.,
		(p.position.y / p.position.z)*h + h/2. );

	std::cout << p.position << std::endl;
	std::cout << pt << std::endl;
	cv::circle( m, pt, 4, cv::Scalar( 255, 0, 0, 0 ) );
	for( size_t i = 0; i < p.children.size(); ++i )
		dfs( p.children[i], m );
}

void Analyzer::principle_components() {

	if( !examples.size() )
		throw "No examples.";

	std::cout << "Estimating pose." << std::endl;
	PoseEstimator pe;
	cv::VideoWriter vw( "test.mpg", 
		CV_FOURCC('P', 'I', 'M', '1'), 24.0, examples[0].size() );

	std::cout << "Created video." << std::endl;
	float w = examples[0].cols, h = examples[0].rows;
	for( size_t i = 0; i < examples.size(); ++i ) {
		Pose p = pe( examples[i] );
		std::cout << "Drawing pose." << std::endl;

		cv::Point pt( (p.position.x / p.position.z)*w + w/2.,
			(p.position.y / p.position.z)*h + h/2. );
		std::cout << pt << std::endl;

		cv::circle( examples[i], pt, 4, cv::Scalar( 255, 0, 0, 0 ) );
		dfs( p.root, examples[i] );	
		vw.write( examples[i] );
	}

	size_t row_length = 3 * examples[0].rows * examples[0].cols;
	cv::Mat data( 0, row_length, examples[0].type() );
	
	std::cout << "Reshaping." << std::endl;
	for( size_t i = 0; i < examples.size(); ++i )
		data.push_back( examples[i].reshape( 1, 1 ) );
	std::cout << data.rows << ", " << data.channels() << std::endl;

	size_t nvectors = starts.size() * 3;	
	pca = cv::PCA( data, cv::Mat(), CV_PCA_DATA_AS_ROW, nvectors );
	std::cout << "PCA'ing." << std::endl;

	for( size_t i = 0; i < nvectors; ++i ) {
		cv::Mat evec_out;
		cv::Mat evec = pca.eigenvectors.row(i)
			.reshape(3, examples[0].rows);
		cv::normalize( evec, evec_out, 0., 255., cv::NORM_MINMAX );
		std::cout << "Writing." << std::endl;

		std::stringstream ss;
		ss << i;
		cv::imwrite( name + "_evec" + ss.str() + ".png", evec_out );
	}

	cv::Mat sample = data.row(0).reshape( 3, examples[0].rows );
	cv::imwrite( name + "_sample.png", sample );

	size_t position = 0;
	for( size_t i = 1; i < starts.size(); ++i ) {
		cv::Mat example_features( 0, nvectors, examples[0].type() );
		while( position != starts[ i ] ) {
			cv::Mat pca_key;
			pca.project( examples[ position++ ].reshape( 1, 1 ), pca_key );
			example_features.push_back( pca_key );
		}

		pca_features.push_back( example_features );
	}

	std::cout << "Done analyzing." << std::endl;
}

std::vector<size_t> Analyzer::time_warp_pca( const std::vector<cv::Mat>& data ) {
	if( data.size() < 2 )
		return std::vector<size_t>();

	std::vector< cv::Mat > pca_data;
	std::cout << "Projecting data." << std::endl;
	for( size_t i = 0; i < data.size(); ++i ) {
		cv::Mat pca_temp;
		pca.project( data[ i ].reshape( 1, 1 ), pca_temp );
		pca_data.push_back( pca_temp );
	}

	cv::Mat comp_elem( data.size(), data.size(), CV_64F );
	std::vector< cv::Mat > components;

	const unsigned char SKIP_DATA = 240, SKIP_TRAIN = 242, DEFAULT = 243;
	cv::Mat trace_elem( data.size(), data.size(), CV_8U, DEFAULT );
	std::vector< cv::Mat > trace;

	for( size_t i = 0; i < pca_features.size(); ++i ) {
		components.push_back( comp_elem.clone() );
		trace.push_back( trace_elem.clone() );
	}

	const double skip_penalty = 8000., accept_penalty = 8000.;

	std::cout << "Initializing start data." << std::endl;
	for( size_t g = 0; g < pca_features.size(); ++g ) {
		for( size_t i = 0; i < data.size(); ++i ) {
			size_t ri = i % pca_features[ g ].rows;
			double n = cv::norm( pca_data[0], pca_features[g].row(ri) );  
			components[ g ].at< double >( 0, i ) = n + i * skip_penalty;

			n = cv::norm( pca_data[i], pca_features[g].row(0) );
			components[ g ].at< double >( i, 0 ) = n + i * skip_penalty;
		}
	}

	std::cout << "Completing matrix." << std::endl;

	for( size_t i = 1; i < data.size(); ++i ) {
		for( size_t j = 1; j < data.size(); ++j ) {
			for( size_t g = 0; g < pca_features.size(); ++g ) {
					size_t r = j % pca_features[ g ].rows;
					double n = cv::norm( pca_data[i], pca_features[g].row(r) );	
					n += components[ g ].at< double >( i-1, j-1 );
					
					trace[ g ].at< unsigned char >( i, j ) = DEFAULT;

					double newn = components[ g ].at< double >( i-1, j );
					if( newn + skip_penalty < n ) {
						trace[ g ].at< unsigned char >( i, j ) = SKIP_TRAIN;
						n = newn + skip_penalty;
					}

					newn = components[ g ].at< double >( i, j-1 );
					if( newn + skip_penalty < n ) {
						trace[ g ].at< unsigned char >( i, j ) = SKIP_DATA;
						n = newn + skip_penalty;
					}

					components[ g ].at< double >( i, j ) = n;
			}

			for( size_t gi = 0; gi < pca_features.size(); ++gi ) {
				for( size_t gj = 0; gj < pca_features.size(); ++gj ) {
					if( j % pca_features[ gj ].rows == 0 ) {
						double n = components[ gi ].at< double >( i, j );
						double newn = components[ gj ].at< double >( i, j );
						if( newn + accept_penalty < n ) {
							components[ gi ].at< double >( i, j ) = 
								newn + accept_penalty;
							trace[ gi ].at< unsigned char >( i, j ) = gj;
						}
					}
				}
			}
		}
	}

	std::cout << "Tracing path." << std::endl;
	std::vector<size_t> result;

	double b = 1.e100;
	size_t g = 0, i = data.size()-1, j = data.size()-1;
	for( size_t gi = 0; gi < pca_features.size(); ++gi )
		if( components[ gi ].at<double>( i, j ) < b ) {
			b = components[ g ].at<double>( i, j );
			g = gi;
		} 

	result.push_back( g );
	while( i && j ) {
		std::cout << i << ", " << j << ", " << g << std::endl;
		std::cout << components[ g ].at< double >( i, j ) 
			<< " " << trace[ g ].at<unsigned char>( i, j ) << std::endl;

		unsigned char t = trace[ g ].at< unsigned char >( i, j );
		if( t == SKIP_TRAIN )	--i;
		else if( t == SKIP_DATA )	--j;
		else if( t == DEFAULT ) {
			--i; --j;
		} else {
			result.push_back( t );
			g = t;
		}
	}	

	std::cout << "Done tracing." << std::endl;
	std::reverse( result.begin(), result.end() );
	return result;
}


