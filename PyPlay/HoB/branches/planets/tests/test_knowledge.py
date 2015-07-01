
import unittest
from knowledge import *

class TestKnowledge( unittest.TestCase ):
	parent = Predicate( "Parent" )
	likes = Predicate( "Likes" )

	def test_binary_unify( self ):
		def unify( s, t, x, y ):
			return self.parent( s, t ).unify( self.parent( x, y ) )

		self.assertEqual( unify( "x", "y", "Tom", "John" ),
			{ 'x': 'Tom', 'y': 'John' } )
		self.assertEqual( unify( "Tom", "x", "Tom", "John" ),
			{ 'x': 'John' } )
		self.assertEqual( unify( "x", "x", "Tom", "Tom" ),
			{ 'x': 'Tom' } )

		#self.assertTrue( unify( "Tom", "y", "y", "FOPC" ) is None )
		#self.assertTrue( unify( "Tom", "Fred", "x", "x" ) is None )


if __name__ == '__main__':
	unittest.main()
