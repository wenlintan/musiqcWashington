
#ifndef SYNTAX_TYPES__H
#define SYNTAX_TYPES__H

#include <string>
#include <vector>

#include <iostream>
#include <algorithm>
#include <functional>

#include <boost/variant.hpp>
#include <boost/type_traits.hpp>
using boost::apply_visitor;

#include <boost/mpl/void.hpp>
#include <boost/mpl/bool.hpp>

#include <boost/mpl/comparison.hpp>
#include <boost/mpl/logical.hpp>

#include <boost/mpl/vector.hpp>
#include <boost/mpl/vector_c.hpp>
#include <boost/mpl/at.hpp>

#include <boost/mpl/unpack_args.hpp>
#include <boost/mpl/zip_view.hpp>
#include <boost/mpl/fold.hpp>

#include <boost/assign.hpp>
using namespace boost::assign;

#include "matrix.h"

namespace AST {

/////////////////////////////////////////////////////////////////////////
// Base class and raw types from lexer
/////////////////////////////////////////////////////////////////////////
class Base {
public:
	enum BaseType { CONSTANT, IDENTIFIER, STATEMENT, VARIABLE_DECLARATION, QUALIFIER, EXPRESSION };
	BaseType base_type;

	Base( BaseType t ): base_type( t )
	{}
};

class Identifier: public Base {
public:
	Identifier(): Base( Base::IDENTIFIER )
	{}

	explicit Identifier( const char* id ): Base( Base::IDENTIFIER ), ident( id )
	{}

	explicit Identifier( std::string id ): Base( Base::IDENTIFIER ), ident( id )
	{}

	bool operator <( const Identifier& other ) const {
		return ident < other.ident;
	}

	std::string	ident;
};

typedef std::vector< Identifier > IdentifierList_t;

class Constant: public Base {
public:
	enum ConstantType { BOOLEAN, INTEGER, DOUBLE, MATRIX };
	ConstantType constant_type;

	Constant( ConstantType t ): Base( Base::CONSTANT ), constant_type( t )
	{}
};

template< typename T >
struct ConstantTypeMap {};

template<> struct ConstantTypeMap<bool> 	{ const static Constant::ConstantType value = Constant::BOOLEAN; };
template<> struct ConstantTypeMap<int> 		{ const static Constant::ConstantType value = Constant::INTEGER; };
template<> struct ConstantTypeMap<double> 	{ const static Constant::ConstantType value = Constant::DOUBLE; };
template< typename T > struct ConstantTypeMap< matrix<T> > 	{ const static Constant::ConstantType value = Constant::MATRIX; };

template< typename T >
class ConstantBase: public Constant {
public:
	ConstantBase(): Constant( ConstantTypeMap<T>::value )
	{}

	explicit ConstantBase( T val ): Constant( ConstantTypeMap<T>::value ), value( val )
	{}

	bool operator <( const ConstantBase<T>& other ) const {
		return value < other.value;
	}

	T value;
};

typedef ConstantBase<bool> BooleanConstant;
typedef ConstantBase<int> IntegerConstant;
typedef ConstantBase<double> DoubleConstant;

typedef boost::variant< BooleanConstant, IntegerConstant, DoubleConstant > Constant_t;
typedef std::vector< Constant_t > ConstantList_t;

/////////////////////////////////////////////////////////////////////////
// Base class and derived implementations for expressions
/////////////////////////////////////////////////////////////////////////
class Expression: public Base {
public:
	enum ExpressionType { IDENTIFIER, CONSTANT, CALL, LAMBDA, UNARY, BINARY, N_ARY, LIST };
	ExpressionType expression_type;

	Expression( ExpressionType t ): Base( Base::EXPRESSION ), expression_type( t )
	{}
};

// Atomic expression types
class IdentifierExpression: public Expression {
public:
	IdentifierExpression(): Expression( Expression::IDENTIFIER )
	{}

	IdentifierExpression( std::string id ): Expression( Expression::IDENTIFIER ), ident( id )
	{}

	IdentifierExpression( Identifier id ): Expression( Expression::IDENTIFIER ), ident( id.ident )
	{}

	std::string	ident;
};

class ConstantExpression: public Expression {
public:
	typedef Constant::ConstantType ConstantExpressionType;
	ConstantExpressionType constant_expression_type;

	ConstantExpression( ConstantExpressionType t ): Expression( Expression::CONSTANT ), constant_expression_type( t )
	{}
};

template< typename T >
class ConstantExpressionBase: public ConstantExpression {
public:
	ConstantExpressionBase(): ConstantExpression( ConstantTypeMap<T>::value )
	{}

