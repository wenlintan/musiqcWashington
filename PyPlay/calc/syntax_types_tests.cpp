
#include <gtest/gtest.h>

#include <boost/function.hpp>
#include <boost/bind.hpp>

#include "syntax_types.h"
#include <FlexLexer.h>
#include "lexer.h"

int yyparse( void* lexer, boost::function<void(AST::Statement_t)> cb );

struct StatementHolder {
	typedef void result_type;
	void operator()( AST::Statement_t s ) {	statement = s; }
	AST::Statement_t statement;
};

void test_simple_expression( const std::string& text, AST::Expression_t& exp ) {
	StatementHolder h;
	TTYFlexLexer test_lex( text );
	yyparse( &test_lex, boost::bind( boost::ref(h), _1 ) );

	AST::Expression_t expect1 = exp;
	AST::Expression_t actual1 = boost::get<AST::ExpressionStatement>( h.statement ).exp;
	EXPECT_EQ( expect1, actual1 );
}

TEST(AST, SimpleTests) {
	AST::Expression_t test = AST::PlusExpression( AST::DoubleConstantExpression(3.), AST::DoubleConstantExpression(4.) );
	test_simple_expression( "3.+4.;", test );

	test = AST::PlusExpression( 
				AST::DoubleConstantExpression(3.), 
				AST::MulExpression( AST::DoubleConstantExpression(4.), AST::DoubleConstantExpression(5.) ) );
	test_simple_expression( "3.+4.*5.;", test );

	test = AST::PlusExpression( 
				AST::DivExpression( AST::DoubleConstantExpression(3.), AST::DoubleConstantExpression(6.) ),
				AST::MulExpression( AST::DoubleConstantExpression(4.), AST::DoubleConstantExpression(5.) ) );
	test_simple_expression( "3./6.+4.*5.;", test );
}


