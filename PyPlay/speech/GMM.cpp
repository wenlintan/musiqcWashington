
#include <algorithm>
#include <numeric>

#include "GMM.h"

#include <boost/accumulators/accumulators.hpp>
#include <boost/accumulators/statistics/stats.hpp>
#include <boost/accumulators/statistics/mean.hpp>
#include <boost/accumulators/statistics/moment.hpp>
using namespace boost::accumulators;

DiagonalGaussian::DiagonalGaussian(size_t nfeatures) :
mean(nfeatures), sigma(nfeatures), norm(0.0) {}

GMM::GMM(size_t ncomponents, size_t nfeatures) {
	gaussians.insert(gaussians.end(), ncomponents,
		std::make_pair(1.0 / ncomponents, DiagonalGaussian(nfeatures)));
}