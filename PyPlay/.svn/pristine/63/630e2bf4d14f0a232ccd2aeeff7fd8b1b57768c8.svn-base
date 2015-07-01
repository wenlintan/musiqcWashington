
#include "utils.hpp"

using namespace CL;

const double MeanBackgroundRemover::cutoff_sigma = 0.;
cv::Mat& MeanBackgroundRemover::operator()( cv::Mat& mat ) {
	cv::Scalar mean, std_dev;
	cv::meanStdDev( mat, mean, std_dev );

	cv::Mat mask = mat < (mean.val[0] + std_dev.val[0] * cutoff_sigma);

	cv::Mat result( mat.size(), mat.type(), 255.f );
	mat.copyTo( result, mask );
	return mat = result;
}

const double MotionHistory::decay = 0.8;
MotionHistory::MotionHistory():
	norm( 0. ), buffer_index( 0 ), setup_run( false ) { }

void MotionHistory::setup( cv::Mat& data ) {
	double cur_decay = 1.;
	for( size_t i = 0; i < buffer_size; ++i ) {
		buffer.push_back( data.clone() );
		norm += cur_decay;
		cur_decay *= decay;
	}

	setup_run = true;
}

cv::Mat& MotionHistory::operator()( cv::Mat& data ) {
	if( !setup_run )
		setup( data );

	buffer[ buffer_index ] = data.clone();
	buffer_index = (buffer_index+1) % buffer_size;

	data *= (1. / norm);
	double cur_decay = 1.;

	for( size_t i = buffer_index;
		i != (buffer_index-1) % buffer_size;
		i = (i+1) % buffer_size ) {

		cur_decay *= decay;
		data += buffer[ i ] * cur_decay / norm;
	}

	return data;
}

void PoseElement::rotate( const cv::Point3f& drot ) {
	rotation += drot;
	transform = 
		( cv::Mat_<float>( 4, 4 ) <<
			cos( rotation.z ), sin( rotation.z ), 0., 0.,
			-sin( rotation.z ), cos( rotation.z ), 0., 0.,
			0., 0., 1., 0.,
			0., 0., 0., 1. ) *
		( cv::Mat_<float>( 4, 4 ) <<
			cos( rotation.y ), 0., sin( rotation.y ), 0.,
			0., 1., 0., 0.,
			-sin( rotation.y ), 0., cos( rotation.y ), 0.,
			0., 0., 0., 1. ) *
		( cv::Mat_<float>( 4, 4 ) <<
			cos( rotation.x ), sin( rotation.x ), 0., 0.,
			-sin( rotation.x ), cos( rotation.x ), 0., 0.,
			0., 0., 1., 0.,
			0., 0., 0., 1. );
		
	child_transform = 
		transform * ( cv::Mat_<float>( 4, 4 ) <<
			1., 0., 0., 0.,
			0., 1., 0., 0.,
			0., 0., 1., length,
			0., 0., 0., 1. );
}

cv::Mat& PoseElement::draw( cv::Mat parent_transform, cv::Mat& mat ) {
	cv::Mat_<float> p = ( cv::Mat_<float>( 4, 1 ) << 0., 0., 0., 1. );
	p = parent_transform * child_transform * p;
	position = cv::Point3f( p(0, 0), p(1, 0), p(2, 0) );

	float r = float(mat.rows), c = float(mat.cols);
	for( size_t i = 0; i < point_cloud.size(); ++i ) {
		cv::Point3f& pt = point_cloud[i];
		p = ( cv::Mat_<float>( 4, 1 ) << pt.x, pt.y, pt.z, 1 );
		p = parent_transform * transform * p;

		cv::Point3f new_pt( p(0, 0), p(1, 0), p(2, 0) );
		int rpos = int( r * new_pt.y / new_pt.z + r / 2 );
		int cpos = int( c * new_pt.x / new_pt.z + c / 2 );
		float d = cv::norm( new_pt );

		if( rpos > 0 && rpos < r && cpos > 0 && cpos < c )
			if( mat.at< float >( rpos, cpos ) > d )
				mat.at< float >( rpos, cpos ) = d; 
	}	

	for( size_t i = 0; i < children.size(); ++i ) {
		children[i].draw( parent_transform * child_transform, mat );
	}

	return mat;
}

