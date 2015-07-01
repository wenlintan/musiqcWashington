
import unittest
from glr import CFGParser, CFGTerminal, CFGNonterminal

class TestGLRList(unittest.TestCase):
	def setUp( self ):
		S, L = CFGNonterminal.create("S", "L")
		self.op, self.cp, self.c, self.x = (
			CFGTerminal.create("(", ")", ",", "x") )

		S.production( lambda i, j, k: j, self.op, L, self.cp )
		S.production( lambda i: i, self.x )
		L.production( lambda i: [i], S )
		def append( l, i ):
			l.append( i )
			return l
		L.production( lambda i, j, k: append(i, k), L, self.c, S )
		self.parser = CFGParser( S, 
			(self.op, self.cp, self.c, self.x), (S, L) )

	def test_single_list( self ):
		l = self.parser.parse_items( self.op, self.x, self.cp )
		self.assertEqual( l, [self.x] )

		l = self.parser.parse_items(
			self.op, self.x, self.c, self.x, self.cp )
		self.assertEqual( l, [self.x, self.x] )

	def test_nested( self ):
		l = self.parser.parse_items(
			self.op, self.x, self.c, self.op, self.x, self.cp, self.cp )
		self.assertEqual( l, [self.x, [self.x]] )

class TestGLRValuesExpr(unittest.TestCase):
	def setUp( self ):
		self.plus, self.mul, self.num = CFGTerminal.create( "+", "*", "num" )
		E, T, F = CFGNonterminal.create( "E", "T", "F" )

		E.production( lambda i: i, T )
		T.production( lambda i, j, k: i + k, T, self.plus, F )
		T.production( lambda i: i, F )
		F.production( lambda i, j, k: i * k, F, self.mul, self.num )
		F.production( lambda i: i, self.num )
		self.parser = CFGParser( E, (self.plus, self.mul, self.num),
				(E, T, F) )

	def _n( self, v ):
		return self.num.with_data(v)

	def test_add( self ):
		v = self.parser.parse_items( self._n(5), self.plus, self._n(2) )
		self.assertEqual( v, 7 )

		v = self.parser.parse_items( self._n(1), self.plus, self._n(4),
			self.plus, self._n(10) )
		self.assertEqual( v, 15 )

	def test_mul( self ):
		v = self.parser.parse_items( self._n(5), self.mul, self._n(2) )
		self.assertEqual( v, 10 )

		v = self.parser.parse_items( self._n(1), self.mul, self._n(4),
			self.mul, self._n(10) )
		self.assertEqual( v, 40 )

	def test_oop( self ):
		v = self.parser.parse_items( self._n(7), self.mul, self._n(3),
			self.plus, self._n(2) )
		self.assertEqual( v, 23 )

		v = self.parser.parse_items( self._n(1), self.plus, self._n(4),
			self.mul, self._n(10) )
		self.assertEqual( v, 41 )

	def test_complex( self ):
		v = self.parser.parse_items( self._n(7), self.mul, self._n(3),
			self.plus, self._n(3), self.mul, self._n(2) )
		self.assertEqual( v, 27 )

		v = self.parser.parse_items( self._n(1), self.plus, self._n(4),
			self.mul, self._n(5), self.plus, self._n(1), self.mul,
			self._n(9), self.mul, self._n(2) )
		self.assertEqual( v, 39 )



#if __name__ == "__main__":
#	unittest.main()

