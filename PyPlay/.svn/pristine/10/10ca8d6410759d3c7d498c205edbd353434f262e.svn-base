
#include "parser.h"

#include <iostream>

#define BOOST_SPIRIT_DEBUG

#include <boost/spirit/include/qi.hpp>
#include <boost/spirit/include/lex_lexertl.hpp>

#include <boost/spirit/include/phoenix_core.hpp>
#include <boost/spirit/include/phoenix_operator.hpp>
#include <boost/spirit/include/phoenix_object.hpp>
#include <boost/spirit/include/phoenix_fusion.hpp>
#include <boost/spirit/include/phoenix_container.hpp>
#include <boost/spirit/include/phoenix_statement.hpp>

#include <boost/mpl/at.hpp>
#include <boost/preprocessor/repetition/repeat.hpp>
#include <boost/fusion/include/adapt_struct.hpp>

using namespace AST;

using boost::mpl::at_c;
namespace phx = boost::phoenix;
namespace lex = boost::spirit::lex;
namespace qi = boost::spirit::qi;

BOOST_FUSION_ADAPT_STRUCT(
	AST::IfExpr,
	(AST::Expr_t, if_)
	(AST::Expr_t, then)
	(boost::optional<AST::Expr_t>, else_)
)

BOOST_FUSION_ADAPT_STRUCT(
	AST::LambdaExpr,
	(AST::IdentifierList_t, args)
	(AST::Expr_t, result)
)

BOOST_FUSION_ADAPT_STRUCT(
	AST::LetExpr,
	(AST::ExprList_t, bindings)
	(AST::Expr_t, in)
)

BOOST_FUSION_ADAPT_STRUCT(
	AST::MatchExpr::Match,
	(AST::Expr_t, with)
	(AST::Expr_t, in)
	(boost::optional<AST::Expr_t>, when)
)

BOOST_FUSION_ADAPT_STRUCT(
	AST::MatchExpr,
	(AST::Expr_t, val)
	(AST::MatchExpr::MatchList_t, matches)
)

template< typename Lexer >
struct ast_lexer: lex::lexer< Lexer > {
	struct atoi_impl {
		template< typename Arg > struct result						{	typedef int type;		};
		template< typename Arg > int operator()( Arg arg ) const	{	return atoi( arg.c_str() );		}
	};

	struct atof_impl {
		template< typename Arg > struct result						{	typedef double type;	};
		template< typename Arg > double operator()( Arg arg ) const	{	return atof( arg.c_str() );		}
	};

	phx::function<atoi_impl> atoi_lazy;
	phx::function<atof_impl> atof_lazy;

	ast_lexer()	{
		using phx::construct;
		using phx::val;

		using lex::lit;

		using lex::_pass;
		using lex::_val;
		using lex::_start;
		using lex::_end;
		using lex::_state;
		using lex::_tokenid;

		whitespace = "[ \\t\\r\\n]+";
		id = "[a-zA-Z_][a-zA-Z0-9_]*";
		operator_ = "[\\+\\-\\*/\\\\=;:<>]+";

		complex = "i";
		unit = "[a-hj-zA-Z][a-zA-Z]*";
		end_trail = ".";

		if_ = "if";
		then = "then";
		else_ = "else";
		let = "let";
		in = "in";
		match = "match";
		with = "with";
		when = "when";
		def = "def";

		error = "\\+-";
		lambda = "\\\\";
		map = "->";

		open_paren = "\\(";
		close_paren = "\\)";
		end_stmt = ";";
		open_match = "\\|";
		comma = ",";

		plus = "\\+";
		minus = "-";
		mul = "\\*";
		div = "\\/";
		power = "\\*\\*";
		assign = "=";

		eq = "==";
		lt = "<";
		gt = ">";
		le = "<=";
		ge = "=>";
		

		true_ = "true";
		false_ = "false";
		int_ = "\\d+";
		double_ = "(\\d*\\.)?\\d+([eE][-+]?\\d+)?";

		this->self
			=	true_ [ _val = construct< AST::Constant<bool> >( true ) ]
			|	false_ [ _val = construct< AST::Constant<bool> >( false ) ]

			|	int_ [ 
					_val = construct< AST::Constant<int> >
						( atoi_lazy( construct<std::string>( _start, _end ) ) ),
					_state = "NumericTrail"
				]
			|	double_ [ 
					_val = construct< AST::Constant<double> >
						( atof_lazy( construct<std::string>( _start, _end ) ) ),
					_state = "NumericTrail"
				]

			|	error |	lambda | map 
			|	open_paren | close_paren | end_stmt | open_match | comma

			|	power | plus | minus | mul | div | assign
			|	le | ge | eq | lt | gt

			|	if_ | then | else_ | let | in | match | with | when | def

			|	id [ _val = construct< AST::Identifier >( _start, _end ) ]
			|	operator_ [ _val = construct< AST::Identifier >( _start, _end ) ]
			|	whitespace[ _pass = lex::pass_flags::pass_ignore ]
		;

		this->self( "NumericTrail" )
			=	complex
			|	unit [ _val = construct< AST::BaseIdentifier_t >( _start, _end ) ]
			|	end_trail [ _end = _start, _state = "INITIAL", _pass = lex::pass_flags::pass_ignore ]
		;
	}

