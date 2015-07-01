
#include <cmath>

#include "simplify_visitor.h"
using namespace AST;

Expression_t OrderVisitor::operator ()( CallExpression& exp ) const {
	for( size_t i = 0; i < exp.arguments.size(); ++i )	apply_visitor(*this, exp.arguments[i]);
	return exp;
}

Expression_t OrderVisitor::operator ()( NegateExpression& exp ) const {
	if( PlusExpression* plus = boost::get<PlusExpression>( &exp.right ) ) {
		PlusExpression new_plus;
		for( size_t i = 0; i < plus->items.size(); ++i )	new_plus.items.push_back( NegateExpression(plus->items[i]) );
		return new_plus;
	}
	return exp;
}

Expression_t OrderVisitor::operator ()( ReciprocalExpression& exp ) const {
	return exp;
}

Expression_t OrderVisitor::operator ()( MinusExpression& exp ) const {
	Expression_t new_negate = NegateExpression( apply_visitor(*this, exp.right) );
	Expression_t new_plus = PlusExpression( apply_visitor(*this, exp.left), new_negate );

	return apply_visitor(*this, new_plus);
}

Expression_t OrderVisitor::operator ()( DivExpression& exp ) const {
	Expression_t new_recip = ReciprocalExpression( apply_visitor(*this, exp.right) );
	Expression_t new_mul = MulExpression( apply_visitor(*this, exp.left), new_recip );

	return apply_visitor(*this, new_mul);
}

Expression_t OrderVisitor::operator ()( PowExpression& exp ) const {
	return exp;
}

Expression_t OrderVisitor::operator ()( PlusExpression& exp ) const {
	return handle_n_ary_expression( exp );
}

Expression_t OrderVisitor::operator ()( MulExpression& exp ) const {
	return handle_n_ary_expression( exp );
}

Expression_t OrderVisitor::operator ()( EqualsExpression& exp ) const {
	return handle_n_ary_expression( exp );
}

////////////////////////////////////////////////////////////////////////////////////
// SimplifyVisitor
////////////////////////////////////////////////////////////////////////////////////
Expression_t SimplifyVisitor::operator ()( CallExpression& exp ) const {
	for( size_t i = 0; i < exp.arguments.size(); ++i )	apply_visitor(*this, exp.arguments[i]);
	return exp;
}

static double negate( double d ) { return -d; };
static double recip( double d ) { return 1.0 / d; }
static double plus( double o, double t ) { return o + t; }
static double minus( double o, double t ) { return o - t; }
static double mul( double o, double t ) { return o * t; }
static double div( double o, double t ) { return o / t; }
// use pow from cmath

Expression_t SimplifyVisitor::operator ()( NegateExpression& exp ) const {
	return simplify_unary( exp, negate );
}	

Expression_t SimplifyVisitor::operator ()( ReciprocalExpression& exp ) const {
	return simplify_unary( exp, recip );
}

Expression_t SimplifyVisitor::operator ()( MinusExpression& exp ) const {
	return simplify_binary( exp, minus );
}

Expression_t SimplifyVisitor::operator ()( DivExpression& exp ) const {
	return simplify_binary( exp, div );
}

Expression_t SimplifyVisitor::operator ()( PowExpression& exp ) const {
	return simplify_binary( exp, pow );
}


