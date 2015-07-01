
#ifndef PARSER__H
#define PARSER__H

#pragma once

#include "ast.h"

#include <fstream>
#include <string>

namespace AST {

class Parser {
private:
	std::string		input;

public:
	void load( const std::string& file );
	AST::Expr_t get();
	void clear();

	Parser& operator <<( const std::string& data );
	Parser& operator >>( AST::Expr_t& comm );
};

}

#endif