bool PoseElement::estimate_gradient( size_t param ) {
	float drot = 0.1f;
	const cv::Point3f drots[3] = {
		cv::Point3f( drot, 0.f, 0.f ),
		cv::Point3f( 0.f, drot, 0.f ),
		cv::Point3f( 0.f, 0.f, drot ) };

	std::cout << position << ", " << rotation << std::endl;
	if( param && param < 4 ) 	rotate( -drots[ param-1 ] );
	if( param < 3 )	{
		child = 0;
		offset = 3;
		rotate( drots[ param ] );
	} else {
		if( !children.size() )	return true;
		if( children[ child ].estimate_gradient( param - offset ) ) {
			child++;
			offset = param;
			if( child >= children.size() ) 
				return true;
			children[ child ].estimate_gradient( 0 );
		}

	}

	return false;
}

size_t PoseElement::update_gradient( cv::Mat& mat, size_t param ) {
	cv::Mat_<float> delta( mat );
	cv::Point3f drot( delta( param, 0 ), 
		delta( param+1, 0 ), delta( param+2, 0 ) );
	rotate( drot );

	param += 3;
	for( size_t c = 0; c < children.size(); ++c ) {
		param = children[ c ].update_gradient( delta, param );
	}

	return param;		 
}

void PoseElement::optimize( cv::Mat parent_transform, cv::Mat& uchar_mat ) {
	
}

void PoseElement::split( cv::Mat parent_transform, cv::Mat& diff ) {
	cv::Scalar mean, std_dev;
	cv::meanStdDev( diff, mean, std_dev );

	const double sigma = 1.0;
	cv::Mat src = diff - mean.val[0] > sigma * std_dev.val[0];
	cv::Mat dest = diff - mean.val[0] < sigma * std_dev.val[0];

	std::vector< std::vector<cv::Point3f> > src_pts;
	//cv::findContours( src, src_pts, 
	//	cv::CV_RETR_EXTERNAL, cv::CV_CHAIN_APPROX_SIMPLE );
	
/*
	const float area_thresh = 100.f;
	for( size_t i = 0; i < src_pts.size(); ++i ) {
		if( cv::contourArea( src_pts[i] ) < area_thresh )
			continue;
		for( size_t j = 0; j < dest_pts.size(); ++j ) {
			if( cv::contourArea( dest_pts[i] ) < area_thresh )
				continue;

			
		}
	}
*/	

}

cv::Mat& Pose::draw( cv::Mat& mat ) {
	mat = 255.f;
	cv::Mat trans = 
		( cv::Mat_<float>( 4, 4 ) <<
			1., 0., 0., position.x,
			0., 1., 0., position.y,
			0., 0., 1., position.z,
			0., 0., 0., 1. );
	root.draw( trans, mat );
	return mat;
}


void Pose::update( cv::Mat& uchar_mat ) {
	cv::Mat mat;
	uchar_mat.convertTo( mat, CV_32F );

	cv::Mat current( mat.size(), CV_32F, 255.f ),
		update( mat.size(), CV_32F, 255.f ),
		error( mat.size(), CV_32F, 0.f ),
		delta( mat.size(), CV_32F, 0.f );
	draw( current );

	imwrite( "base.png", mat );
	imwrite( "draw.png", current );

	cv::Mat error_out;
	error = current - mat;
	float drot = 5.f, cur_error = cv::norm( error );

	size_t i = 0;
	std::cout << "Converging." << std::endl;
	while( i < 100 ) {
		size_t parameter = 0;
		cv::Point3f offsets[3] = {
				cv::Point3f( drot, 0.f, 0.f ),
				cv::Point3f( 0.f, drot, 0.f ),
				cv::Point3f( 0.f, 0.f, drot )
			};

		error = draw( current ) - mat;
		cv::normalize( error, error_out, 0., 255., cv::NORM_MINMAX );
		imwrite( "base_error.png", error_out );
		cv::Mat design( 0, uchar_mat.rows*uchar_mat.cols, 
			CV_32F, 255.f );

		for( size_t o = 0; o < 3; ++o ) {
			position += offsets[ o ];
			delta = (draw( update ) - current) / drot;
	
			std::stringstream ss;
			ss << "error_pos" << o << ".png";
			cv::normalize( delta, error_out, 0., 255., cv::NORM_MINMAX );
			imwrite( ss.str().c_str(), delta.mul( error ) );

			if( cv::norm( delta ) )
				delta /= cv::norm( delta );
			design.push_back( delta.reshape( 0, 1 ) );
			position -= offsets[ o ];
		}

		while( !root.estimate_gradient( parameter++ ) ) {
			delta = (draw( update ) - current) / 0.1f;

			std::stringstream ss;
			ss << "error" << parameter << ".png";
			cv::normalize( delta, error_out, 0., 255., cv::NORM_MINMAX );
			imwrite( ss.str().c_str(), error_out );

			if( cv::norm( delta ) )
				delta /= cv::norm( delta );
			design.push_back( delta.reshape( 0, 1 ) );
		}
			
		error = draw( current ) - mat;
		cv::Mat gradient = -design * error.reshape( 0, 1 ).t();
		std::cout << gradient << std::endl;
		gradient /= cv::norm( gradient );
		std::cout << gradient << std::endl;

		float gamma = 1e-3;
		cv::Point3f offset; 

		size_t j = 0;
		do {
			cur_error = cv::norm( error );

			gamma *= 2.f;
			cv::Mat_<float> changes( gamma * gradient );
			offset = cv::Point3f(
				changes(0, 0), changes(1, 0), changes(2, 0) ); 
			std::cout << offset << std::endl;
			position += offset;

			cv::Mat update = gamma * gradient;
			root.update_gradient( update, 3 );

			error = draw( current ) - mat;
			std::cout << "Error: " << cur_error << ", " <<
				cv::norm( error ) <<  std::endl;

			std::stringstream ss;
			ss << "draw" << j++ << ".png";
			imwrite( ss.str().c_str(), current );

		} while( cv::norm( error ) <= cur_error );

		position -= offset;
		cv::Mat update = -gamma * gradient;
		root.update_gradient( update, 3 );
	}
}

