
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

TEST( Diff, Polynomials ) {
	std::string data = 
		"let diff_simple = \\diff_expr -> match diff_expr with"
		"	| term + expr -> "
		"		diff_simple term + diff_simple expr "
		"	| factor * expr -> "
		"		diff_simple factor * expr + factor * diff_simple expr "
		"	| base ** exponent -> "
		"		exponent * base ** ( exponent - 1 ) * diff_simple base + "
		"		base ** exponent * ln base * diff_simple exponent "
		"	| cos expr -> -(sin expr) * diff_simple expr "
		"	| sin expr -> (cos expr) * diff_simple expr "
		"	| x -> 1 when variable x "
		"	| y -> 0 when variable y "
		"	| c -> 0 when constant c "
		"in diff_simple (5*x**2 + 4);";

	Expr_t base;
	AST::Parser() << data >> base;
	std::cout << base << std::endl;

	AST::Expr_t actual = Eval::Evaluator().evaluate( base ), 
		expect = Constant<int>(3);

	EXPECT_EQ( expect, actual );
}