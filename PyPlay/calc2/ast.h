
#ifndef AST__H
#define AST__H

#pragma once

#include <string>
#include <iostream>
#include <algorithm>
#include <vector>

#include <boost/variant.hpp>
#include <boost/optional.hpp>

#define BOOST_MPL_CFG_NO_PREPROCESSED_HEADERS
#define BOOST_MPL_LIMIT_VECTOR_SIZE 30

#include <boost/mpl/vector.hpp>
#include <boost/mpl/insert_range.hpp>
#include <boost/mpl/transform.hpp>
#include <boost/mpl/lambda.hpp>

namespace AST {

// Detail functions
namespace detail {

// Detail function to print list with separator
template< typename T, typename Sep >
void print_list( std::ostream& os, const std::vector<T>& list, Sep sep ) {
	if( !list.size() )	return;
	for( std::vector<T>::size_type i = 0; i < list.size() -1; ++i )	os << list[ i ] << sep;
	os << list.back();
}

}

/////////////////////////////////////////////////////////////////////////////////////////////////////////
// Basic Types
/////////////////////////////////////////////////////////////////////////////////////////////////////////

// Identifier
typedef std::string BaseIdentifier_t;
struct Identifier {
	Identifier()											{}
	Identifier( const BaseIdentifier_t& val ): id( val )	{}

	template< typename Iterator >
	Identifier( Iterator begin, Iterator end ): id( begin, end )		{}

	BaseIdentifier_t id;
};
typedef std::vector< Identifier > IdentifierList_t;
std::ostream& operator << ( std::ostream& os, const Identifier& id );
bool operator < ( const Identifier& lhs, const Identifier& rhs );
bool operator == ( const Identifier& lhs, const Identifier& rhs );

// Constant
enum ConstantType { BOOLEAN, INTEGER, DOUBLE, COMPLEX };
template< typename T > struct ConstantTypeMap {};

typedef boost::mpl::vector< bool, int, double > ConstantBaseTypes;
template<> struct ConstantTypeMap<bool>		{ const static ConstantType value = BOOLEAN; };
template<> struct ConstantTypeMap<int> 		{ const static ConstantType value = INTEGER; };
template<> struct ConstantTypeMap<double> 	{ const static ConstantType value = DOUBLE; };

template< typename T > struct Constant {
	Constant(): type( ConstantTypeMap<T>::value )							{}
	Constant( const T& v ): type( ConstantTypeMap<T>::value ), value( v )	{}

	ConstantType type;
	T value;
};
typedef boost::mpl::transform< ConstantBaseTypes, Constant<boost::mpl::_1> >::type ConstantTypes;
typedef boost::make_variant_over< ConstantTypes >::type Constant_t;

std::ostream& operator << ( std::ostream& os, const Constant<bool>& c );

template< typename T >
std::ostream& operator << ( std::ostream& os, const Constant<T>& c ) {
	os << c.value;
	return os;
}

template< typename T >
bool operator < ( const Constant<T>& lhs, const Constant<T>& rhs ) {
	return lhs.value < rhs.value;
}

template< typename T >
bool operator == ( const Constant<T>& lhs, const Constant<T>& rhs ) {
	return lhs.value == rhs.value;
}

// UnitConstant
struct UnitConstant {
	UnitConstant()																				{}
	UnitConstant( const Constant_t& c, const BaseIdentifier_t& u ): constant( c ), unit( u )	{}

