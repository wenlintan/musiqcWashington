
import unittest, tokenize
from itertools import izip_longest, chain

from file_parser import CFGFileParser

class TestCFGFileLexer(unittest.TestCase):
	def setUp( self ):
		self.parser = CFGFileParser()
		
	def _test_file( self, filename ):
		f = file( filename )
		l = list( self.parser.python_tokenize( chain.from_iterable( f ) ) )
		f.close()

		f = file( filename )
		p = list( t[:-1] for t in tokenize.generate_tokens(f.readline) )
		f.close()

		for t1, t2 in izip_longest( l, p ):
			self.assertEqual( t1, t2 )
	
	def test_simple_python_file( self ):
		self._test_file( 'test/test_cfg_file_lexer.py' )

	def test_complicated_python_file( self ):
		self._test_file( 'file_parser.py' )
		self._test_file( 'lexer.py' )
		self._test_file( 'glr.py' )
		pass