PoseEstimator::PoseEstimator(): initialized(false) {

}

std::vector< cv::Point3f > cylinder( float rx, float ry, float h ) {
	std::vector< cv::Point3f > result;
	for( float t = 0.; t < 2*3.1415; t += 0.25 / (rx + ry) )
		for( float z = 0.; z < h; z += 0.2 ) {
			float x = rx * cos(t);
			float y = ry * sin(t);
			result.push_back( cv::Point3f( x, y, z ) );
		}
	return result;
}

void PoseEstimator::initialize( cv::Mat& data ) {
	//current_pose.position = cv::Point3f( 0., 80., 200. );
	current_pose.position = cv::Point3f( 0., 120., 220. );
	current_pose.root.length = 100.;
	current_pose.root.rotate( cv::Point3f( 0., 1.57079, 1.57079 ) );

	current_pose.root.point_cloud = cylinder( 75., 25., 100. );

	PoseElement left_shoulder;
	left_shoulder.length = 35.;
	left_shoulder.rotate( cv::Point3f( 0., 1.57079, 1.57079 ) );

	PoseElement left_arm;
	left_arm.length = 60.;
	left_arm.rotate( cv::Point3f( 0., 1.57079, 0. ) );

	left_arm.point_cloud = cylinder( 6., 6., 60. );
	left_shoulder.children.push_back( new PoseElement(left_arm) );

	PoseElement right_shoulder;
	right_shoulder.length = 35.;
	right_shoulder.rotate( cv::Point3f( 0., 1.57079, -1.57079 ) );

	PoseElement right_arm;
	right_arm.length = 60.;
	right_arm.rotate( cv::Point3f( 0., 1.57079, 0. ) );

	right_arm.point_cloud = cylinder( 6., 6., 60. );
	right_shoulder.children.push_back( new PoseElement(right_arm) );

	current_pose.root.children.push_back( new PoseElement(left_shoulder) );
	current_pose.root.children.push_back( new PoseElement(right_shoulder) );

	/*
	float row_off = float(data.rows)/2.f, col_off = float(data.cols)/2.f;
	for( int r = 0; r < data.rows; ++r )
		for( int c = 0; c < data.cols; ++c ) {
			float y = float(r) / data.rows - row_off;
			float x = float(c) / data.cols - col_off;

			cv::Point3f pt( x, y, 1.0f );
			float l = cv::norm( pt );
			pt *= data.at<float>(r, c) / l;
			current_pose.root.point_cloud.push_back( pt );
		}
	*/

	initialized = true;
}
#include <queue>
#include <utility>

template< typename T, typename V >
struct first_greater {
	bool operator() ( const std::pair< T, V >& one, 
		const std::pair< T, V >& two ) {
		return one.first > two.first;
	}
};

float solve( cv::Mat_<float>& T, cv::Mat_<unsigned char>& mask, 
	cv::Point i, cv::Point j ) {

	if( mask( i ) == 0 ) {
		if( mask( j ) == 0 ) {
			float r = cv::sqrt( 2*(T(i) - T(j))*(T(i) - T(j)) );
			float s = (T(i) + T(j) - r) / 2.f;
			if( s >= T(i) && s >= T(j) )
				return s;
	
			s += r;
			if( s >= T(i) && s >= T(j) )
				return s;
		} else {
			return 1 + T( i );
		}
	} else if( mask( j ) == 0 ) {
		return 1 + T( j );
	}

	return 1e6f;
}