	Constant_t			constant;
	BaseIdentifier_t	unit;
};
std::ostream& operator << ( std::ostream& os, const UnitConstant& c );
bool operator < ( const UnitConstant& lhs, const UnitConstant& rhs );
bool operator == ( const UnitConstant& lhs, const UnitConstant& rhs );

typedef boost::mpl::push_back<
		boost::mpl::push_front< ConstantTypes, Identifier >::type,
		UnitConstant 
	>::type BaseTypes;

typedef boost::make_variant_over< BaseTypes >::type Base_t;

/////////////////////////////////////////////////////////////////////////////////////////////////////////
// Expression Types
/////////////////////////////////////////////////////////////////////////////////////////////////////////

// All Base types are valid expression types
typedef BaseTypes BaseExprTypes;

// Forward declare recursive expression types
struct IfExpr;
struct LambdaExpr;
struct LetExpr;
struct MatchExpr;

struct Negate {};
struct Reciprocal {};

template< typename Op > struct UnaryExpr;
typedef UnaryExpr< Negate > NegateExpr;
typedef UnaryExpr< Reciprocal > RecipExpr;

struct Plus {};
struct Minus {};
struct Mul {};
struct Div {};
struct Pow {};
struct Assign {};

struct Eq {};
struct Lt {};
struct Gt {};
struct Le {};
struct Ge {};

struct Call {};
struct List {};
struct Type {};

template< typename Op > struct BinaryExpr;
typedef BinaryExpr< Plus > PlusExpr;
typedef BinaryExpr< Minus > MinusExpr;
typedef BinaryExpr< Mul > MulExpr;
typedef BinaryExpr< Div > DivExpr;
typedef BinaryExpr< Pow > PowExpr;
typedef BinaryExpr< Assign > AssignExpr;

typedef BinaryExpr< Eq > EqExpr;
typedef BinaryExpr< Lt > LtExpr;
typedef BinaryExpr< Gt > GtExpr;
typedef BinaryExpr< Le > LeExpr;
typedef BinaryExpr< Ge > GeExpr;

typedef BinaryExpr< Call > CallExpr;
typedef BinaryExpr< List > ListExpr;
typedef BinaryExpr< Type > TypeExpr;

typedef boost::mpl::vector< 
		IfExpr, LambdaExpr, LetExpr, MatchExpr,
		NegateExpr, RecipExpr, 
		PlusExpr, MinusExpr, MulExpr, DivExpr, PowExpr, AssignExpr, 
		EqExpr, LtExpr, GtExpr, LeExpr, GeExpr,
		CallExpr, ListExpr, TypeExpr
	> RecursiveExprBaseTypes;

struct create_recursive_wrapper {
	template< typename T > struct apply { typedef boost::recursive_wrapper<T> type; };
};

typedef boost::mpl::transform< 
		RecursiveExprBaseTypes, 
		boost::mpl::lambda< create_recursive_wrapper >::type 
	>::type RecursiveExprWrappedTypes;

typedef boost::mpl::insert_range< 
		RecursiveExprWrappedTypes, 
		boost::mpl::begin< RecursiveExprWrappedTypes >::type,
		BaseExprTypes 
	>::type ExprTypes;

typedef boost::make_variant_over< ExprTypes >::type Expr_t;
typedef std::vector<Expr_t> ExprList_t;

Expr_t expr_from_base( const Base_t& b );
Expr_t normalize_expr( const Expr_t& e );

struct IfExpr {
	Expr_t	if_, then;
	boost::optional<Expr_t>	else_;
};
std::ostream& operator << ( std::ostream& os, const IfExpr& if_ );
bool operator < ( const IfExpr& lhs, const IfExpr& rhs );
bool operator == ( const IfExpr& lhs, const IfExpr& rhs );

struct LambdaExpr {
	LambdaExpr()																		{}
	LambdaExpr( const IdentifierList_t& a, const Expr_t& r ): args( a ), result( r )	{}

	IdentifierList_t	args;
	Expr_t	result;
};
std::ostream& operator << ( std::ostream& os, const LambdaExpr& lam );
bool operator < ( const LambdaExpr& lhs, const LambdaExpr& rhs );
bool operator == ( const LambdaExpr& lhs, const LambdaExpr& rhs );

struct LetExpr {
	LetExpr()		{}
	LetExpr( const Expr_t& in_ ): in( in_ )		{}