	lex::token_def<> whitespace, complex, complex_unity, end_trail;

	lex::token_def<> error, lambda, map;
	lex::token_def<> open_paren, close_paren, end_stmt, open_match, comma;

	lex::token_def<> plus, minus, mul, div, power, assign;
	lex::token_def<> lt, gt, le, ge, eq;

	lex::token_def< AST::Identifier > id, operator_;
	lex::token_def< AST::BaseIdentifier_t > unit;
	lex::token_def<> if_, then, else_, let, in, match, with, when, def;

	lex::token_def< AST::Constant<bool> > true_, false_;
	lex::token_def< AST::Constant<int> > int_;
	lex::token_def< AST::Constant<double> > double_;
};

template< typename Iterator >
struct ast_parser: qi::grammar< Iterator, Expr_t() > {

	template< typename TokenDef >
	ast_parser( TokenDef const& tok ): ast_parser::base_type( result_expr ) {
		using qi::_val;
		using qi::_1;
		using qi::_2;
		using qi::_3;
		using qi::_4;

		using qi::lit;
		using qi::eps;
		using qi::omit;
		
		using qi::on_error;
		using qi::fail;
		
		using phx::construct;
		using phx::push_back;

		using phx::at_c;
		using phx::val;
		using phx::while_;

		result_expr %= expr > omit[tok.end_stmt];
		expr %= assign_expr;

		assign_expr = logical_expr[ _val = _1 ] >> *(
			( tok.assign > logical_expr[ _val = construct<AssignExpr>( _1, _val ) ] )
			);

		logical_expr = term_expr[ _val = _1 ] >> *( 
			  ( tok.eq > term_expr[ _val = construct<EqExpr>( _val, _1 ) ] )
			| ( tok.lt  > term_expr[ _val = construct<LtExpr>( _val, _1 ) ] )
			| ( tok.gt  > term_expr[ _val = construct<GtExpr>( _val, _1 ) ] )
			| ( tok.le > term_expr[ _val = construct<LeExpr>( _val, _1 ) ] )
			| ( tok.ge > term_expr[ _val = construct<GeExpr>( _val, _1 ) ] )
			);

		term_expr = factor_expr[ _val = _1 ] >> *(
			  ( tok.plus > factor_expr[ _val = construct<PlusExpr>( _val, _1 ) ] )
			| ( tok.minus > factor_expr[ _val = construct<MinusExpr>( _val, _1 ) ] )
			);

		factor_expr = negate_expr[ _val = _1 ] >> *(
			  ( tok.mul > negate_expr[ _val = construct<MulExpr>( _val, _1 ) ] )
			| ( tok.div > negate_expr[ _val = construct<DivExpr>( _val, _1 ) ] )
			);

		negate_expr = power_expr[ _val = _1 ] 
			| tok.minus > negate_expr[ _val = construct<NegateExpr>( _1 ) ]
			;

		power_expr = call_expr[ _val = _1 ] >> *(
			( tok.power > call_expr[ _val = construct<PowExpr>( _val, _1 ) ] )
			);

		call_expr %= terminal_expr[ _val = _1 ] >> *(
			( terminal_expr [ _val = construct<CallExpr>( _val, _1 ) ] )
			);

		terminal_expr %= lambda_expr | let_expr | match_expr | sub_expr | base_expr;
		if_expr %= omit[tok.if_] > expr > omit[tok.then] > expr > -(omit[tok.else_] > expr);
		lambda_expr %= omit[tok.lambda] > (tok.id % omit[tok.comma]) > omit[tok.map] > expr;

		let_expr %= omit[tok.let] > (expr % omit[tok.comma]) > omit[tok.in] > expr;

		match_match %= omit[tok.open_match] > expr > omit[tok.map] > expr > -(omit[tok.when] > expr);
		match_expr %= omit[tok.match] > expr > omit[tok.with] > *match_match;

		sub_expr %= omit[tok.open_paren] >> expr > omit[tok.close_paren];
		base_expr %= base;

		base 
			= tok.true_ [ _val = _1 ]
			| tok.false_ [ _val = _1 ]

			/*
			| (tok.int_ >> tok.complex >> tok.unit) [ 
					_val = construct<UnitConstant>(
							construct<complex_t>( 0.0, bind(&Constant<int>::value, _1) ), _3
						)
				]
			| (tok.double_ >> tok.complex >> tok.unit) [ 
					_val = construct<UnitConstant>(
							construct<complex_t>( 0.0, bind(&Constant<double>::value, _1) ), _3
						)
				]

			| (tok.int_ >> tok.complex) [ 
					_val = construct<complex_t>( 0.0, bind(&Constant<int>::value, _1) ) 
				]
			| (tok.double_ >> tok.complex) [ 
					_val = construct<complex_t>( 0.0, bind(&Constant<double>::value, _1) ) 
				]
			*/

			| (tok.int_ >> tok.unit) [ _val = construct<UnitConstant>( _1, _2 ) ]
			| (tok.double_ >> tok.unit) [ _val = construct<UnitConstant>( _1, _2 ) ]

			| tok.int_ [ _val = _1 ]
			| tok.double_ [ _val = _1 ]
			| tok.id [ _val = _1 ]
		;

		
		on_error<fail>
        (
            result_expr,
			std::cout 
				<< val("Expecting ") << _4 << val(" here: \"")
				<< construct<std::string>(_3, _2) << val("\"") << std::endl
        );

		BOOST_SPIRIT_DEBUG_NODE( expr );
		BOOST_SPIRIT_DEBUG_NODE( assign_expr );
		BOOST_SPIRIT_DEBUG_NODE( logical_expr );
		BOOST_SPIRIT_DEBUG_NODE( term_expr );
		BOOST_SPIRIT_DEBUG_NODE( factor_expr );
		BOOST_SPIRIT_DEBUG_NODE( negate_expr );
		BOOST_SPIRIT_DEBUG_NODE( power_expr );
		BOOST_SPIRIT_DEBUG_NODE( call_expr );

		BOOST_SPIRIT_DEBUG_NODE( terminal_expr );
		BOOST_SPIRIT_DEBUG_NODE( if_expr );
		BOOST_SPIRIT_DEBUG_NODE( lambda_expr );
		BOOST_SPIRIT_DEBUG_NODE( let_expr );
		BOOST_SPIRIT_DEBUG_NODE( match_match );
		BOOST_SPIRIT_DEBUG_NODE( match_expr );
		BOOST_SPIRIT_DEBUG_NODE( sub_expr );
		BOOST_SPIRIT_DEBUG_NODE( base_expr );

		BOOST_SPIRIT_DEBUG_NODE( base );
	}

