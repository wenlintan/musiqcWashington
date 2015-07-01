
%token lex_identifier
%token lex_constant

%token lex_endstmt lex_comma
%token lex_oparen lex_cparen lex_obracket lex_cbracket lex_osqbracket lex_csqbracket
%token lex_givenkwd lex_withkwd lex_inkwd
%token lex_constantkwd lex_variablekwd lex_functionkwd

%left lex_plus lex_minus
%left lex_mul lex_div 
%right lex_pow 
%left NEG

%right lex_equals
%right lex_lt lex_le lex_ge lex_gt lex_eq
%right lex_logical_and lex_logical_or

%right lex_map
%right lex_assign

%{
#include <cmath>
#include <boost/function.hpp>

#include <FlexLexer.h>
#include "lexer.h"

#include "syntax_types.h"
#define YYSTYPE AST::AST_t
extern int line_number;

#define YYERROR_VERBOSE
#define YYPARSE_PARAM scanner, boost::function<void(AST::Statement_t)> handle
#define YYLEX_PARAM scanner

int yylex( void* data ) {
	TTYFlexLexer* lex = (TTYFlexLexer*)data;
	return lex->yylex();
}

int yyerror( const char *s ) {
	printf( "Error on line %d: %s\n", line_number, s );
	return 0;
}
%}

%%
statements:
	statements statement {
		if( AST::Statement_t* s = boost::get<AST::Statement_t>(&$2) )
			handle( *s );
	}
	| 
;

statement:
	lex_endstmt
	| expression comma_qualifier_list_empty lex_endstmt {
		AST::ExpressionStatement s( boost::get<AST::Expression_t>($1) );
		s.qualifiers = boost::get<AST::QualifierList_t>($2);
		$$ = (AST::Statement_t)s;
	}
	| lex_identifier lex_assign expression lex_endstmt {
	}
	| lex_obracket statement_list lex_cbracket {
		$$ = $2;
	}
	| error lex_endstmt {
		yyerrok;
	}
;

statement_list:
	statement statement_list {
		AST::StatementList_t l = boost::get<AST::StatementList_t>($2);
		l.insert( l.begin(), boost::get<AST::Statement_t>($1) );
		$$ = l;
	}
	| {
		$$ = AST::StatementList_t();
	}
;

qualifier:
	lex_givenkwd expression {
		$$ = (AST::Qualifier_t)AST::GivenQualifier( boost::get<AST::Expression_t>($2) );
	}
	| lex_withkwd comma_variable_declaration_list {
		$$ = (AST::Qualifier_t)AST::WithQualifier( boost::get<AST::VariableDeclarationList_t>($2) );
	}
	| lex_inkwd expression {
		$$ = (AST::Qualifier_t)AST::InQualifier( boost::get<AST::Expression_t>($2) );
	}
;

comma_qualifier_list:
	qualifier lex_comma comma_qualifier_list {
		AST::QualifierList_t l = boost::get<AST::QualifierList_t>($3);
		l.insert( l.begin(), boost::get<AST::Qualifier_t>($1) );
		$$ = l;
	}
	| qualifier {
		$$ = AST::QualifierList_t( 1, boost::get<AST::Qualifier_t>($1) );
	}
;

comma_qualifier_list_empty:
	comma_qualifier_list 	{	$$ = $1;	}
	| 						{	$$ = AST::QualifierList_t();	}
;

variable_declaration:
	lex_constantkwd lex_identifier {
		$$ = (AST::VariableDeclaration_t)AST::ConstantVariableDeclaration( boost::get<AST::Identifier>($2) );
	}
	| lex_variablekwd lex_identifier {
		$$ = (AST::VariableDeclaration_t)AST::VariableVariableDeclaration( boost::get<AST::Identifier>($2) );
	}
	| lex_functionkwd lex_identifier lex_oparen comma_identifier_list_empty lex_cparen {
		$$ = (AST::VariableDeclaration_t)AST::FunctionVariableDeclaration( boost::get<AST::Identifier>($2),
					boost::get<AST::IdentifierList_t>($4) );
	}