	ConstantExpressionBase( const T& val ): ConstantExpression( ConstantTypeMap<T>::value ), value( val )	
	{}

	ConstantExpressionBase( const ConstantBase<T>& c ): ConstantExpression( ConstantTypeMap<T>::value ), value( c.value )
	{}

	T value;
};

typedef ConstantExpressionBase<bool> BooleanConstantExpression;
typedef ConstantExpressionBase<int> IntegerConstantExpression;
typedef ConstantExpressionBase<double> DoubleConstantExpression;

typedef boost::variant< BooleanConstantExpression, IntegerConstantExpression, DoubleConstantExpression > 
	ConstantExpression_t;

namespace detail {
	struct ConstantExpressionMapVisitor {
		typedef ConstantExpression_t result_type;

		template< typename T >
		ConstantExpression_t operator ()( const ConstantBase<T>& c ) const {
			return ConstantExpressionBase<T>( c );
		}
	};
}

inline ConstantExpression_t ExpressionFromConstant( Constant_t constant ) {
	return apply_visitor( detail::ConstantExpressionMapVisitor(), constant );
}

class CallExpression;
class LambdaExpression;

class NegateExpression;
class ReciprocalExpression;

class MinusExpression;
class DivExpression;
class PowExpression;

class PlusExpression;
class MulExpression;
class EqualsExpression;

typedef boost::variant< IdentifierExpression, 		ConstantExpression_t,
	boost::recursive_wrapper<CallExpression>, 		boost::recursive_wrapper<LambdaExpression>,
	boost::recursive_wrapper<NegateExpression>,		boost::recursive_wrapper<ReciprocalExpression>, 
	boost::recursive_wrapper<PlusExpression>,		boost::recursive_wrapper<MinusExpression>, 		
	boost::recursive_wrapper<MulExpression>,		boost::recursive_wrapper<DivExpression>, 		
	boost::recursive_wrapper<PowExpression>,		boost::recursive_wrapper<EqualsExpression> > 
		Expression_t;

typedef std::vector< Expression_t > ExpressionList_t;

class CallExpression: public Expression {
public:
	CallExpression(): Expression( Expression::CALL )
	{}

	CallExpression( Identifier fn, ExpressionList_t& l ): 
		Expression( Expression::CALL ), func( fn.ident ), arguments( l )
	{}

	void add_argument( Expression_t arg ) {
		arguments.push_back( arg );
	}

	Expression_t			function;
	ExpressionList_t		arguments;
};

class LambdaExpression: public Expression {
public:
	LambdaExpression(): Expression( Expression::LAMBDA )
	{}

	LambdaExpression( IdentifierList_t ids, Expression_t exp ): Expression( Expression::LAMBDA ), variables( ids ), val( exp )
	{}

	IdentifierList_t		variables;
	Expression_t			value;
};

// Unary operator expressions
class UnaryExpression: public Expression {
public:
	enum UnaryExpressionType { NEGATE, RECIPROCAL };
	UnaryExpressionType unary_expression_type;

	UnaryExpression( UnaryExpressionType t, Expression_t r ):
		Expression( Expression::UNARY ), right( r )
	{}

	Expression_t		right;
};

class NegateExpression: public UnaryExpression {
public:
	NegateExpression( Expression_t r ): UnaryExpression( UnaryExpression::RECIPROCAL, r )
	{}
};

class ReciprocalExpression: public UnaryExpression {
public:
	ReciprocalExpression( Expression_t r ): UnaryExpression( UnaryExpression::RECIPROCAL, r )
	{}
};

// Binary operator expressions
class BinaryExpression: public Expression {
public:
	enum BinaryExpressionType { MINUS, DIV, POW };
	BinaryExpressionType binary_expression_type;

	BinaryExpression( BinaryExpressionType t, Expression_t l, Expression_t r ):
		Expression( Expression::BINARY ), left( l ), right( r )
	{}

	Expression_t		left, right;
};

class MinusExpression: public BinaryExpression {
public:
	MinusExpression( Expression_t l, Expression_t r ): BinaryExpression( BinaryExpression::MINUS, l, r )
	{}
};

class DivExpression: public BinaryExpression {
public:
	DivExpression( Expression_t l, Expression_t r ): BinaryExpression( BinaryExpression::DIV, l, r )
	{}
};

class PowExpression: public BinaryExpression {
public:
	PowExpression( Expression_t l, Expression_t r ): BinaryExpression( BinaryExpression::POW, l, r )
	{}
};

// Binary operator expressions
class N_aryExpression: public Expression {
public:
	enum N_aryExpressionType { PLUS, MUL, EQUALS };
	N_aryExpressionType n_ary_expression_type;