void paint( cv::Mat& image, cv::Mat_<unsigned char>& mask, cv::Point& p ) {
	cv::Mat_<unsigned char> depth( image );
	//depth( p ) = 255;
	//return;

	float val = 0., norm = 0.;
	cv::Point offs[4] = {
		cv::Point( 1, 0 ), cv::Point( -1, 0 ),
		cv::Point( 0, 1 ), cv::Point( 0, -1 ) };

	for( int c = -10; c <= 10; ++c ) for( int r = -10; r <= 10; ++r ) {
		cv::Point off( c, r );
		cv::Point q = off + p;
		if( q.x < 0 || q.x >= image.cols 
			|| q.y < 0 || q.y >= image.rows )	continue;
		if( mask( q ) != 0 )	continue;

		float d = off.ddot( off );
		if( d > 100. )	continue;

		float w = 1. / d;
		cv::Point2f gradient;
		if( mask( q + offs[0] ) == 0 && mask( q + offs[1] ) == 0 &&
			mask( q + offs[2] ) == 0 && mask( q + offs[3] ) == 0 ){

			unsigned char gx, gy;
			gx = depth( q + offs[0] ) - depth( q + offs[1] );
			gy = depth( q + offs[2] ) - depth( q + offs[3] );

			float norm = cv::sqrt( gx*gx + gy*gy );
			if( norm )
				gradient = cv::Point2f( gx / norm, gy / norm );
		}
			
		val += w * (depth( q ) + gradient.dot( off ) );
		norm += w;	
	}

	depth( p ) = val / norm;
}

cv::Mat& cleanup( cv::Mat& depth ) {
	cv::Mat_<unsigned char> mask = cv::Mat( depth < 25 );
	cv::Mat_<float> T = cv::Mat( depth.size(), CV_32F, 0.f );
	T.setTo( 1e6f, mask );

	std::priority_queue< std::pair<float, cv::Point>,
		std::vector< std::pair<float, cv::Point> >,
		first_greater< float, cv::Point > > band;

	cv::Point offs[4] = {
		cv::Point( 1, 0 ), cv::Point( -1, 0 ),
		cv::Point( 0, 1 ), cv::Point( 0, -1 ) };

	for( size_t r = 0; r < T.rows; ++r )
		for( size_t c = 0; c < T.cols; ++c ) {
			cv::Point p( c, r );
			if( T( p ) == 0.f && (
				T(p + offs[0]) != 0.f || 
				T(p + offs[1]) != 0.f ||
				T(p + offs[2]) != 0.f ||
				T(p + offs[3]) != 0.f ) ) {

				//T( p ) = 0.f;
				mask( p ) = 2;
				paint( depth, mask, p );
				//depth.at<unsigned char>( p ) = 255;
				band.push( std::make_pair( 0.f, p ) );
			}
		}

	while( band.size() ) {
		std::pair<float, cv::Point> val = band.top();
		band.pop();
		
		std::cout << val.first << ", " << val.second << std::endl;
		mask( val.second ) = 0;

		for( size_t i = 0; i < 4; ++i ) {
			cv::Point pt = val.second + offs[i];
			if( pt.y < 0 || pt.y >= depth.rows ||
				pt.x < 0 || pt.x >= depth.cols )
				continue;

			if( mask( pt ) != 0 ) {
				if( mask( pt ) == 255 ) {
					mask( pt ) = 2;
					paint( depth, mask, pt );
				}
				
				float t = std::min(
					std::min( 
					solve(T, mask, pt+offs[0], pt+offs[2]),
					solve(T, mask, pt+offs[1], pt+offs[2])),
					std::min(
					solve(T, mask, pt+offs[0], pt+offs[3]),
					solve(T, mask, pt+offs[1], pt+offs[3]))
					);

				T( pt ) = t;
				band.push( std::make_pair( t, pt ) );
			}
		}
	}
/*	
	unsigned char last_val = 0;
	for( size_t r = 0; r < channels[0].rows; ++r )
		for( size_t c = 0; c < channels[0].cols; ++c ) 
			if( channels[0].at<unsigned char>( r, c ) < 5 )
				channels[0].at<unsigned char>(r, c) = last_val;
			else	last_val = channels[0].at<unsigned char>(r, c);
*/
	//cv::medianBlur( depth, depth, 5 );
	return depth;
}

Pose PoseEstimator::operator()( cv::Mat& data ) {
	std::vector< cv::Mat > channels( 3, data );
	cv::split( data, channels );

	MeanBackgroundRemover bg;
	//cv::Mat fg = bg( channels[0] );

	if( !initialized )	initialize( channels[0] );

	imwrite( "original.png", channels[0] );
	cleanup( channels[0] );
	imwrite( "modified.png", channels[0] );

	current_pose.update( channels[0] );
	return current_pose;
}


