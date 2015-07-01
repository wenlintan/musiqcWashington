
#include <string>
#include <vector>

#pragma once 

class WaveFile {
    std::string _filename;
    unsigned int _sample_rate, _bps;
    std::vector< double > _samples;

public:
    WaveFile( const std::string& filename );

    const std::string& filename() const          { return _filename; }
    unsigned int sample_rate() const             { return _sample_rate; }
    unsigned int bps() const                     { return _bps; }
    const std::vector< double >& samples() const { return _samples; }
};

