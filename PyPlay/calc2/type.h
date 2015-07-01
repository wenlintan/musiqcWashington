
#ifndef TYPE__H
#define TYPE__H

#if 0
#include <vector>

#include <boost/variant.hpp>
#include <boost/mpl/vector.hpp>
#include <boost/mpl/insert_range.hpp>
#include <boost/mpl/transform.hpp>
#include <boost/mpl/lambda.hpp>

#pragma once

namespace Type {

struct Any {};

struct Bool {};
struct Integer {};
struct Unsigned {};
struct Double {};
struct Complex {};
typedef boost::mpl::vector< Bool, Integer, Unsigned, Double, Complex > BuiltinTypes;
typedef boost::make_variant_over< BuiltinTypes >::type Builtin_t;

struct Constant	{ Builtin_t value; };
struct Variable	{ Builtin_t value; };

struct Distance {};
struct Mass {};
struct Time {};
struct Current {};
struct Temperature {};
struct Intensity {};
struct Quantity {};
typedef boost::mpl::vector< Distance, Mass, Time, Current, Temperature, Intensity, Quantity > UnitTypes;
typedef boost::make_variant_over< UnitTypes >::type Unit_t;

template< typename Base >
struct Unit	{ Base base;	Unit_t unit; };

struct Function;

struct create_recursive_wrapper {
	template< typename T > struct apply { typedef boost::recursive_wrapper<T> type; };
};

typedef boost::mpl::lambda< create_recursive_wrapper >::type recursive_wrapper_lambda;

typedef boost::mpl::vector< Constant, Variable, Unit<Constant>, Unit<Variable> > BaseTypes;
typedef boost::mpl::vector< Function > DerivedTypes;
typedef boost::mpl::transform< DerivedTypes, recursive_wrapper_lambda >::type WrappedTypes;

typedef boost::mpl::insert_range< BaseTypes, boost::mpl::end<BaseTypes>::type, WrappedTypes >::type Types;
typedef boost::make_variant_over<Types>::type Type_t;

struct Function {
	Type_t	from, to;
};

}
#endif

#endif