	ExprList_t	bindings;
	Expr_t		in;
};
std::ostream& operator << ( std::ostream& os, const LetExpr& let );
bool operator < ( const LetExpr& lhs, const LetExpr& rhs );
bool operator == ( const LetExpr& lhs, const LetExpr& rhs );

struct MatchExpr {
	struct Match {
		Expr_t	with;
		Expr_t	in;
		boost::optional<Expr_t>	when;
	};
	typedef std::vector<Match> MatchList_t;

	Expr_t			val;
	MatchList_t		matches;
};
std::ostream& operator << ( std::ostream& os, const MatchExpr::Match& match );
std::ostream& operator << ( std::ostream& os, const MatchExpr& match );
bool operator < ( const MatchExpr::Match& lhs, const MatchExpr::Match& rhs );
bool operator < ( const MatchExpr& lhs, const MatchExpr& rhs );
bool operator == ( const MatchExpr::Match& lhs, const MatchExpr::Match& rhs );
bool operator == ( const MatchExpr& lhs, const MatchExpr& rhs );

template< typename Op >
struct UnaryExpr {
	UnaryExpr()									{}
	UnaryExpr( const Expr_t& l ): left( l )		{}
	Expr_t	left;
};

template< typename Op >
bool operator < ( const UnaryExpr<Op>& lhs, const UnaryExpr<Op>& rhs ) {
	return lhs.left < rhs.left;
}

template< typename Op >
bool operator == ( const UnaryExpr<Op>& lhs, const UnaryExpr<Op>& rhs ) {
	return lhs.left == rhs.left;
}

std::ostream& operator << ( std::ostream& os, const NegateExpr& neg );
std::ostream& operator << ( std::ostream& os, const RecipExpr& rec );
typedef boost::mpl::vector< NegateExpr, RecipExpr > UnaryExprTypes;

template< typename Op >
struct BinaryExpr {
	BinaryExpr()																{}
	BinaryExpr( const Expr_t& l, const Expr_t& r ): left( l ), right( r )		{}
	Expr_t	left, right;
};

template< typename Op > struct BinaryNotationMap {};
template<> struct BinaryNotationMap< Plus >		{ const static char value = '+'; };
template<> struct BinaryNotationMap< Minus >	{ const static char value = '-'; };
template<> struct BinaryNotationMap< Mul >		{ const static char value = '*'; };
template<> struct BinaryNotationMap< Div >		{ const static char value = '/'; };
template<> struct BinaryNotationMap< Pow >		{ const static char* value; };
template<> struct BinaryNotationMap< Assign >	{ const static char value = '='; };

template<> struct BinaryNotationMap< Eq >		{ const static char* value; };
template<> struct BinaryNotationMap< Lt >		{ const static char value = '<'; };
template<> struct BinaryNotationMap< Gt >		{ const static char value = '<'; };
template<> struct BinaryNotationMap< Le >		{ const static char* value; };
template<> struct BinaryNotationMap< Ge >		{ const static char* value; };

template<> struct BinaryNotationMap< Call >		{ const static char value = ' '; };
template<> struct BinaryNotationMap< List >		{ const static char value = ','; };
template<> struct BinaryNotationMap< Type >		{ const static char value = ':'; };

template< typename Op >
bool operator < ( const BinaryExpr<Op>& lhs, const BinaryExpr<Op>& rhs ) {
	return lhs.left < rhs.left || ( !(rhs.left < lhs.left) && lhs.right < rhs.right );
}

template< typename Op >
bool operator == ( const BinaryExpr<Op>& lhs, const BinaryExpr<Op>& rhs ) {
	return lhs.left == rhs.left && lhs.right == rhs.right;
}

template< typename Op >
std::ostream& operator << ( std::ostream& os, const BinaryExpr<Op>& expr ) {
	os << '(' << expr.left << BinaryNotationMap<Op>::value << expr.right << ')';
	return os;
}

}

#endif