	size_t err_line;

	qi::rule<Iterator, Expr_t()> result_expr;
	qi::rule<Iterator, Expr_t()> expr;
	qi::rule<Iterator, Expr_t()> assign_expr;
	qi::rule<Iterator, Expr_t()> logical_expr;
	qi::rule<Iterator, Expr_t()> term_expr;
	qi::rule<Iterator, Expr_t()> factor_expr;
	qi::rule<Iterator, Expr_t()> negate_expr;
	qi::rule<Iterator, Expr_t()> power_expr;
	qi::rule<Iterator, Expr_t()> call_expr;

	qi::rule<Iterator, Expr_t()> terminal_expr;
	qi::rule<Iterator, IfExpr()> if_expr;
	qi::rule<Iterator, LambdaExpr()> lambda_expr;

	qi::rule<Iterator, LetExpr()> let_expr;
	qi::rule<Iterator, MatchExpr::Match()> match_match;
	qi::rule<Iterator, MatchExpr()> match_expr;

	qi::rule<Iterator, Expr_t()> sub_expr;
	qi::rule<Iterator, Expr_t()> base_expr;
	qi::rule<Iterator, Base_t()> base;
};

namespace boost { namespace spirit { namespace traits {
    // Provide specializations that assumes value has been assigned
	// Don't use code that attempts to create attribute from iterators (boost spirit base instantion does this)
	template< typename Iterator, typename AttributeTypes, typename HasState >
	struct assign_to_attribute_from_value< AST::Identifier, lex::lexertl::token<Iterator, AttributeTypes, HasState> > {
        static void call(lex::lexertl::token<Iterator, AttributeTypes, HasState> const& t, AST::Identifier& attr) {
			spirit::traits::assign_to(get< AST::Identifier >(t.value()), attr);
		}
	};

