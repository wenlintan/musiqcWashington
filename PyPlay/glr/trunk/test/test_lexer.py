
import unittest
from lexer import CFGLexer, CFGNFAState

class Token:
	def __init__( self, data, start, end ):
		self.data, self.start, self.end = data, start, end

	def __eq__( self, rhs ):
		print self, rhs
		return (	self.data == rhs[0] and
					self.start == (rhs[1], rhs[2]) and
					self.end == (rhs[3], rhs[4]) 	)

	def __str__( self ):
		return "({0} {1} {2})".format(
			self.data, str(self.start), str(self.end) )

	def __repr__( self ):
		return str( self )

class TestLexerTokenizer(unittest.TestCase):
	def _toks( self, *toks ):
		line, col, res = 1, 0, []
		for t in toks:
			if isinstance( t, tuple ):
				line, col = t
				res.append( None )
			else:
				l = len( t )
				start = line, col
				for ch in t:
					col += 1
					if ch == '\n':
						line, col = line+1, 0
				res.append( (t, start, (line,col)) )
		return res

	def _tuple( self, d, s, e ):
		return (d, s, e)

	def test_basic_regex( self ):
		l = CFGLexer( {"ab*": self._tuple} )
		fn = lambda s: list( l.tokenize(s) )
		self.assertEqual( fn("abb"), self._toks( "abb" ) )
		self.assertEqual( fn("aba"), self._toks( "ab", "a" ) )

		self.assertEqual( fn("abaca"), self._toks( "ab", "a", (1, 4), "a" ) )
		self.assertEqual( fn("caba"), self._toks( (1, 1), "ab", "a" ) )
		self.assertEqual( fn("abac"), self._toks( "ab", "a", (1, 4) ) )

	def test_identifier_regex( self ):
		l = CFGLexer( {	"if": self._tuple,  
						"else": self._tuple,
						"elif": self._tuple,
						"[a-zA-Z_][a-zA-Z0-9_]*": self._tuple } )
		fn = lambda s: list( l.tokenize(s) )
		self.assertEqual( fn("if elif"), self._toks( "if", (1, 3), "elif" ) )
		self.assertEqual( fn("ab 03if"), self._toks( "ab", (1, 5), "if" ) )
		self.assertEqual( fn("elin if 432"), 
			self._toks( "elin", (1, 5), "if", (1, 11) ) )

	def test_bol( self ):
		l = CFGLexer( {"ab\\n": self._tuple, "^c\\n": self._tuple } )
		fn = lambda s: list( l.tokenize(s) )
		self.assertEqual( fn( "ab\n" ), self._toks( "ab\n" ) )
		self.assertEqual( fn( "c\n" ), self._toks( "c\n" ) )
		self.assertEqual( fn( "ab\nc\n" ), self._toks( "ab\n", "c\n" ) )
		self.assertEqual( fn( "bac\n" ), self._toks( (1, 4) ) )

	def test_eol( self ):
		l = CFGLexer( {"\\na": self._tuple, "$\\nc": self._tuple } )
		fn = lambda s: list( l.tokenize(s) )
		self.assertEqual( fn( "\na\nc" ), self._toks( "\na", "\nc" ) )
		self.assertEqual( fn( "\nb\nc" ), self._toks( (2, 1), "\nc" ) )

	def test_empty_bol( self ):
		l = CFGLexer( {"b\\n": self._tuple, "^[ \\t]*": self._tuple } )
		fn = lambda s: list( l.tokenize(s) )
		self.assertEqual( fn("b\n  b\n"), 
			self._toks( "", "b\n", "  ", "b\n", "" ) )
		self.assertEqual( fn(" \tb\n"), self._toks( " \t", "b\n", "" ) )
		self.assertEqual( fn(" \n "), self._toks( " ", (2, 0), " " ) )

	def test_empty_eol( self ):
		l = CFGLexer( {"\\nab": self._tuple, "c*$": self._tuple } )
		fn = lambda s: list( l.tokenize(s) )
		self.assertEqual( fn("c\nab"), self._toks( "c", "\nab", "" ) )
		self.assertEqual( fn("\nabcc\nab"), 
				self._toks( "", "\nab", "cc", "\nab", "" ) )
		self.assertEqual( fn("\nab"), self._toks( "", "\nab", "" ) )
		self.assertEqual( fn("ca\nab"), self._toks( (1, 2), "", "\nab", "" ) )


