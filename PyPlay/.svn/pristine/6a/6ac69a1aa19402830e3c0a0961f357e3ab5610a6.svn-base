
class ExprParser:
    def parse_expr( self, f ):


    def _primary_expr( self, f ):
        tok = f.next()
        if isinstance( tok, Keyword ) and tok.data = "this":
            return ThisExpr( tok.pos )

        if isinstance( tok, Literal ):
            return LiteralExpr( tok.pos, tok.flags, tok.value )
        
        
