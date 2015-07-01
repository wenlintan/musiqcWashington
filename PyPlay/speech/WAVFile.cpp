
#include <cstdint>
#include <fstream>
#include <iostream>
#include <memory>

#include "WAVFile.h"

struct WaveChunkHeader {
	uint8_t id[4];
    uint32_t size;
};

struct WaveFileHeader {
    uint8_t format[4];
};

struct WaveFileFormat {
    uint16_t audio_format, nchannels;
    uint32_t sample_rate, byte_rate;
    uint16_t block_align, bps;
};

WaveFile::WaveFile( const std::string& filename ) {
    _filename = filename;
    std::ifstream file( filename.c_str(), 
        std::ifstream::binary | std::ifstream::in );

	if (!file.is_open()) {
		std::cout << "Failed to open wave file." << std::endl;
		return;
	}

	WaveChunkHeader header;
    bool format_loaded = false, file_loaded = false;
	while (file.read(reinterpret_cast<char*>(&header), sizeof(header))) {
		std::string id(reinterpret_cast<char*>(header.id), 4);
		if (id == "RIFF") {
			WaveFileHeader file_header;
			file.read(reinterpret_cast<char*>(&file_header),
				sizeof(WaveFileHeader));

			std::string fmt(reinterpret_cast<char*>(file_header.format), 4);
			if (fmt != "WAVE") {
				std::cout << "Unknown file format." << std::endl;
				break;
			}
		}
		else if (id == "fmt ") {
			if (header.size != sizeof(WaveFileFormat)) {
				std::cout << "Bad file format in Wave file." << std::endl;
				break;
			}
			WaveFileFormat file_format;
			file.read(reinterpret_cast<char*>(&file_format), header.size);
			if (file_format.audio_format != 1 || file_format.nchannels != 1){
				std::cout << "Unloadable file format in wave file." << std::endl;
				break;
			}

            _sample_rate = file_format.sample_rate;
            _bps = file_format.bps;
            format_loaded = true;
        } else if( id == "data" ) {
            if( !format_loaded ) {
                std::cout << "File data before format." << std::endl;
                break;
            }
            size_t nsamples = header.size / (_bps/8);
            _samples.reserve( nsamples );

            if( _bps == 8 ) {
                std::unique_ptr< uint8_t[] > data( new uint8_t[nsamples] );
                file.read( reinterpret_cast<char*>(data.get()), nsamples );
                for( size_t i = 0; i < nsamples; ++i ) {
                    _samples.push_back( static_cast<double>(data[i]) );
                }
            } else if( _bps == 16 ) {
                std::unique_ptr< int16_t[] > data( new int16_t[nsamples] );
                file.read( reinterpret_cast<char*>(data.get()), nsamples*2 );
                for( size_t i = 0; i < nsamples; ++i ) {
                    _samples.push_back( static_cast<double>(data[i]) );
                }
            } else {
                std::cout << "Uknown bits per sample rate." << std::endl;
                break;
            }

            file_loaded = true;
        } else {
            // Unknown chunk type skipping
            file.seekg( header.size, std::ifstream::cur );
        }
    } 
}