	N_aryExpression( N_aryExpressionType t ): Expression( Expression::N_ARY ), n_ary_expression_type( t )
	{}

	N_aryExpression( N_aryExpressionType t, Expression_t l, Expression_t r ): Expression( Expression::N_ARY ),
		n_ary_expression_type( t ) {
		items += l, r;
	}

	ExpressionList_t		items;
};

class PlusExpression: public N_aryExpression {
public:
	PlusExpression(): N_aryExpression( N_aryExpression::PLUS )
	{}

	PlusExpression( Expression_t l, Expression_t r ): N_aryExpression( N_aryExpression::PLUS, l, r )
	{}
};

class MulExpression: public N_aryExpression {
public:
	MulExpression(): N_aryExpression( N_aryExpression::MUL )
	{}

	MulExpression( Expression_t l, Expression_t r ): N_aryExpression( N_aryExpression::MUL, l, r )
	{}
};

class EqualsExpression: public N_aryExpression {
public:
	EqualsExpression(): N_aryExpression( N_aryExpression::EQUALS )
	{}

	EqualsExpression( Expression_t l, Expression_t r ): N_aryExpression( N_aryExpression::EQUALS, l, r )
	{}
};

/////////////////////////////////////////////////////////////////////////
// Base class and derived implementations for variable modifiers
/////////////////////////////////////////////////////////////////////////
class VariableDeclaration: public Base {
public:
	enum VariableDeclarationType { CONSTANT, VARIABLE, FUNCTION };
	VariableDeclarationType variable_declaration_type;

	VariableDeclaration( Identifier id, VariableDeclarationType t ): Base( Base::VARIABLE_DECLARATION ), 
		variable_declaration_type( t ), ident( id.ident )
	{}

	ExpressionList_t constraints;
	std::string ident;
};

class ConstantVariableDeclaration: public VariableDeclaration {
public:
	ConstantVariableDeclaration( Identifier id ): VariableDeclaration( id, VariableDeclaration::CONSTANT )
	{}
};

class VariableVariableDeclaration: public VariableDeclaration {
public:
	VariableVariableDeclaration( Identifier id ): VariableDeclaration( id, VariableDeclaration::VARIABLE )
	{}
};

class FunctionVariableDeclaration: public VariableDeclaration {
public:
	FunctionVariableDeclaration( Identifier id, IdentifierList_t args ): 
		VariableDeclaration( id, VariableDeclaration::FUNCTION ), arguments( args )
	{}

	IdentifierList_t arguments;
};

typedef boost::variant< ConstantVariableDeclaration, VariableVariableDeclaration, FunctionVariableDeclaration > 
	VariableDeclaration_t;
typedef std::vector< VariableDeclaration_t > VariableDeclarationList_t;

/////////////////////////////////////////////////////////////////////////
// Base class and derived implementations for qualifiers
/////////////////////////////////////////////////////////////////////////
class Qualifier: public Base {
public:
	enum QualifierType { GIVEN, WITH, IN };
	QualifierType qualifier_type;

	Qualifier( QualifierType t ): Base( Base::QUALIFIER ), qualifier_type( t )
	{}
};

class GivenQualifier: public Qualifier {
public:
	GivenQualifier( Expression_t e ): Qualifier( Qualifier::GIVEN ), exp( e )
	{}

	Expression_t exp;
};

class WithQualifier: public Qualifier {
public:
	WithQualifier( VariableDeclarationList_t vars ): Qualifier( Qualifier::WITH ), variables( vars )
	{}

	VariableDeclarationList_t variables;
};

class InQualifier: public Qualifier {
public:
	InQualifier( Expression_t e ): Qualifier( Qualifier::IN ), exp( e )
	{}

	Expression_t exp;
};

typedef boost::variant< GivenQualifier, WithQualifier, InQualifier > Qualifier_t;
typedef std::vector< Qualifier_t > QualifierList_t;

/////////////////////////////////////////////////////////////////////////
// Derived implementations for statements
/////////////////////////////////////////////////////////////////////////
class Statement: public Base {
public:
	enum StatementType { VARDECL, ASSIGNMENT, EXPRESSION };
	StatementType statement_type;

	Statement( StatementType t ): Base( Base::STATEMENT ), statement_type( t )
	{}
};

class ExpressionStatement: public Statement {
public:
	ExpressionStatement(): Statement( Statement::EXPRESSION )
	{}

	explicit ExpressionStatement( Expression_t e ):
		Statement( Statement::EXPRESSION ), exp( e )
	{}

