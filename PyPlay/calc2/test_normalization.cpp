
#include <gtest/gtest.h>

#include <boost/assign.hpp>
using namespace boost::assign;

#include <boost/spirit/include/phoenix_core.hpp>
#include <boost/spirit/include/phoenix_bind.hpp>
#include <boost/spirit/include/phoenix_operator.hpp>
namespace phx = boost::phoenix;

#include "eval.h"
#include "parser.h"

using namespace AST;

class Normalization: public ::testing::TestWithParam< std::vector<const char*> > {
public:
	void TestSorting() {
		std::vector<const char*> params = GetParam();
		std::vector<Expr_t> exprs( params.size() );

		std::transform( params.begin(), params.end(), exprs.begin(), 
			phx::bind( &AST::Parser::get, phx::ref( parser ) << phx::arg_names::_1  ) );

		for( std::vector<Expr_t>::iterator i = ++exprs.begin(); i != exprs.end(); ++i ) {
			EXPECT_EQ( exprs.front(), *i );
		}
	}

protected:
	AST::Parser	parser;
};

TEST_P( Normalization, ExprSorting ) {
	TestSorting();
}

std::vector< std::vector< const char* > > ConstExprSortingTests = list_of
	( list_of< const char* >( "3+4;" )( "4+3;" ) )
	( list_of< const char* >( "3+1+542+4;" )( "1+542+4+3;" ) )
	( list_of< const char* >( "2.2+3.5+4.2;" )( "4.2+2.2+3.5;" )( "4.2+3.5+2.2;" ) )
	;

INSTANTIATE_TEST_CASE_P( Constants, Normalization, ::testing::ValuesIn( ConstExprSortingTests ) );

std::vector< std::vector< const char* > > TypeExprSortingTests = list_of
	( list_of< const char* >( "id+3i+2.3i+5+true;" )( "id+true+3i+5+2.3i;" )( "5+3i+id+true+2.3i;" ) )
	( list_of< const char* >( "id+3i+(3*5)+2.3i-5;" )( "3*5+id+3i-5+2.3i;" )( "-5+3i+id+3*5+2.3i;" ) )
	;

INSTANTIATE_TEST_CASE_P( Types, Normalization, ::testing::ValuesIn( TypeExprSortingTests ) );
