
#include "opencv2/opencv.hpp"

#include "boost/ptr_container/ptr_vector.hpp"

#include <vector>
#include <string>
#include <iostream>

#pragma once

namespace CL {

struct MeanBackgroundRemover {
	const static double cutoff_sigma;
	cv::Mat& operator() ( cv::Mat& mat );
};

class MotionHistory {
	std::vector< cv::Mat > buffer;
	size_t buffer_index;
	const static size_t buffer_size = 4;

	double norm;
	const static double decay;

	bool setup_run;
	void setup( cv::Mat& mat );

public:
	MotionHistory();
	cv::Mat& operator() ( cv::Mat& mat );
};

struct PoseElement {
	size_t		child, offset;
	cv::Point3f	position, rotation;
	float		length;

	std::vector< cv::Point3f >	point_cloud;
	cv::Mat		transform, child_transform;

	typename boost::ptr_vector<PoseElement> children;

	void rotate( const cv::Point3f& drot );
	cv::Mat& draw( cv::Mat parent_transform, cv::Mat& data );

	bool estimate_gradient( size_t param );
	size_t update_gradient( cv::Mat& delta, size_t param = 0 );

	void optimize( cv::Mat parent_transform, cv::Mat& data );
	void split( cv::Mat parent_transform, cv::Mat& data );
};


struct Pose {
	cv::Point3f 	position;
	PoseElement 	root;

	cv::Mat& draw( cv::Mat& surface );
	void update( cv::Mat& data );
};

class PoseEstimator {
	bool	initialized;
	void	initialize( cv::Mat& mat );

	Pose	current_pose;

public:
	PoseEstimator();
	Pose operator() ( cv::Mat& mat );	
};


}

