
#include "boost/filesystem/operations.hpp"
#include "boost/filesystem/path.hpp"

typedef boost::filesystem::directory_iterator dir_iter;
typedef boost::filesystem::path path;

#include <sstream>
#include <iostream>

#include "avi.h"

int main(int argc, char** argv) {
	dir_iter end;
	for( dir_iter data_iter("data"); data_iter != end; ++data_iter ) {
		std::cout << "Parsing directory " << *data_iter << std::endl;
		size_t d = 1;
		while( true ) {
			std::stringstream ss;
			ss << "K_" << d << ".avi";

			path p( *data_iter / ss.str() );
			if( !boost::filesystem::exists(p) )
				break;

			std::string fname = p.string();
			std::cout << "Parsing file " << fname << std::endl;
			AVI::AVIFile avi( fname );
			++d;
		}
	}

	return 0;
}
