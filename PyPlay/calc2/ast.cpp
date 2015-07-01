
#include "ast.h"
#include <boost/assign.hpp>

using namespace boost::mpl;
using namespace boost::assign;
using boost::apply_visitor;

using namespace AST;

// Ugly hack to avoid problem with ADL in boost swap specialization
// For anything in std, ADL picks up std::swap at same specialization level as boost optimization
namespace std {
	inline void swap( Expr_t& s1, Expr_t& s2) {
		std::swap< Expr_t >( s1, s2 );
	}
}

/////////////////////////////////////////////////////////////////////////////////////////////////////////
// Basic Types
/////////////////////////////////////////////////////////////////////////////////////////////////////////

// Identifier
std::ostream& AST::operator << ( std::ostream& os, const Identifier& id ) {
	os << id.id;
	return os;
}

bool AST::operator < ( const Identifier& lhs, const Identifier& rhs ) {
	return lhs.id < rhs.id;
}

bool AST::operator == ( const Identifier& lhs, const Identifier& rhs ) {
	return lhs.id == rhs.id;
}

// Constant overloads
std::ostream& AST::operator << ( std::ostream& os, const Constant<bool>& c ) {
	os << (c.value ? "true" : "false");
	return os;
}

// Unit Constant
std::ostream& AST::operator << ( std::ostream& os, const UnitConstant& c ) {
	os << c.constant << c.unit;
	return os;
};

bool AST::operator < ( const UnitConstant& lhs, const UnitConstant& rhs ) {
	if( lhs.unit < rhs.unit )	return true;
	if( lhs.unit > rhs.unit )	return false;
	return lhs.constant < rhs.constant;
}

bool AST::operator == ( const UnitConstant& lhs, const UnitConstant& rhs ) {
	return lhs.unit == rhs.unit && lhs.constant == rhs.constant;
}

/////////////////////////////////////////////////////////////////////////////////////////////////////////
// Expression Types
/////////////////////////////////////////////////////////////////////////////////////////////////////////

// IfExpr
std::ostream& AST::operator << ( std::ostream& os, const IfExpr& if_ ) {
	os << "if " << if_.if_ << " then " << if_.then;
	if( if_.else_ )	os << " else " << *if_.else_;
	return os;
}

bool AST::operator < ( const IfExpr& lhs, const IfExpr& rhs ) {
	return lhs.if_ < rhs.if_ ||
		( !(rhs.if_ < lhs.if_) && lhs.then < rhs.then ) ||
		( !(rhs.if_ < lhs.if_) && !(rhs.then < lhs.then) && lhs.else_ < rhs.else_ );
}

bool AST::operator == ( const IfExpr& lhs, const IfExpr& rhs ) {
	return lhs.if_ == rhs.if_ && lhs.then == rhs.then && lhs.else_ == rhs.else_;
}

// LambdaExpr
std::ostream& AST::operator << ( std::ostream& os, const LambdaExpr& lam ) {
	os << "(\\";
	AST::detail::print_list( os, lam.args, ", " );
	os << " -> " << lam.result << ")";
	return os;
}

bool AST::operator < ( const LambdaExpr& lhs, const LambdaExpr& rhs ) {
	bool args_less = std::lexicographical_compare( 
		lhs.args.begin(), lhs.args.end(), rhs.args.begin(), rhs.args.end() );

	return lhs.result < rhs.result || ( !(rhs.result < lhs.result) && args_less );
}

bool AST::operator == ( const LambdaExpr& lhs, const LambdaExpr& rhs ) {
	return lhs.args.size() == rhs.args.size() &&
		std::equal( lhs.args.begin(), lhs.args.end(), rhs.args.begin() ) &&
		lhs.result == rhs.result;
}

// LetExpr
std::ostream& AST::operator << ( std::ostream& os, const LetExpr& let ) {
	os << "let ";
	AST::detail::print_list( os, let.bindings, ", " );
	os << " in" << std::endl;
	os << let.in << std::endl;
	return os;
}

bool AST::operator < ( const LetExpr& lhs, const LetExpr& rhs ) {
	bool bindings_less = std::lexicographical_compare(
		lhs.bindings.begin(), lhs.bindings.end(), rhs.bindings.begin(), rhs.bindings.end() );

	return lhs.in < rhs.in || ( !(rhs.in < lhs.in) && bindings_less );
}

bool AST::operator == ( const LetExpr& lhs, const LetExpr& rhs ) {
	return lhs.bindings.size() == rhs.bindings.size() &&
		std::equal( lhs.bindings.begin(), lhs.bindings.end(), rhs.bindings.begin() ) &&
		lhs.in == rhs.in;
}

// MatchExpr
std::ostream& AST::operator << ( std::ostream& os, const MatchExpr::Match& match ) {
	os << "| " << match.with << " -> " << match.in;
	if( match.when ) os << " when " << *match.when;
	return os;
}

bool AST::operator < ( const MatchExpr::Match& lhs, const MatchExpr::Match& rhs ) {
	return lhs.with < rhs.with || 
		( !(rhs.with < lhs.with) && lhs.in < rhs.in ) ||
		( !(rhs.with < lhs.with) && !(rhs.in < lhs.in) && lhs.when < rhs.when );
}


bool AST::operator == ( const MatchExpr::Match& lhs, const MatchExpr::Match& rhs ) {
	return lhs.with == rhs.with && lhs.in == rhs.in && lhs.when == rhs.when;
}

std::ostream& AST::operator << ( std::ostream& os, const MatchExpr& match ) {
	os << "match " << match.val;
	os << " with" << std::endl;
	AST::detail::print_list( os, match.matches, "\n" );
	os << std::endl;
	return os;
}

bool AST::operator < ( const MatchExpr& lhs, const MatchExpr& rhs ) {
	bool matches_less = std::lexicographical_compare( 
		lhs.matches.begin(), lhs.matches.end(), rhs.matches.begin(), rhs.matches.end() );

	return lhs.val < rhs.val || ( !(rhs.val < lhs.val) && matches_less );
}

bool AST::operator == ( const MatchExpr& lhs, const MatchExpr& rhs ) {
	return lhs.val == rhs.val &&
		lhs.matches.size() == rhs.matches.size() &&
		std::equal( lhs.matches.begin(), lhs.matches.end(), rhs.matches.begin() );
}

// UnaryExpr
std::ostream& AST::operator << ( std::ostream& os, const NegateExpr& neg ) {
	os << '-' << neg.left;
	return os;
}

std::ostream& AST::operator << ( std::ostream& os, const RecipExpr& rec ) {
	os << rec.left << "**-1";
	return os;
}

// BinaryExpr
const char* BinaryNotationMap< Pow >::value = "**";
const char* BinaryNotationMap< Eq >::value = "==";
const char* BinaryNotationMap< Le >::value = "<=";
const char* BinaryNotationMap< Ge >::value = ">=";