	Expression_t		exp;
	QualifierList_t		qualifiers;	
};

typedef boost::variant< ExpressionStatement > Statement_t;
typedef std::vector< Statement_t > StatementList_t;

typedef boost::variant< Identifier, Constant_t, IdentifierList_t, ConstantList_t,
	Statement_t, Qualifier_t, VariableDeclaration_t, Expression_t,
	StatementList_t, QualifierList_t, VariableDeclarationList_t, ExpressionList_t > 
		AST_t;

typedef boost::mpl::vector<Identifier, Constant_t, Statement_t, Qualifier_t, VariableDeclaration_t, Expression_t> Base_t;
typedef boost::mpl::vector<IdentifierList_t, ConstantList_t, StatementList_t, QualifierList_t, 
	VariableDeclarationList_t, ExpressionList_t> List_t;

}

class PrintVisitor {
private:
	std::ostream& out;

	void handle_unary( const AST::UnaryExpression& exp, const char* op ) const;
	void handle_binary( const AST::BinaryExpression& exp, const char* op ) const;
	void handle_n_ary( const AST::N_aryExpression& exp, const char* op ) const;

public:
	typedef void result_type;
	PrintVisitor( std::ostream& o ): out( o )
	{}

	void operator ()( const AST::Statement_t& s ) const						{ apply_visitor( *this, s );	 }
	void operator ()( const AST::ExpressionStatement& s ) const;

	void operator ()( const AST::Qualifier_t& q ) const						{ apply_visitor( *this, q );	 }
	void operator ()( const AST::GivenQualifier& q ) const;
	void operator ()( const AST::WithQualifier& q ) const;
	void operator ()( const AST::InQualifier& q ) const;

	void operator ()( const AST::VariableDeclaration_t& v ) const			{ apply_visitor( *this, v );	 }
	void operator ()( const AST::ConstantVariableDeclaration& v ) const;
	void operator ()( const AST::VariableVariableDeclaration& v ) const;
	void operator ()( const AST::FunctionVariableDeclaration& v ) const;

	void operator ()( const AST::IdentifierExpression& exp ) const 			{ out << exp.ident;				 }
	void operator ()( const AST::ConstantExpression_t& exp ) const			{ apply_visitor( *this, exp );	 }
	void operator ()( const AST::BooleanConstantExpression& exp ) const		{ out << exp.value;				 }
	void operator ()( const AST::IntegerConstantExpression& exp ) const		{ out << exp.value;				 }
	void operator ()( const AST::DoubleConstantExpression& exp ) const		{ out << exp.value;				 }
	void operator ()( const AST::CallExpression& exp ) const;

	void operator ()( const AST::NegateExpression& exp ) const				{ handle_unary( exp, "-" );		 }
	void operator ()( const AST::ReciprocalExpression& exp ) const			{ handle_unary( exp, "1.0 / " ); }

	void operator ()( const AST::MinusExpression& exp ) const				{ handle_binary( exp, "-" );	 }
	void operator ()( const AST::DivExpression& exp ) const					{ handle_binary( exp, "/" );	 }
	void operator ()( const AST::PowExpression& exp ) const					{ handle_binary( exp, "**" );	 }

	void operator ()( const AST::MulExpression& exp ) const					{ handle_n_ary( exp, "*" );		 }
	void operator ()( const AST::PlusExpression& exp ) const				{ handle_n_ary( exp, "+" );		 }
	void operator ()( const AST::EqualsExpression& exp ) const				{ handle_n_ary( exp, "=" );		 }

};

namespace AST {

template< typename T >
typename boost::enable_if< boost::is_base_of<Base,T>, std::ostream& >::type 
operator <<( std::ostream& o, const T& b ) {
	PrintVisitor p( o );
	p( b );
	return o;
}

}

template< typename T > struct IsEqual 		{ const static bool value = false; };

#define Start typedef boost::mpl::vector_c< int, 
#define End > type
template< typename T > struct ExpressionTypeMap {};
template<> struct ExpressionTypeMap<AST::IdentifierExpression> 	{ Start AST::Expression::IDENTIFIER End; };
template<> struct ExpressionTypeMap<AST::ConstantExpression> 	{ Start AST::Expression::CONSTANT End; };
template<> struct ExpressionTypeMap<AST::CallExpression> 		{ Start AST::Expression::CALL End; };
template<> struct ExpressionTypeMap<AST::NegateExpression> 		{ Start AST::Expression::UNARY, AST::UnaryExpression::NEGATE End; };
#undef End
#undef Start

template< typename seq1, typename seq2 >
struct lexicographical_compare {