;

comma_variable_declaration_list:
	variable_declaration lex_comma comma_variable_declaration_list {
		AST::VariableDeclarationList_t l = boost::get<AST::VariableDeclarationList_t>($3);
		l.insert( l.begin(), boost::get<AST::VariableDeclaration_t>($1) );
		$$ = l;
	}
	| variable_declaration {
		$$ = AST::VariableDeclarationList_t( 1, boost::get<AST::VariableDeclaration_t>($1) );
	}
;	

comma_identifier_list_empty:
	comma_identifier_list 	{	$$ = $1;	}
	| 						{	$$ = AST::IdentifierList_t();	}
;

comma_identifier_list:
	lex_identifier lex_comma comma_identifier_list {
		AST::IdentifierList_t l = boost::get<AST::IdentifierList_t>($3);
		l.insert( l.begin(), boost::get<AST::Identifier>($1) );
		$$ = l;
	}
	| lex_identifier {
		$$ = AST::IdentifierList_t( 1, boost::get<AST::Identifier>($1) );
	}
;

expression:
	expression lex_equals expression {
		$$ = (AST::Expression_t)AST::EqualExpression( boost::get<AST::Expression_t>($1), boost::get<AST::Expression_t>($3) );
	}
	comma_identifier_list lex_map expression {
		$$ = (AST::Expression_t)AST::LambdaExpression( boost::get<AST::IdentifierList_t>($1), boost::get<AST::Expression_t>($3) );
	}
	
	expression lex_plus expression {
		$$ = (AST::Expression_t)AST::PlusExpression( boost::get<AST::Expression_t>($1), boost::get<AST::Expression_t>($3) );
	}
	| expression lex_minus expression {
		$$ = (AST::Expression_t)AST::MinusExpression( boost::get<AST::Expression_t>($1), boost::get<AST::Expression_t>($3) );
	}
	| expression lex_mul expression {
		$$ = (AST::Expression_t)AST::MulExpression( boost::get<AST::Expression_t>($1), boost::get<AST::Expression_t>($3) );
	}
	| expression lex_div expression {
		$$ = (AST::Expression_t)AST::DivExpression( boost::get<AST::Expression_t>($1), boost::get<AST::Expression_t>($3) );
	}

	| lex_minus expression %prec NEG {
		$$ = (AST::Expression_t)AST::NegateExpression( boost::get<AST::Expression_t>($2) );
	}
	| expression lex_pow expression {
		$$ = (AST::Expression_t)AST::PowExpression( boost::get<AST::Expression_t>($1), boost::get<AST::Expression_t>($3) );
	}
	| lex_oparen expression lex_cparen {
		$$ = $2;
	}

	| lex_constant {
		$$ = (AST::Expression_t)AST::ExpressionFromConstant( boost::get<AST::Constant_t>($1) );
	}
	| lex_identifier {
		$$ = (AST::Expression_t)AST::IdentifierExpression( boost::get<AST::Identifier>($1) );
	}
	| expression lex_oparen comma_expression_list_empty lex_cparen {
		AST::ExpressionList_t l = boost::get<AST::ExpressionList_t>($3);
		$$ = (AST::Expression_t)AST::CallExpression( boost::get<AST::Expression_t>($1), l );
	}
;

comma_expression_list_empty:
	comma_expression_list 	{	$$ = $1;	}
	| 						{	$$ = AST::ExpressionList_t();	}
;

comma_expression_list:
	expression lex_comma comma_expression_list {
		AST::ExpressionList_t l = boost::get<AST::ExpressionList_t>($3);
		l.insert( l.begin(), boost::get<AST::Expression_t>($1) );
		$$ = l;
	}
	| expression {
		$$ = AST::ExpressionList_t( 1, boost::get<AST::Expression_t>($1) );
	}
;

%%




	
