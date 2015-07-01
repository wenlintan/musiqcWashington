%{
#include "syntax_types.h"
#define YYSTYPE AST::AST_t

#include "syntax.tab.h"
int line_number = 1;

#include "lexer.h"
%}

%option c++
%option noyywrap
%option yyclass="TTYFlexLexer"

%%

\n 				{ line_number++; }
[ \t\r]			{ /* Discard newlines, spaces, and tabs */ }

";"				{ return lex_endstmt; }
","				{ return lex_comma; }

"("				{ return lex_oparen; }
")"				{ return lex_cparen; }
"{"				{ return lex_obracket; }
"}"				{ return lex_cbracket; }
"["				{ return lex_osqbracket; }
"]"				{ return lex_csqbracket; }

"given"			{ return lex_givenkwd; }
"with"			{ return lex_withkwd; }
"in"			{ return lex_inkwd; }

"constant"		{ return lex_constantkwd; }
"variable"		{ return lex_variablekwd; }
"function"		{ return lex_functionkwd; }

":="			{ return lex_assign; }
"=>"			{ return lex_map; }

"&&"			{ return lex_logical_and; }
"||"			{ return lex_logical_or; }

"<"				{ return lex_lt; }
"<="			{ return lex_le; }
">="			{ return lex_ge; }
">"				{ return lex_gt; }
"=="			{ return lex_eq; }

"="				{ return lex_equals; }
"**"			{ return lex_pow; }
"*"				{ return lex_mul; }
"/"				{ return lex_div; }
"+"				{ return lex_plus; }
"-"				{ return lex_minus; }

"true" {
	yylval = (AST::Constant_t)AST::BooleanConstant( true );
	return lex_constant;
}

"false" {
	yylval = (AST::Constant_t)AST::BooleanConstant( false );
	return lex_constant;
}

[1-9][0-9]* {
	yylval = (AST::Constant_t)AST::IntegerConstant( atoi(yytext) );
	return lex_constant;
}
		
[1-9][0-9]*(\.[0-9]*)?(e(\+|\-)?[1-9][0-9]*)? { 
	yylval = (AST::Constant_t)AST::DoubleConstant( atof(yytext) );
	return lex_constant; 
}

[a-zA-Z_][a-zA-Z0-9_]* { 
	yylval = AST::Identifier( yytext );		
	return lex_identifier; 
}

"\"[a-zA-Z0-9_\ ]*\"" {
	std::string s( yytext );
	yylval = AST::Identifier( s.substr( 1, s.length()-2 ) );
	return lex_identifier;
}
%%

