
#include <iostream>
#include <gtest/gtest.h>
#include <boost/program_options.hpp>

#include "eval.h"
#include "parser.h"

namespace po = boost::program_options;

int main( int argc, char** argv ) {
	po::options_description desc("Allowed options");
	desc.add_options()
	    ("help,h", "produce help message")
	    ("test,t", "run test suite")
	;

	po::variables_map vm;
	po::store(po::parse_command_line(argc, argv, desc), vm);
	po::notify(vm);    

	if( vm.count( "help" ) ) {
		std::cout << desc << std::endl;
	    return 0;
	}

	if( vm.count( "test" ) ) {
		::testing::InitGoogleTest(&argc, argv);
		int result = RUN_ALL_TESTS();
		std::cin.get();
		return result;
	}

	AST::Parser p;
	Eval::Evaluator eval;
	AST::Expr_t e;

	char data[ 1024 ];
	while( true ) {
		std::cout << "-->";
		std::cin.getline( data, 1024 );

		p << data >> e;
		std::cout << e << std::endl;
		std::cout << eval.evaluate( e ) << std::endl;
	}
	return 0;
}