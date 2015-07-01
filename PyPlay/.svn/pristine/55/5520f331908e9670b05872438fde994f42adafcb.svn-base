
#include <boost/function.hpp>
#include <boost/bind.hpp>

#include <FlexLexer.h>
#include "lexer.h"

#include "syntax_types.h"
#include "simplify_visitor.h"

using std::cout;
struct ProcessVisitor {
	typedef void result_type;

	template< typename T >
	void operator()( T& statement ) const {
		PrintVisitor pv( cout );
		pv( statement );
	}

	void operator()( AST::ExpressionStatement& statement ) const {
		PrintVisitor pv( cout );
		OrderVisitor ov;	SimplifyVisitor sv;

		pv( statement );

		AST::Expression_t temp = apply_visitor( ov, statement.exp );
		statement.exp = apply_visitor( sv, temp );

		pv( statement );
	}
};

int
process( AST::Statement_t s ) {
	apply_visitor( ProcessVisitor(), s );
	return 0;
}

int yyparse( void* lexer, boost::function<void(AST::Statement_t)> handler );

int
main(int argc, char **argv)
{
	TTYFlexLexer* lex = new TTYFlexLexer();
	while( !yyparse( lex, boost::bind( &process, _1 ) ) );
	return 0;
}

