
#ifndef ENVIRONMENT__H
#define ENVIRONMENT__H

#pragma once

#include "ast.h"

#include <map>

namespace Eval {

struct LookupException {};

class Namespace {
public:
	typedef AST::BaseIdentifier_t Identifier_t;
	typedef AST::Expr_t Value_t;

	Namespace()		
	{}

	Namespace( const AST::LetExpr& let );

	void put( const Identifier_t& id, const Value_t& val );
	void put( const AST::LetExpr& let );
	const Value_t& get( const Identifier_t& id ) const;

protected:
	void put_assn( const AST::Expr_t& assn );

	typedef std::map< Identifier_t, Value_t > Map_t;
	Map_t map;
};

class Environment {
public:
	typedef Namespace Namespace_t;
	typedef Namespace_t::Identifier_t Identifier_t;
	typedef Namespace_t::Value_t Value_t;

	void push( const AST::LetExpr& let );
	void pop();

	const Value_t& get( const Identifier_t& id ) const;

protected:
	typedef std::vector< Namespace > Environment_t;
	Environment_t env;
};

}

#endif