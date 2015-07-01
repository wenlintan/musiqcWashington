
#include "environment.h"

#include <boost/spirit/include/phoenix_core.hpp>
#include <boost/spirit/include/phoenix_bind.hpp>
#include <boost/spirit/include/phoenix_operator.hpp>
#include <boost/spirit/include/phoenix_function.hpp>

#include <algorithm>

using namespace Eval;
namespace phx = boost::phoenix;

Namespace::Namespace( const AST::LetExpr& let ) {
	put( let );
}

void Namespace::put( const Namespace::Identifier_t& id, const Namespace::Value_t& val ) {
	map[ id ] = val;	
}

void Namespace::put( const AST::LetExpr& let ) {
	std::for_each( let.bindings.begin(), let.bindings.end(), 
		phx::bind( &Namespace::put_assn, *this, phx::arg_names::_1 ) );
}

const Namespace::Value_t& Namespace::get( const Namespace::Identifier_t& id ) const {
	Map_t::const_iterator iter = map.find( id );
	if( iter == map.end() )		throw LookupException();
	return iter->second;
}

void Namespace::put_assn( const AST::Expr_t& assn ) {
	//put( assn.id.id, assn.val );
}

void Environment::push( const AST::LetExpr& let ) {
	if( env.size() ) {
		Namespace current = env.back();
		current.put( let );
		env.push_back( current );
		return;
	}

	env.push_back( Namespace( let ) );
}

void Environment::pop() {
	env.pop_back();
}

const Environment::Value_t& Environment::get( const Environment::Identifier_t& id ) const {
	if( !env.size() )	throw LookupException();
	return env.back().get( id );
}
