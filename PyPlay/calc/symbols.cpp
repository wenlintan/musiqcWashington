
#include "symbols.h"

using namespace AST;
using namespace Scope;

Expression_t ScopeVisitor::operator ()( IdentifierExpression& exp ) const {
	return exp;
}

Expression_t ScopeVisitor::operator ()( CallExpression& exp ) const {
	return exp;
}

