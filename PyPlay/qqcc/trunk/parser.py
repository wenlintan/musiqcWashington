
from itertools import chain
from token import *

class PPASTNode(object):
    pass

class PPDirective(PPASTNode):
    pass

class PPParser:
    def __init__( self, lexer ):
        self.lexer = lexer
        self.token = self.lexer.next()
        self.definitions = {}

    def __iter__( self ):
        return self
        
    def next( self ):
        while isinstance( self.token, Whitespace ):
            self.token = self.lexer.next()

        tok = self.token
        if isinstance(tok, PPOpOrPunc) and tok.pp_directive():
            tok = self._consume_whitespace()

            if isinstance(tok, Identifier) and tok.data in self.pp_directives:
                fn = getattr(self, "parse_" + ident.data)
                return fn( ident )

    def _consume_whitespace( self, i = self.lexer ):
        tok = i.next()
        while isinstance(tok, Whitespace):
            tok = i.next()
        return tok

    pp_directives = [
            "if", "ifdef", "ifndef",
            "include", "define", "undef"
            "line", "error", "pragma"
        ]        

    def parse_if( self, name ):
        data = self._pp_line()
        

    def parse_ifdef( self, *lookahead ):
        return self.parse_if( 
        
        
        
        
        
    
