
#include "WAVFile.h"

#pragma once

struct MFCCOptions {
    double window_size, step_size;  //ms;
	size_t nmel_banks, ncoeffs, sample_rate;
	double min_freq, max_freq, lifter_coeff;
    bool hamming, lifter, deltas, delta_deltas;
};

class MFCC {
	MFCCOptions _options;
	size_t window, step;
	std::vector<double> mel_bins;
	std::vector<double> hamming_window;
	std::vector<double> lifter;

public:
    MFCC( const MFCCOptions& options );

	typedef std::vector<double> VectorType;
	typedef std::vector<VectorType> MatrixType;

	MatrixType operator()(const WaveFile& wf) const;
	MatrixType operator()(const std::vector<double>& data) const;

	size_t nfeatures() { return _options.ncoeffs; }

};

