
#include "diff_visitor.h"
using namespace AST;

template< typename T >
typename boost::enable_if< boost::is_arithmetic<T>, Expression_t >::type operator ()( T& v ) {
	return AST::ConstantExpressionBase<T>( v );
}

Expression_t d( ExpressionList_t args ) {
	return CallExpression( "d", args );
}

Expression_t DiffVisitor::operator ()( IdentifierExpression& exp ) const {
	ExpressionList_t args( 1, exp );
	return d( args );
}

Expression_t DiffVisitor::operator ()( CallExpression& exp ) const {
	return exp;
}

Expression_t DiffVisitor::operator ()( NegateExpression& exp ) const {
	return NegateExpression( apply_visitor( *this, exp.right ) );
}

Expression_t DiffVisitor::operator ()( ReciprocalExpression& exp ) const {
	return NegateExpression( MulExpression( 
			ReciprocalExpression( PowExpression( exp, c(2) ) ),
			apply_visitor( *this, exp ) )
		);
}

Expression_t DiffVisitor::operator ()( MinusExpression& exp ) const {
	return MinusExpression( apply_visitor(*this, exp.left), apply_visitor(*this, exp.right) );
}

Expression_t DiffVisitor::operator ()( DivExpression& exp ) const {
	return apply_visitor( *this, MulExpression( exp.left, ReciprocalExpression( exp.right ) ) );
}

Expression_t DiffVisitor::operator ()( PowExpression& exp ) const {
	return PlusExpression( 
		MulExpression( 
			MulExpression( 
				CallExpression( "ln", ExpressionList_t( 1, exp.left ) ), 
				exp ), 
			),
			apply_visitor(*this, exp.right)
		), MulExpression(
			MulExpression(
				exp.right,
				PowExpression( exp.left, MinusExpression( exp.right, IntegerConstantExpression(1) ) )
			),
			apply_visitor(*this, exp.left);
		)
	); 
}

Expression_t DiffVisitor::operator ()( MulExpression& exp ) const {
	PlusExpression result;
	for( size_t i = 0; i < exp.items.size(); ++i ) {
		MulExpression new_exp = exp;
		new_exp[ i ] = apply_visitor( *this, new_exp[i] );
		result.items.push_back( new_exp );
	}
	return result;
}

Expression_t DiffVisitor::operator ()( PlusExpression& exp ) const {
	PlusExpression result;
	std::transform( exp.items.begin(), exp.items.end(), result.items.begin(), apply_visitor(*this) );
	return result;
}

Expression_t DiffVisitor::operator ()( EqualsExpression& exp ) const {
	std::transform( exp.items.begin(), exp.items.end(), apply_visitor(*this) );
}



