
#include <vector>

#pragma once

struct GMMOptions {
	size_t nmixtures;
};

struct DiagonalGaussian {
	std::vector<double> mean, sigma;
	double norm;
	size_t nobservations;

	DiagonalGaussian(size_t nfeatures);

	template< typename Container >
	double probability(const Container& x) const {
		double res = norm;
		const double sqrt2 = sqrt(2.);
		for (size_t i = 0; i < mean.size(); ++i) {
			double val = (x[i] - mean[i]) / sqrt2 / sigma[i];
			res += -val*val;
		}
		return res;
	}

	void clear();
	void update(double prob, const std::vector<double>& x);
	void finalize();
};

struct GMM {
	typedef std::pair<double, DiagonalGaussian> WeightedDiagonalGaussian;
	std::vector<WeightedDiagonalGaussian> gaussians;

	GMM(size_t ncomponents, size_t nfeatures);

	template< typename Container >
	double probability(const Container& x) const {
		return std::accumulate(gaussians.begin(), gaussians.end(), 0.0,
			[=](double res, const WeightedDiagonalGaussian& g) {
			return res + g.first * g.second.probability(x);
		});
	}
};

