
#ifndef DIFF_VISITOR__H
#define DIFF_VISITOR__H

#include "syntax_types.h"

class DiffVisitor {
public:
	typedef AST::Expression_t result_type;

	AST::Expression_t operator ()( AST::IdentifierExpression& exp ) const;
	AST::Expression_t operator ()( AST::ConstantExpression_t& exp ) const		{ return apply_visitor(*this, exp); }

	template< typename T >
	typename boost::enable_if< boost::is_arithmetic<T>, Expression_t >::type
	operator ()( AST::ConstantExpressionBase<T> exp ) const {
		return AST::ConstantExpressionBase<T>( T(0) );
	}

	AST::Expression_t operator ()( AST::CallExpression& exp ) const;
	AST::Expression_t operator ()( AST::NegateExpression& exp ) const;
	AST::Expression_t operator ()( AST::ReciprocalExpression& exp ) const;

	AST::Expression_t operator ()( AST::MinusExpression& exp ) const;
	AST::Expression_t operator ()( AST::DivExpression& exp ) const;
	AST::Expression_t operator ()( AST::PowExpression& exp ) const;

	AST::Expression_t operator ()( AST::MulExpression& exp ) const;
	AST::Expression_t operator ()( AST::PlusExpression& exp ) const;
	AST::Expression_t operator ()( AST::EqualsExpression& exp ) const;
};

AST::Expression_t d( AST::Expression_t exp );
#endif
