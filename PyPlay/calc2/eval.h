
#ifndef EVAL__H
#define EVAL__H

#pragma once

#include "ast.h"
#include "type.h"
#include "environment.h"

namespace Eval {

class Evaluator {
public:
	typedef Environment Environment_t;
	AST::Expr_t evaluate( const AST::Expr_t& expr );

protected:
	Environment_t env;
};

}

#endif