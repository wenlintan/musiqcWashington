
#include <gtest/gtest.h>
#include "syntax_types.h"
using namespace AST;

#include <boost/mpl/vector_c.hpp>
using namespace boost::mpl;

TEST( lexicographical_compare, SimpleTests ) {
	typedef lexicographical_compare< vector_c< int, 1 >, vector_c< int, 2 > > t1;
	typedef lexicographical_compare< vector_c< int, 1, 1 >, vector_c< int, 1, 2 > > t2;
	typedef lexicographical_compare< vector_c< int, 1, 1, 1, 1 >, vector_c< int, 1, 1, 6, 1 > > t3;

	EXPECT_TRUE( t1::value );	EXPECT_TRUE( t2::value );	EXPECT_TRUE( t3::value );

	typedef lexicographical_compare< vector_c< int, 2 >, vector_c< int, 1 > > rt1;
	typedef lexicographical_compare< vector_c< int, 1, 2 >, vector_c< int, 1, 1 > > rt2;
	typedef lexicographical_compare< vector_c< int, 1, 1, 8, 1 >, vector_c< int, 1, 1, 1, 1 > > rt3;

	EXPECT_FALSE( rt1::value );	EXPECT_FALSE( rt2::value );	EXPECT_FALSE( rt3::value );
}

TEST( lexicographical_compare, SizeTests ) {

	typedef lexicographical_compare< vector_c< int, 1 >, vector_c< int, 1, 2 > > t1;
	typedef lexicographical_compare< vector_c< int, 1 >, vector_c< int, 1, 0 > > t2;
	EXPECT_TRUE( t1::value );	EXPECT_TRUE( t2::value );

/*
	typedef lexicographical_compare< vector_c< int, 1, 3, 1 >, vector_c< int, 1, 2 > > rt1;
	typedef lexicographical_compare< vector_c< int, 1, 0, 10 >, vector_c< int, 1, 0 > > rt2;
	EXPECT_FALSE( rt1::value );	EXPECT_FALSE( rt2::value );
*/
}

TEST( lexicographical_compare, EqualTests ) {
	typedef lexicographical_compare< vector_c< int, 1, 9, 0 >, vector_c< int, 1, 9, 0 > > t1;
	EXPECT_FALSE( t1::value );
}

template< typename T >
Expression_t c( T val ) {
	return ConstantExpressionBase<T>( val );
}

TEST( EqualVisitor, ConstantTests ) {
	EqualVisitor eq;
	EXPECT_TRUE( eq( BooleanConstantExpression(true), BooleanConstantExpression(true) ) );
	EXPECT_TRUE( eq( IntegerConstantExpression(10), IntegerConstantExpression(10) ) );
	EXPECT_TRUE( eq( DoubleConstantExpression(3.), DoubleConstantExpression(3.) ) );
	EXPECT_TRUE( eq( DoubleConstantExpression(4./3.), DoubleConstantExpression((0.5+1/6.)*2.) ) );

	EXPECT_FALSE( eq( BooleanConstantExpression(false), BooleanConstantExpression(true) ) );
	EXPECT_FALSE( eq( IntegerConstantExpression(100), IntegerConstantExpression(10) ) );
	EXPECT_FALSE( eq( DoubleConstantExpression(30.), DoubleConstantExpression(3.) ) );
	EXPECT_FALSE( eq( DoubleConstantExpression(40./3.), DoubleConstantExpression((0.5+1/6.)*2.) ) );
}

TEST( EqualVisitor, N_aryTests ) {
	EqualVisitor eq;
	EXPECT_TRUE( eq( PlusExpression( c(3.), c(4.) ), PlusExpression( c(3.), c(4.) ) ) );
	EXPECT_TRUE( eq( PlusExpression( c(3.), c(4.) ), PlusExpression( c(3.), c(4.) ) ) );
	EXPECT_TRUE( eq( PlusExpression( c(3.), c(4.) ), PlusExpression( c(3.), c(4.) ) ) );
}

TEST( LessThanVisitor, ConstantTests ) {
	LessThanVisitor lt;
	EXPECT_TRUE( lt( IntegerConstantExpression(10), IntegerConstantExpression(32) ) );
	EXPECT_TRUE( lt( DoubleConstantExpression(3.), DoubleConstantExpression(30.) ) );
	EXPECT_TRUE( lt( DoubleConstantExpression(4./3.), DoubleConstantExpression(6.) ) );

	EXPECT_FALSE( lt( IntegerConstantExpression(100), IntegerConstantExpression(10) ) );
	EXPECT_FALSE( lt( DoubleConstantExpression(30.), DoubleConstantExpression(3.) ) );
	EXPECT_FALSE( lt( DoubleConstantExpression(40./3.), DoubleConstantExpression(1/3.) ) );
}





