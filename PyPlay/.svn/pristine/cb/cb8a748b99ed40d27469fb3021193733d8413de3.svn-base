
#include "boost/cstdint.hpp"

#include <string>
#include <iostream>
#include <fstream>

namespace AVI {

using boost::uint64_t;
typedef boost::uint32_t DWORD;
typedef boost::uint16_t WORD;
typedef boost::uint8_t BYTE;

struct CHUNK_header {
	DWORD dwFourCC, dwSize;
};

struct LIST_header {
	DWORD dwList, dwSize, dwFourCC;
};

struct AVIItem {
	bool list;
	union { CHUNK_header chunk; LIST_header list; } data;
};

struct MainAVIHeader {
	DWORD dwMicroSecPerFrame, dwMaxBytesPerSec, dwPaddingGranularity;
	DWORD dwFlags, dwTotalFrames, dwInitialFrames, dwStreams;
	DWORD dwSuggestedBufferSize;

	DWORD dwWidth, dwHeight;
	DWORD dwReserved[4];
};

struct AVIStreamHeader {
	DWORD fccType, fccHandler;
	DWORD dwFlags;
	WORD wPriority, wLanguage;

	DWORD dwInitialFrames, dwScale, dwRate, dwStart, dwLength;
	DWORD dwSuggestedBufferSize;
	DWORD dwQuality, dwSampleSize;

	DWORD rcFrame[4];
};

struct AVISuperIndex {
	DWORD fcc, cb;
	WORD wLongsPerEntry;

	BYTE bIndexSubType, bIndexType;
	DWORD nEntriesInUse, dwChunkId;
	DWORD dwReserved[3];
};

struct AVISuperIndexEntry {
	uint64_t qwOffset;
	DWORD dwSize, dwDuration;
};


class AVIStream {

};
	
class AVIFile {
	std::string dw_to_str( boost::uint32_t dw );

	template< typename T >
	T load_header( std::ifstream& in ) {
		T res;
		in.read( reinterpret_cast<char*>(&res), sizeof(T) );
		return res;
	}

	AVIItem load_item( std::ifstream& in );
	AVIStream load_stream_header( std::ifstream& in, AVIItem& item );

public:
	AVIFile( const std::string& filename );
};

}


