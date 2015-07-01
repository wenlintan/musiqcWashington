
#include "opencv2/opencv.hpp"
#include <string>

namespace CL {

class Analyzer {
	std::string name;
	std::vector< cv::Mat > examples;
	std::vector< size_t > starts;

	cv::PCA pca;
	std::vector< cv::Mat > pca_features;

	void principle_components();
	std::vector<size_t> time_warp_pca( const std::vector<cv::Mat>& test );

public:
	typedef std::vector<std::string> FileList_t;
	Analyzer( const std::string& name,
		const FileList_t examples, const FileList_t tests );

};

}


