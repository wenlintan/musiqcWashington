
#ifndef SIMPLIFY_VISITOR__H
#define SIMPLIFY_VISITOR__H
#include "syntax_types.h"

class OrderVisitor {
private:
	template< typename T >
	struct ExpressionBuilder {
		ExpressionBuilder( std::vector<AST::Expression_t>& data ): v(data) {}

		void operator ()( AST::Expression_t e ) {
			AST::Expression_t exp = apply_visitor( OrderVisitor(), e );
			if( T* t = boost::get<T>( &exp ) )	v.insert( v.end(), t->items.begin(), t->items.end() );
			else								v.push_back( exp );
		}

		std::vector<AST::Expression_t>& v;
	};

	template< typename T >
	T handle_n_ary_expression( T& exp ) const {
		T new_exp;
		std::for_each( exp.items.begin(), exp.items.end(), ExpressionBuilder<T>( new_exp.items ) );
		//std::sort( new_exp.items.begin(), new_exp.items.end(), LessThanVisitor() );
		return new_exp;
	}

public:
	typedef AST::Expression_t result_type;
	AST::Expression_t operator ()( AST::IdentifierExpression& exp ) const		{ return exp; }

	AST::Expression_t operator ()( AST::ConstantExpression_t& exp ) const		{ return apply_visitor(*this, exp); }
	AST::Expression_t operator ()( AST::BooleanConstantExpression& exp ) const	{ return exp; }
	AST::Expression_t operator ()( AST::IntegerConstantExpression& exp ) const	{ return exp; }
	AST::Expression_t operator ()( AST::DoubleConstantExpression& exp ) const	{ return exp; }

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

class SimplifyVisitor {
private:
	template< typename T >
	typename boost::enable_if< boost::is_base_of<AST::UnaryExpression,T>, AST::Expression_t>::type
	simplify_unary( T& exp, double (*f)(double) ) const {
		exp.right = apply_visitor(*this, exp.right);
	
		if( AST::DoubleConstantExpression* constant = boost::get<AST::DoubleConstantExpression>(&exp.right) )
			return AST::DoubleConstantExpression( f( constant->value ) );

		return exp;
	}

	template< typename T >
	typename boost::enable_if< boost::is_base_of<AST::BinaryExpression,T>, AST::Expression_t>::type
	simplify_binary( T& exp, double (*f)(double, double) ) const {
		exp.left = apply_visitor(*this, exp.left);
		exp.right = apply_visitor(*this, exp.right);

		AST::DoubleConstantExpression *left, *right;
		if( (left = boost::get<AST::DoubleConstantExpression>(&exp.left)) && 
			(right = boost::get<AST::DoubleConstantExpression>(&exp.right)) )
				return AST::DoubleConstantExpression( f( left->value, right->value ) );

		return exp;
	}

public:
	typedef AST::Expression_t result_type;
	AST::Expression_t operator ()( AST::IdentifierExpression& exp ) const		{ return exp; }

	AST::Expression_t operator ()( AST::ConstantExpression_t& exp ) const		{ return apply_visitor(*this, exp); }
	AST::Expression_t operator ()( AST::BooleanConstantExpression& exp ) const	{ return exp; }
	AST::Expression_t operator ()( AST::IntegerConstantExpression& exp ) const	{ return exp; }
	AST::Expression_t operator ()( AST::DoubleConstantExpression& exp ) const	{ return exp; }

	AST::Expression_t operator ()( AST::CallExpression& b ) const;
	AST::Expression_t operator ()( AST::NegateExpression& exp ) const;
	AST::Expression_t operator ()( AST::ReciprocalExpression& exp ) const;

	AST::Expression_t operator ()( AST::MinusExpression& exp ) const;		
	AST::Expression_t operator ()( AST::DivExpression& exp ) const;
	AST::Expression_t operator ()( AST::PowExpression& exp ) const;

	AST::Expression_t operator ()( AST::PlusExpression& exp ) const				{ return exp; }
	AST::Expression_t operator ()( AST::MulExpression& exp ) const				{ return exp; }
	AST::Expression_t operator ()( AST::EqualsExpression& exp ) const			{ return exp; }
};

#endif
