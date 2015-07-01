
#include "matrix.h"

#include <cmath>
#include <gtest/gtest.h>

#include <boost/bind.hpp>
#include <boost/assign.hpp>
using boost::assign::list_of;

TEST( GRBMatrix, ContainerSimpleTest ) {
	matrix<float> data, expect;
	data = matrix<float>::from_container( list_of( list_of(1.f)(2.f) )( list_of(3.f)(4.f) ), 
		boost::bind( static_cast<float(*)(float,float)>(&powf), _1, 2.f ) );

	expect = matrix<float>::from_container( list_of( list_of(1.f)(4.f) )( list_of(9.f)(16.f) ) );
	EXPECT_EQ( data, expect );
}

TEST( GRBMatrix, ColumnMatrixSimpleTest ) {
	matrix<float> data, expect;
	data = matrix<float>::column_from_container( list_of(1.f)(2.f)(3.f), boost::bind( static_cast<float(*)(float,float)>(&powf), _1, 2.f ) );
	expect = matrix<float>::column_from_container( list_of(1.f)(4.f)(9.f) );
	EXPECT_EQ( data, expect );
}

TEST( GRBMatrix, AdditionOperatorsSimpleTest ) {
	matrix<float> one, two, expect;
	one = matrix<float>::from_container( list_of( list_of(1.f)(2.f) )( list_of(3.f)(4.f) ) );
	two = matrix<float>::from_container( list_of( list_of(4.f)(3.f) )( list_of(2.f)(1.f) ) );
	expect = matrix<float>::from_container( list_of( list_of(5.f)(5.f) )( list_of(5.f)(5.f) ) );
	EXPECT_EQ( one+two, expect );

	one += two;
	EXPECT_EQ( one, expect );
}

TEST( GRBMatrix, SubtractionOperatorsSimpleTest ) {
	matrix<float> one, two, expect;
	one = matrix<float>::from_container( list_of( list_of(1.f)(2.f) )( list_of(3.f)(4.f) ) );
	two = matrix<float>::from_container( list_of( list_of(4.f)(3.f) )( list_of(2.f)(1.f) ) );
	expect = matrix<float>::from_container( list_of( list_of(-3.f)(-1.f) )( list_of(1.f)(3.f) ) );
	EXPECT_EQ( one-two, expect );

	one -= two;
	EXPECT_EQ( one, expect );
}

TEST( GRBMatrix, MultiplicationOperatorSimpleTest ) {
	matrix<float> one, two, expect;
	one = matrix<float>::from_container( list_of( list_of(1.f)(2.f) )( list_of(3.f)(4.f) ) );
	two = matrix<float>::from_container( list_of( list_of(4.f)(3.f) )( list_of(2.f)(1.f) ) );
	expect = matrix<float>::from_container( list_of( list_of(8.f)(5.f) )( list_of(20.f)(13.f) ) );
	EXPECT_EQ( one*two, expect );
}

TEST( GRBMatrix, InverseSimpleTest ) {
	matrix<float> data, inverse;
	data = matrix<float>::from_container( list_of( list_of(4.f)(2.f)(2.f) )( list_of(4.f)(6.f)(8.f) )( list_of(-2.f)(2.f)(4.f) ) );
	inverse = matrix<float>::from_container( list_of( list_of(1.f)(-.5f)(.5f) )( list_of(-4.f)(2.5f)(-3.f) )( list_of(2.5f)(-1.5f)(2.f) ) );
	EXPECT_EQ( data.inverse(), inverse );
}