	typedef boost::mpl::unpack_args<
		boost::mpl::if_< boost::mpl::less< boost::mpl::_1, boost::mpl::_2 >, 
			boost::mpl::true_,
			boost::mpl::if_< boost::mpl::less< boost::mpl::_2, boost::mpl::_1 >, 
				boost::mpl::false_,
				boost::mpl::void_ > > 
		> compare_;

	typedef typename boost::mpl::fold<
		boost::mpl::zip_view< boost::mpl::vector< seq1, seq2 > >,
		boost::mpl::void_,
		boost::mpl::if_< boost::is_same< boost::mpl::_1, boost::mpl::void_ >, 
			compare_::apply< boost::mpl::_2 >,
			boost::mpl::_1 > 
		>::type compare_list_;

	typedef typename boost::mpl::if_< boost::is_same< compare_list_, boost::mpl::void_ >,
			typename boost::mpl::less< typename boost::mpl::size< seq1 >::type, typename boost::mpl::size< seq2 >::type >::type,
			compare_list_ 
		>::type type;

	const static bool value = type::value;	
};

template< typename Compare, typename EqualCompare = IsEqual<Compare> >
class CompareVisitor {
public:
	typedef bool result_type;

	//typedef typename boost::mpl::if_c< EqualCompare::value,
	//	std::equals, std::lexicographical_compare >::type list_compare;

	template< typename T, typename U >
	typename boost::enable_if_c< EqualCompare::value && !boost::is_same<T,U>::value, bool >::type
	operator ()( const T& lhs, const U& rhs ) {
		return false;
	}

	template< typename T, typename U >
	typename boost::disable_if_c< EqualCompare::value || boost::is_same<T,U>::value, bool >::type
	operator ()( const T& lhs, const U& rhs ) {
		return lexicographical_compare< typename ExpressionTypeMap<T>::type, typename ExpressionTypeMap<U>::type >::value;
	}

	bool operator ()( const AST::IdentifierExpression& lhs, const AST::IdentifierExpression& rhs ) {
		return Compare()( lhs.ident, rhs.ident );
	}

	bool operator ()( const AST::ConstantExpression_t& lhs, const AST::ConstantExpression_t& rhs ) {
		return apply_visitor(*this, lhs, rhs);
	}

	template< typename T >
	bool operator ()( const AST::ConstantExpressionBase<T>& lhs, const AST::ConstantExpressionBase<T>& rhs ) {
		return Compare()( lhs.value, rhs.value );
	}

	bool operator ()( const AST::CallExpression& lhs, const AST::CallExpression& rhs ) {
		if( lhs.func != rhs.func )	return false;
		return std::equal( lhs.arguments.begin(), lhs.arguments.end(), rhs.arguments.begin(), apply_visitor(*this) );
	}

	template< typename T >
	typename boost::enable_if< boost::is_base_of<AST::UnaryExpression,T>, bool >::type
	operator ()( const T& lhs, const T& rhs ) {
		return apply_visitor(*this, lhs.right, rhs.right);
	}

	template< typename T >
	typename boost::enable_if< boost::is_base_of<AST::BinaryExpression,T>, bool >::type
	operator ()( const T& lhs, const T& rhs ) {
		return apply_visitor(*this, lhs.left, rhs.left) && apply_visitor(*this, lhs.right, rhs.right);
	}

	template< typename T >
	typename boost::enable_if< boost::is_base_of<AST::N_aryExpression,T>, bool >::type
	operator ()( const T& lhs, const T& rhs ) {
		return std::equal( lhs.items.begin(), lhs.items.end(), rhs.items.begin(), apply_visitor(*this) );
	}
};

struct EqualTo {
	template< typename T >
	bool operator ()( const T& lhs, const T& rhs ) { 
		return lhs == rhs; 
	}
};

struct LessThan {
	template< typename T >
	bool operator ()( const T& lhs, const T& rhs ) { 
		return lhs < rhs; 
	}
};

template<> struct IsEqual< EqualTo > 	{ const static bool value = true; };
typedef CompareVisitor< EqualTo > EqualVisitor;
typedef CompareVisitor< LessThan > LessThanVisitor;

namespace AST {

template< typename T>
typename boost::enable_if< boost::is_base_of<Base,T>, bool>::type
operator ==( const T& lhs, const T& rhs ) {
	EqualVisitor eq;
	return eq( lhs, rhs );
}

template< typename T>
typename boost::enable_if< boost::is_base_of<Base,T>, bool>::type
operator <( const T& lhs, const T& rhs ) {
	LessThanVisitor lt;
	return lt( lhs, rhs );
}

}

#endif