	template< typename Iterator, typename AttributeTypes, typename HasState >
	struct assign_to_attribute_from_value< AST::BaseIdentifier_t, lex::lexertl::token<Iterator, AttributeTypes, HasState> > {
        static void call(lex::lexertl::token<Iterator, AttributeTypes, HasState> const& t, AST::BaseIdentifier_t& attr) {
			spirit::traits::assign_to(get< AST::BaseIdentifier_t >(t.value()), attr);
		}
	};

	template< typename T, typename Iterator, typename AttributeTypes, typename HasState >
	struct assign_to_attribute_from_value< AST::Constant<T>, lex::lexertl::token<Iterator, AttributeTypes, HasState> > {
        static void call(lex::lexertl::token<Iterator, AttributeTypes, HasState> const& t, AST::Constant<T>& attr) {
			spirit::traits::assign_to(get< AST::Constant<T> >(t.value()), attr);
		}
	};

	template< typename Iterator, typename AttributeTypes, typename HasState >
	struct assign_to_attribute_from_value< AST::UnitConstant, lex::lexertl::token<Iterator, AttributeTypes, HasState> > {
        static void call(lex::lexertl::token<Iterator, AttributeTypes, HasState> const& t, AST::UnitConstant& attr) {
			spirit::traits::assign_to(get< AST::UnitConstant >(t.value()), attr);
		}
	};

	// More stupid shit in boost spirit, their overload for boost optional isn't close to working
	// Should probably submit a bug report for this ... or workaround
	/*
	template < typename Out >
	struct print_attribute_debug<Out, boost::optional<AST::Expr_t> > {
		static void call(Out& out, boost::optional<AST::Expr_t> const& val) {
			if (val)	print_attribute(out, *val);
			else		out << "<empty>";
        }
    };
	*/
}}}

struct token_printer {
	typedef bool result_type;

	template< typename Token >
	bool operator()( Token const& t ) const {
		std::cout << t.id() << ": " << t.value() << std::endl;
		return true;
	}
};

Parser& Parser::operator <<( const std::string& data ) {
	input += data;
	return *this;
}

void Parser::load( const std::string& file ) {
	std::ifstream in( file.c_str() );

	const size_t read_ln = 2048;
	char data[ read_ln ];

	while( !in.eof() ) {
		in.read( data, read_ln );
		(*this) << data;
	}

	(*this) << data;
}

AST::Expr_t Parser::get() {
	AST::Expr_t expr;
	(*this) >> expr;
	return expr;
}

void Parser::clear() {
	input = "";
}

Parser& Parser::operator >>( AST::Expr_t& expr ) {
	typedef char const* raw_iterator_type;

	typedef lex::lexertl::token< 
			raw_iterator_type, 
			boost::mpl::push_front< AST::BaseTypes, AST::BaseIdentifier_t >::type, 
			boost::mpl::true_
		> token_type;

	typedef lex::lexertl::actor_lexer< token_type > lexertl_type;
	typedef ast_lexer< lexertl_type > lexer_type;
	typedef lexer_type::iterator_type iterator_type;

	ast_lexer< lexertl_type > lexer;
	ast_parser< iterator_type > parser( lexer );

	raw_iterator_type begin = input.c_str();
	raw_iterator_type end = &begin[ input.size() ];

	/*
	bool tokenized = lex::tokenize( begin, end, lexer, token_printer() );
	begin = input.c_str();
	*/

	bool r = lex::tokenize_and_parse( begin, end, lexer, parser, expr );

	if( !r ) {
		std::cout << "Parsing Failed!" << std::endl;
		std::cout << " -> Failed at: " << std::string( begin, end ) << std::endl;
		input = "";
	} else {
		input = std::string( begin, end );
	}

	return *this;
}