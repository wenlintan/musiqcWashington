#ifndef TYPES__H
#define TYPES__H

#include <vector>
#include <exception>

#include <boost/mpl/logical.hpp>
#include <boost/mpl/at.hpp>

#include <boost/function.hpp>
#include <boost/function_types/result_type.hpp>
#include <boost/function_types/function_arity.hpp>
#include <boost/function_types/parameter_types.hpp>
#include <boost/type_traits.hpp>

#include <boost/ptr_container/ptr_map.hpp>
#include <boost/assign.hpp>

#include "syntax_types.h"

namespace Types {
using namespace boost::assign;

struct bad_invoke: public std::runtime_error {
	bad_invoke( const std::string& n ): std::runtime_error( n )
	{}
};

struct bad_convert: public std::runtime_error {
	bad_convert( const std::string& n ): std::runtime_error( n )
	{}
};

struct not_implemented: public std::runtime_error {
	not_implemented( const std::string& n ): std::runtime_error( n )
	{}
};

typedef AST::ExpressionList_t& 	args_type;
typedef AST::Expression_t& 		result_type;
typedef void*					function_type;

typedef void 	(*invoke_type)( function_type, args_type, result_type );
struct manager_type {
	void (*release_type)( function_type data );
	void (*check_arg_type)( function_type data, args_type args, result_type result );
};

template< typename T, typename Enable = void >
class Converter {
};

template< typename T >
class Converter<T, typename boost::enable_if< boost::is_arithmetic<T>, boost::mpl::int_<0> >::type> {
	T convert( AST::Expression_t& exp ) {
		AST::ConstantExpressionBase<T>* c = boost::get< AST::ConstantExpressionBase<T> >( &exp );
		if( !c )	throw bad_convert( "invalid conversion." );
		return c->value;
	}
};

template< typename T >
class Converter<T, typename boost::enable_if< boost::is_base_of<AST::Expression, T>, boost::mpl::int_<1> >::type> {
	T convert( AST::Expression_t& exp ) {
		T* c = boost::get< T >( &exp );
		if( !c )	throw bad_convert( "invalid conversion." );
		return *c;
	}
};

template< >
class Converter< AST::Expression_t, boost::mpl::int_<2> > {
	AST::Expression_t convert( AST::Expression_t& exp ) {
		return exp;
	}
};

template< typename Signature, 
	typename R = typename boost::function_types::result_type<Signature>::type,
	size_t Arity = boost::function_types::function_arity<Signature>::value,
	typename Params = typename boost::function_types::parameter_types<Signature>::type,
	typename VoidReturn = typename boost::is_void<R>::type >
class CInvoker {
private:
	typedef boost::function<Signature> type;
};

template< typename Signature, typename R, typename Params >
class CInvoker< Signature, R, 1, Params, boost::mpl::false_ > {
	typedef boost::function<Signature> type;
	const static size_t Arity = 1;

public:
	static inline void invoke( function_type data, args_type args, result_type result ) {
		if( args.size() != Arity )			throw bad_invoke( "incorrect number of arguments." );

		type fn = *((type*)data);
		result = fn( Converter< typename boost::mpl::at_c<Params,0>::type >().convert( args[0] ) );
	}
};

class Scope;
class Object {
public:
	Object( const std::string& name_, Scope& container ): name( name_ ), scope( &container )
	{}

	virtual AST::Expression_t operator ()( AST::ExpressionList_t l ) 	{	throw not_implemented( "operator ()." );	}
	virtual AST::Expression_t operator - ( ) 							{	throw not_implemented( "operator -." );		}

	virtual AST::Expression_t operator = ( AST::Expression_t exp );

protected:
	std::string		name;
	Scope*			scope;

	std::map< std::string, Object >		members;
};

class Function: public Object {
public:
	template< typename Signature >
	Function( const std::string& name, Scope& scope, boost::function<Signature> fn ):
			Object( name, scope ) {

		typedef CInvoker< Signature > invoker_type;

		func = (function_type)( new boost::function<Signature>( fn ) );
		invoker = &invoker_type::invoke;		
	}

	Function( const std::string& name, Scope& scope, AST::Expression_t exp ):
			Object( name, scope ) {

		func = (function_type)( new AST::Expression_t(exp) );
		invoker = 0;
	}

	Function( const Function& fn ): Object( fn.name, *fn.scope ) {
		// need manager to reallocate data
	}

	~Function() {
		// need manager function to release allocated data
	}

	AST::Expression_t operator ()( AST::ExpressionList_t args ) {
		AST::Expression_t result;
		invoker( func, args, result );
		return result;
	}
	
private:
	invoke_type		invoker;
	function_type	func;	
};

class Constant: public Object {
public:
	Variable( const std::string& name, Scope& scope, AST::Expression_t exp ):
			Object( name, scope ), value( boost::get<AST::ConstantExpression_t>( exp ) )
	{ }

	template< typename T >
	Variable( const std::string& name, Scope& scope, T val, typename boost::enable_if< boost::is_arithmetic<T> >::type* dummy = 0 ):
			Object( name, scope ), value( AST::ConstantExpressionBase<T>( val ) )
	{ }

private:
	AST::ConstantExpression_t	value;
};

class Expression: public Object {
public:
	Expression( const std::string& name, Scope& scope, AST::Expression_t expression ):
			Object( name, scope ), exp( expression )
	{ }

	// For lambda expression, evaluates with given arguments
	// For other expression, if called with zero arguments evaluates expression in current scope
	AST::Expression_t operator ()( AST::ExpressionList_t args );
	void subs( AST::IdentifierExpression id, AST::ConstantExpression_t val );

	AST::Expression_t evaluate();
	AST::Expression_t simplify();

private:
	AST::Expression_t	exp;
};

}

#endif


