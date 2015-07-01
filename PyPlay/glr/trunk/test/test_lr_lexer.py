
import unittest

from lexer import CFGLexer
from glr import CFGParser, CFGTerminal, CFGNonterminal

class Number:
	def __init__( self, s, start = (0,0), end = (0,0) ):
		self.value = int(s)
	def add( self, rhs ):
		return Number( self.value + rhs.value )
	def mul( self, rhs ):
		return Number( self.value * rhs.value )

class TestGLRLexer(unittest.TestCase):
	def setUp( self ):
		plus, times, num = CFGTerminal.create("+", "*", "num")
		E, T, F = CFGNonterminal.create("E", "T", "F")

		E.production( lambda i: i, T )
		T.production( lambda i, j, k: i.add(k), T, plus, F )
		T.production( lambda i: i, F )
		F.production( lambda i, j, k: i.mul(k), F, times, num )
		F.production( lambda i: i, num )

		tokens = {
			'\\+': plus, '\\*': times,
			"[0-9][0-9]*": num.data_wrapper(Number)
			}

		self.lexer = CFGLexer( tokens )
		self.parser = CFGParser( E, (plus, times, num), (E, T, F) )

	def _n( self, s ):
		return self.parser.parse( self.lexer.tokenize( s ) ).value

	def test_add( self ):
		self.assertEqual( self._n("5+4"), 9 )
		self.assertEqual( self._n("1+3+0"), 4 )

	def test_mul( self ):
		self.assertEqual( self._n("3*2"), 6 )
		self.assertEqual( self._n("1*5*13"), 65 )
		self.assertEqual( self._n("4*0"), 0 )

	def test_oop( self ):
		self.assertEqual( self._n("4+2*8"), 20 )
		self.assertEqual( self._n("5+0*12+4*3*2"), 29 )



