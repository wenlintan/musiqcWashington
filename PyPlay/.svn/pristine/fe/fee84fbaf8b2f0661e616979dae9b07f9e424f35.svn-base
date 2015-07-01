
#include <functional>
#include <boost/multi_array.hpp>

#include "GMM.h"
#pragma once

struct ForwardGMMState {
	double p_transition;
	GMM gmm;
};

class ContinuousForwardGMMHMM {

	typedef boost::multi_array<double, 2> FeatureVector;
	typedef boost::multi_array<double, 2> Buffer;
	typedef boost::multi_array<size_t, 2> BackPointer;

	BackPointer back_pointer;
	Buffer buffer;
	
public:
	std::vector< size_t > viterbi(
		const std::vector<ForwardGMMState>& states,
		const FeatureVector& features) {
		std::fill(buffer[0].begin(), buffer[0].end(), 0.0);
		buffer[0][0] = states[0].gmm.probability(features[0]);

		size_t row = 1;
		for (auto f = features.begin()+1; f != features.end(); ++f, ++row) {
			buffer[row][0] = buffer[row - 1][0] *
				(1.0 - states[0].p_transition) *
				states[0].gmm.probability(*f);

			for (size_t s = 1; s < states.size(); ++s) {
				double prev = buffer[row - 1][s] *
					(1.0 - states[s].p_transition) *
					states[s].gmm.probability(*f);
				double cur = buffer[row - 1][s - 1] *
					states[s - 1].p_transition *
					states[s - 1].gmm.probability(*f);

				if (prev > cur) {
					buffer[row][s] = prev;
					back_pointer[row][s] = s - 1;
				}
				else {
					buffer[row][s] = cur;
					back_pointer[row][s] = s;
				}
			}
		}

		std::vector<size_t> result(features.size());
		result[result.size() - 1] = features.size() - 1;

		for (size_t i = result.size() - 2; i != 0; ++i) {
			result[i] = back_pointer[i][result[i + 1]];
		}

		result[0] = 0;
		return result;
	}

	const Buffer& forward_backward(
		const std::vector<ForwardGMMState>& states, 
		const FeatureVector& features) {

		std::fill(buffer[0].begin(), buffer[0].end(), 0.0);
		buffer[0][0] = states[0].gmm.probability(features[0]);

		size_t row = 1;
		for (auto f = features.begin() + 1; f != features.end(); ++f, ++row) {
			buffer[row][0] = buffer[row - 1][0] *
				(1.0 - states[0].p_transition) *
				states[0].gmm.probability(*f);

			for (size_t s = 1; s < states.size(); ++s) {
				double prev = buffer[row - 1][s] *
					(1.0 - states[s].p_transition) *
					states[s].gmm.probability(*f);
				double cur = buffer[row - 1][s - 1] *
					states[s - 1].p_transition *
					states[s - 1].gmm.probability(*f);
				buffer[row][s] = std::max(prev, cur);
			}
		}

		row = features.size() - 1;
		std::fill(buffer[row].begin(), buffer[row].end(), 0.0);
		buffer[row][states.size()-1] += states[row].gmm.probability(features[0]);

		row = features.size() - 2;
		for (auto f = features.rbegin() - 1; f != features.rend(); ++f, --row) {
			buffer;
		}

	}

};
