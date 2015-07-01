
#ifdef _DEBUG
#  pragma comment( lib, "gtestd.lib" )
#  pragma comment( lib, "gtest_maind.lib" )
#else
#  pragma comment( lib, "gtest.lib" )
#endif

#include <gtest/gtest.h>

#include "eval.h"
#include "parser.h"

using namespace AST;

TEST( Lambda, PartialEvaluation ) {
	Expr_t base;
	AST::Parser() << "(\\x,y -> x) 3 4;" >> base;
	AST::Expr_t actual = Eval::Evaluator().evaluate( base ), expect = Constant<int>(3);
	EXPECT_EQ( expect, actual );
}