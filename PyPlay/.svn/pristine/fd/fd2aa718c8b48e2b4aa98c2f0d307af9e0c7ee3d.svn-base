
#ifndef OBJECT__H
#define OBJECT__H

#pragma once

namespace Object {

typedef std::string Identifier;
typedef bool Boolean;

struct Integer {
	
};

struct Rational {

};

struct Irrational {

};

struct Negate {};
struct Reciprocal {};

template< typename Op > struct UnaryExprObject;
typedef UnaryExpr< Negate > NegateObject;
typedef UnaryExpr< Reciprocal > RecipObject;

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

template< typename Op > struct ExprObject;
typedef ExprObject< Plus > PlusObject;
typedef ExprObject< Minus > MinusObject;
typedef ExprObject< Mul > MulObject;
typedef ExprObject< Div > DivObject;
typedef ExprObject< Pow > PowObject;
typedef ExprObject< Assign > AssignObject;

typedef ExprObject< Eq > EqObject;
typedef ExprObject< Lt > LtObject;
typedef ExprObject< Gt > GtObject;
typedef ExprObject< Le > LeObject;
typedef ExprObject< Ge > GeObject;

typedef ExprObject< Call > CallObject;
typedef ExprObject< List > ListObject;
typedef ExprObject< Type > TypeObject;

template< typename Op > struct IsUnordered	{ const static bool value = false; }
template<> struct IsUnordered< Plus >		{ const static bool value = true; }
template<> struct IsUnorderer< Mul >		{ const static bool value = true; }


}
#endif