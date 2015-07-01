
#include "boost/filesystem/operations.hpp"
#include "boost/filesystem/path.hpp"

typedef boost::filesystem::directory_iterator dir_iter;
typedef boost::filesystem::path path;

#include "opencv2/highgui/highgui.hpp"

#include "utils.hpp"
#include "analysis.hpp"

#include <sstream>
#include <iostream>
#include <fstream>
#include <vector>
#include <algorithm>

int main(int argc, char** argv) {
	dir_iter end;

	if( argc < 2 ) {
		std::cout << "Require 2 arguments." << std::endl;
		return 0;
	}

	std::string parse_dir = argv[1];
	for( dir_iter data_iter(parse_dir); data_iter != end; ++data_iter ) {
		std::cout << "Parsing directory " << *data_iter << std::endl;
		std::vector< std::string > examples, tests;

		char temp[256];
		std::string data_dir = path(*data_iter).filename().string();
		path fpath =  path(*data_iter) / (data_dir + "_train.csv");
		std::ifstream csv( fpath.string().c_str() );

		while( csv.getline( temp, 256 ) ) {
			std::string data( temp );

			size_t comma = data.find( "," );
			std::string fileno = data.substr( 0, comma );
			std::string ident = data.substr( comma+1 );

			size_t id = std::atoi( ident.c_str() ) - 1;
			if( id >= examples.size() )
				examples.resize( id + 1 );

			fileno = "K" + fileno.substr( data_dir.length() );
			fileno += ".avi";
			examples[ id ] = path( *data_iter / fileno ).string();
		}

		size_t d = 1;
		while( true ) {
			std::stringstream ss;
			ss << "K_" << d << ".avi";

			path p( *data_iter / ss.str() );
			if( !boost::filesystem::exists(p) )
				break;

			std::string fname = p.string();
			//if( std::find( examples.begin(), examples.end(), fname )
			//	== examples.end() )
				tests.push_back( fname );
			++d;
		}

		CL::Analyzer a( data_dir, examples, tests );
		break;
	}

	return 0;
}

