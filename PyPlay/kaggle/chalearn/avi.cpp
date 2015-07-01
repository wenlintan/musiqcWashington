
#include "avi.h"
using namespace AVI;

std::string AVIFile::dw_to_str( boost::uint32_t dw ) {
	return std::string( reinterpret_cast<char*>(&dw), 4 );
}

AVIItem AVIFile::load_item( std::ifstream& in ) {
	AVIItem item;
	item.list = false;
	in.read( reinterpret_cast<char*>(&item.data.chunk), sizeof(CHUNK_header) );

	std::string name = dw_to_str(item.data.chunk.dwFourCC);
	if( name == "LIST" || name == "RIFF" ) {
		in.read( reinterpret_cast<char*>(&item.data.list.dwFourCC), 4 );
		item.list = true;
	}

	return item;
}

AVIStream AVIFile::load_stream_header( std::ifstream& in, AVIItem& item ) {
	size_t left = item.data.list.dwSize - 4;
	std::cout << "Stream header " << left << " " << dw_to_str(item.data.list.dwFourCC) << std::endl;
	while( left  && left < item.data.list.dwSize ) {
		AVIItem i = load_item( in );
		left -= i.data.list.dwSize;
		left -= sizeof(CHUNK_header);
		std::cout << i.data.list.dwSize << " " << left << std::endl;

		std::cout << dw_to_str(i.data.chunk.dwFourCC) << std::endl;
		if( !i.list && dw_to_str(i.data.chunk.dwFourCC) == "strh" ) {
			AVIStreamHeader sh = load_header<AVIStreamHeader>( in );
			std::cout << dw_to_str(sh.fccType) << std::endl;
			std::cout << dw_to_str(sh.fccHandler) << std::endl;
			in.seekg( i.data.chunk.dwSize - sizeof(AVIStreamHeader),
				   std::ios_base::cur	);
		} else if( dw_to_str(i.data.chunk.dwFourCC) == "strn" ) {
			std::string name( i.data.chunk.dwSize+1, '\0' );
			in.read( const_cast<char*>(name.c_str()), i.data.chunk.dwSize+1 );
			std::cout << "Name " << name << std::endl;	
			// Correct weird off-by-one problem
			left -= 1;
		} else {
			size_t off = i.data.list.dwSize + (i.list? -4: 0);
			in.seekg( off, std::ios_base::cur );
		}
	}
	return AVIStream();
}

AVIFile::AVIFile( const std::string& filename ) {
	std::ifstream f( filename.c_str(), 
			std::ifstream::binary | std::ifstream::in );
	if( !f.is_open() )
		throw "ERROR";

	AVIItem riff_avi = load_item( f );
	if( dw_to_str(riff_avi.data.list.dwList) != "RIFF" )
		throw "ERROR";
	if( dw_to_str(riff_avi.data.list.dwFourCC) != "AVI " )
		throw "ERROR";
	
	AVIItem header_list = load_item( f );
	if( !header_list.list || 
		dw_to_str(header_list.data.list.dwFourCC) != "hdrl" )
		throw "ERROR";
		
	size_t left = header_list.data.list.dwSize - 4;
	while( left < header_list.data.list.dwSize ) {
		AVIItem header_item = load_item( f );
		left -= header_item.data.list.dwSize;
		left -= sizeof(CHUNK_header);

		std::cout << dw_to_str(header_item.data.chunk.dwFourCC) << std::endl;
		std::cout << dw_to_str(header_item.data.list.dwFourCC) << std::endl;
		if( !header_item.list &&
			dw_to_str(header_item.data.chunk.dwFourCC) == "avih" ) {
			MainAVIHeader header = load_header<MainAVIHeader>( f );
			std::cout << header.dwWidth << " " << header.dwHeight << std::endl;
			f.seekg( header_item.data.list.dwSize - sizeof(MainAVIHeader),
				  std::ios_base::cur );
		} else if( header_item.list &&
			dw_to_str(header_item.data.list.dwFourCC) == "strl" ) {
			load_stream_header( f, header_item );
		} else {
			size_t off = header_item.data.list.dwSize + (header_item.list? -4: 0);
			f.seekg( off, std::ios_base::cur );
		}
	}

}

