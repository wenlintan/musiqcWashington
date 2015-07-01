
#include "syntax_types.h"
using namespace AST;

void PrintVisitor::handle_unary( const AST::UnaryExpression& exp, const char* op ) const {
	out << op;
	apply_visitor( *this, exp.right );
}

void PrintVisitor::handle_binary( const AST::BinaryExpression& exp, const char* op ) const {
	out << "(";
	apply_visitor( *this, exp.left );
	out << " " << op << " ";
	apply_visitor( *this, exp.right );
	out << ")";
}

void PrintVisitor::handle_n_ary( const AST::N_aryExpression& exp, const char* op ) const {
	if( !exp.items.size() )		return;
	out << "(";
	for( size_t i = 0; i < exp.items.size()-1; ++i ) {
		apply_visitor( *this, exp.items[i] );	out << " " << op << " ";
	}
	apply_visitor( *this, exp.items.back() );
	out << ")";
}

void PrintVisitor::operator ()( const AST::ExpressionStatement& s ) const {
	apply_visitor( *this, s.exp );

	if( s.qualifiers.size() )		out << " ";
	for( size_t i = 0; i < s.qualifiers.size(); ++i ) {
		apply_visitor( *this, s.qualifiers[i] );
		if( i != s.qualifiers.size() -1 )		out << ", ";
	}

	out << ";" << std::endl;
}

void PrintVisitor::operator ()( const AST::GivenQualifier& q ) const {
	out << "given ";
	apply_visitor( *this, q.exp );
}

void PrintVisitor::operator ()( const AST::WithQualifier& q ) const {
	out << "with ";
	for( size_t i = 0; i < q.variables.size(); ++i ) {
		apply_visitor( *this, q.variables[i] );
		if( i != q.variables.size() -1 )		out << ", ";
	}
}

void PrintVisitor::operator ()( const AST::InQualifier& q ) const {
	out << "in ";
	apply_visitor( *this, q.exp );
}

void PrintVisitor::operator ()( const AST::ConstantVariableDeclaration& v ) const {
	out << "constant " << v.ident;
}

void PrintVisitor::operator ()( const AST::VariableVariableDeclaration& v ) const {
	out << "variable " << v.ident;
}

void PrintVisitor::operator ()( const AST::FunctionVariableDeclaration& v ) const {
	out << "function " << v.ident << "(";
	for( size_t i = 0; i < v.arguments.size(); ++i ) {	
		out << v.arguments[i].ident;	
		if( i != v.arguments.size() -1 )		out << ", ";
	}	
	out << ")";
}


void PrintVisitor::operator ()( const AST::CallExpression& exp ) const { 
	out << exp.func << "(";
	for( size_t i = 0; i < exp.arguments.size(); ++i ) {	
		apply_visitor( *this, exp.arguments[i] );	
		if( i != exp.arguments.size() -1 )		out << ", ";
	}
	out << ")";
}

template<>
bool EqualTo::operator ()<double>( const double& lhs, const double& rhs ) {
	return abs( lhs - rhs ) / std::min( abs(lhs), abs(rhs) ) < 0.0001;
}







