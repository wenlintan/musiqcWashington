
#include <memory>
#include <algorithm>
#include <functional>
#include <cassert>

#include <boost/math/constants/constants.hpp>
#include <fftw3.h>

#include "Features.h"

double mel( double x ) {
    return 1125. * log (1. + x / 700.);
}

double imel( double x ) {
    return 700. * (exp (x / 1125.) - 1.);
}

MFCC::MFCC(const MFCCOptions& options) : _options(options),
window(static_cast<size_t>(options.window_size * options.sample_rate / 1000.)),
step(static_cast<size_t>(options.step_size * options.sample_rate / 1000.)),
mel_bins(options.nmel_banks+2), hamming_window(window), lifter(options.ncoeffs) {
	double min_mel = mel(_options.min_freq),
		max_mel = mel(_options.max_freq),
		step_mel = (max_mel - min_mel) / (_options.nmel_banks + 1.);

	for (size_t i = 0; i < _options.nmel_banks+2; ++i) {
		mel_bins[i] = imel(min_mel + i*step_mel) * window /
			_options.sample_rate;
	}

	const double pi = boost::math::constants::pi<double>();
	for (size_t i = 0; i < window; ++i) {
		hamming_window[i] = 0.54 - 0.46 * cos(2 * pi * i / (window - 1));
	}

	for (size_t i = 0; i < options.ncoeffs; ++i){
		lifter[i] = 1 + (options.lifter_coeff / 2) *
			sin(pi * i / options.lifter_coeff);
	}
}

MFCC::MatrixType MFCC::operator()(const WaveFile& wf) const{
	assert(wf.sample_rate() == _options.sample_rate);
	return (*this)(wf.samples());
}

MFCC::MatrixType MFCC::operator()(const std::vector<double>& samples) const {
    size_t place = 0;
	std::vector< fftw_complex > output(window);
	std::vector< double > melbanks(_options.nmel_banks), input(window);

	MatrixType result;
	VectorType features(_options.ncoeffs), 
		prev_features( _options.ncoeffs ), 
		prev_deltas( _options.ncoeffs );

	fftw_plan fft = fftw_plan_dft_r2c_1d(window,
		input.data(), output.data(),
		FFTW_ESTIMATE);

	fftw_plan dct = fftw_plan_r2r_1d(_options.nmel_banks,
		melbanks.data(), melbanks.data(), FFTW_REDFT10 /*DCT-II*/,
		FFTW_ESTIMATE);

    while( place + window < samples.size() ) {
		std::copy_n(&samples[place], window, input.begin());
		if (_options.hamming)
			std::transform(input.begin(), input.end(), hamming_window.begin(),
				input.begin(), std::multiplies<double>());
        fftw_execute( fft );

		std::fill(melbanks.begin(), melbanks.end(), 0.0);
		size_t prevbank = 0;

        for( 
			size_t i = size_t(mel_bins.front()); 
			i < size_t(mel_bins.back()); 
			++i ) {

			double power = output[i][0] * output[i][0];
			power += output[i][1]*output[i][1];
			power /= window;

			if( i > mel_bins[prevbank+1] ) {
				++prevbank;
				if (prevbank == _options.nmel_banks+1) break;
			}

			double factor = std::max(0.0, (i - mel_bins[prevbank]) /
				(mel_bins[prevbank + 1] - mel_bins[prevbank]));
			if (prevbank != 0)
				melbanks[prevbank-1] += (1.0 - factor) * power;
			if (prevbank != _options.nmel_banks)
				melbanks[prevbank] += factor * power;
		}

		std::transform(melbanks.begin(), melbanks.end(), melbanks.begin(), 
			std::ptr_fun<double, double>(log));
		fftw_execute(dct);

		if (_options.lifter)
			std::transform(lifter.begin(), lifter.end(), melbanks.begin(),
				melbanks.begin(), std::multiplies<double>());

		std::copy_n(melbanks.begin(), _options.ncoeffs, features.begin());
		result.push_back(features);
        place += step;
    }

	fftw_destroy_plan(fft);
	fftw_destroy_plan(dct);
	return result;
}

