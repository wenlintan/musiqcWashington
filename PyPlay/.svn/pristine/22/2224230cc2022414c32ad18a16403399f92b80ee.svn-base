
#ifndef SYMBOLS__H
#define SYMBOLS__H

#include <vector>
#include <string>

#include <boost/ptr_container/ptr_map.hpp>
#include <boost/assign.hpp>

#include "syntax_types.h"
#include "types.h"

namespace Scope {
using namespace boost::assign;

class ScopeVisitor {
public:
	typedef AST::Expression_t result_type;
	ScopeVisitor( const Scope& s ): scope( s )
	{}

	template< typename T >
	AST::Expression_t operator ()( T& exp ) const {
		return exp;
	}

	AST::Expression_t operator ()( AST::IdentifierExpression& exp ) const;
	AST::Expression_t operator ()( AST::CallExpression& exp ) const;

private:
	const Scope& scope;
};

class Scope {
public:
	AST::Expression_t bind( AST::Expression_t exp ) {
		return apply_visitor( ScopeVisitor( *this ), exp );
	}

	template< typename Signature >
	Scope& def( const std::string& name, boost::function<Signature> fn ) {
		objects[ name ] = new Function( name, *this, fn );
		return *this;
	}

	template< typename T >
	typename boost::enable_if< boost::is_arithmetic<T>, Scope& >::type
	def( const std::string& name, T value ) {
		objects[ name ] = new Variable( name, *this, value );
		return *this;
	}

	// If expression evaluates to constant at time of def, defined as Variable, otherwise Function
	Scope& def( const std::string& name, AST::Expression_t exp ) {
		if( AST::ConstantExpression_t* c = boost::get<AST::ConstantExpression_t>(&exp) ) {
			objects[ name ] = new Variable( name, *this, *c );
			return *this;
		}

		objects[ name ] = new Expression( name, *this, exp );
		return *this;
	}

	Scope& push( const Scope& other ) 	{	inner_scopes.push_back( other );	return *this;	}
	Scope& pop()						{	inner_scopes.pop_back();			return *this; 	}

private:
	boost::ptr_map< std::string, Object >	objects;
	std::vector< Scope >					inner_scopes;
};

}

#endif

