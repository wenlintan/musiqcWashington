
#include "eval.h"

#include <boost/spirit/include/phoenix_core.hpp>
#include <boost/spirit/include/phoenix_bind.hpp>
#include <boost/spirit/include/phoenix_operator.hpp>
#include <boost/spirit/include/phoenix_function.hpp>

using namespace Eval;
using namespace AST;

namespace phx = boost::phoenix;
using boost::apply_visitor;

struct lazy_apply_visitor_impl {
	template< typename Visitor, typename Arg1, typename Arg2 >
	struct result { typedef typename Visitor::result_type type; };

	template< typename Visitor, typename Arg1, typename Arg2 >
	typename Visitor::result_type operator()( Visitor& v, Arg1 a, Arg2 b ) const {
		return apply_visitor( v, a, b );
	}
};
phx::function<lazy_apply_visitor_impl> const lazy_apply_visitor = lazy_apply_visitor_impl();

struct MatchVisitor {
	typedef bool result_type;
	MatchVisitor( const Evaluator::Environment_t& environ ): env( environ )
	{}

	template< typename T, typename U >
	bool operator()( T t, U u ) {
		std::cout << "Failing match " << t << " with " << u << std::endl;
		bindings.bindings.resize(0);
		return false;
	}

	template< typename T >
	bool operator()( const Identifier& match, const T& expr ) {
		std::cout << "Matching " << match << " with " << expr << std::endl;
		bindings.bindings.push_back( AssignExpr( match.id, expr ) );
		return true;
	}

	template< typename T >
	bool operator()( const Constant<T>& match, const Constant<T>& expr ) {
		if( !(match.value == expr.value) ) {
			std::cout << "Failing match " << match << " with " << expr << std::endl;
			bindings.bindings.resize(0);
			return false;
		}

		std::cout << "Matching " << match << " with " << expr << std::endl;
		return true;
	}

	template< typename Op >
	bool operator()( const UnaryExpr<Op>& match, const UnaryExpr<Op>& expr ) {
		std::cout << "Matching " << match << " with " << expr << std::endl;
		return apply_visitor( *this, match.left, expr.left );
	}

	template< typename Op >
	bool operator()( const BinaryExpr<Op>& match, const BinaryExpr<Op>& expr ) {
		std::cout << "Matching " << match << " with " << expr << std::endl;
		return apply_visitor( *this, match.left, expr.left ) &&
			apply_visitor( *this, match.right, expr.right );
	}

	/*
	template< typename Op >
	bool operator()( const N_aryExpr<Op>& match, const N_aryExpr<Op>& expr ) {
		std::cout << "Matching " << match << " with " << expr << std::endl;
		if( match.exprs.size() > expr.exprs.size() ) return false;
		return std::equal( match.exprs.begin(), match.exprs.end(), expr.exprs.begin(), apply_visitor( *this ) );
	}
	*/

	LetExpr bindings;
	const Evaluator::Environment_t& env;
};

struct EnvVisitor {
	typedef Expr_t result_type;
	EnvVisitor( Evaluator::Environment_t& environ ): env( environ )		{}

	Expr_t operator ()( const Identifier& id ) const {
		try {
			return apply_visitor( *this, env.get( id.id ) );
		} catch( LookupException ) {
			return id;
		}
	}

	Expr_t lambda_bind( LambdaExpr& lambda, LetExpr& let, const Expr_t& value ) const {
		let.bindings.push_back( AssignExpr(lambda.args.front(), value) );
		lambda.args.erase( lambda.args.begin() );

		if( lambda.args.empty() )	return (*this)( let );
		return lambda;
	}

	Expr_t operator ()( const CallExpr& call ) const {
		Expr_t func = apply_visitor( *this, call.left ), arg = apply_visitor( *this, call.right );

		if( LambdaExpr* lambda = boost::get<LambdaExpr>( &func ) ) {
			if( LetExpr* let = boost::get<LetExpr>( &lambda->result ) )
				return lambda_bind( *lambda, *let, arg );

			lambda->result = LetExpr( lambda->result );
			return lambda_bind( *lambda, boost::get<LetExpr>(lambda->result), arg );
		}

		return CallExpr( func, arg );
	}

	Expr_t operator ()( const LetExpr& let ) const {
		env.push( let );
		Expr_t result = apply_visitor( *this, let.in );
		env.pop();

		return result;
	}

	bool evaluates_true( const Expr_t& expr ) const {
		Expr_t eval = apply_visitor( *this, expr );

		if( Constant<bool>* boolean = boost::get< Constant<bool> >( &eval ) )
			return boolean->value;
		return false;
	}

	Expr_t operator ()( const MatchExpr& match ) const {
		MatchVisitor visitor( env );
		Expr_t value = apply_visitor( *this, match.val );

		MatchExpr::MatchList_t::const_iterator iter = match.matches.begin();

		while( iter != match.matches.end() ) {
			iter = std::find_if( iter, 
				match.matches.end(),
				lazy_apply_visitor( phx::ref( visitor ),
					phx::bind( &MatchExpr::Match::with, phx::arg_names::_1 ), 
					value ) 
				);

			if( iter != match.matches.end() && ( !iter->when || evaluates_true( *iter->when ) ) ) {
				// successfully completed match, apply match bindings and execute
				visitor.bindings.in = iter->in;
				std::cout << "Match success: " << *iter << " to " << visitor.bindings << std::endl;
				return (*this)( visitor.bindings );
			}

			++iter;
		}

		return match;
	}

	template< typename Op >
	Expr_t operator ()( const BinaryExpr<Op>& expr ) const {
		return BinaryExpr<Op>( apply_visitor( *this, expr.left ), apply_visitor( *this, expr.right ) );
	}

	/*
	template< typename Op >
	Expr_t operator ()( const N_aryExpr<Op>& expr ) const {
		std::vector< Expr_t > trans( expr.exprs.size() );
		std::transform( expr.exprs.begin(), expr.exprs.end(), trans.begin(), apply_visitor( *this ) );
		return N_aryExpr<Op>( trans );
	}
	*/

	template< typename T >
	Expr_t operator ()( T unknown ) const {
		return unknown;
	}

	Evaluator::Environment_t& env;
};

Expr_t Evaluator::evaluate( const Expr_t& expr ) {
	return apply_visitor( EnvVisitor( env ), expr );
}