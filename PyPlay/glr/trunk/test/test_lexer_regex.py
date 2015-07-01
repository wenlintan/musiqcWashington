
import unittest
from lexer import CFGLexer

class TestLexerRegex(unittest.TestCase):
	def test_kleene( self ):
		l = CFGLexer( {"ab*": "match"} )
		self.assertEqual( l.match( "a" ), "match" )
		self.assertEqual( l.match( "ab" ), "match" )
		self.assertEqual( l.match( "abbbb" ), "match" )
		self.assertEqual( l.match( "aab" ), None )
		self.assertEqual( l.match( "b" ), None )

	def test_options( self ):
		l = CFGLexer( {"(a|b)*(c|d)": "match"} )
		print l.base_state
		print l.base_state.edges['c']
		print l.base_state.edges['d']
		print l.base_state.edges['a']
		print l.base_state.edges['b']
		self.assertEqual( l.match( "c" ), "match" )
		self.assertEqual( l.match( "d" ), "match" )
		self.assertEqual( l.match( "ac" ), "match" )
		self.assertEqual( l.match( "aabad" ), "match" )
		self.assertEqual( l.match( "aadc" ), None )
		self.assertEqual( l.match( "aba" ), None )
		self.assertEqual( l.match( "dd" ), None )

	def test_groups( self ):
		l = CFGLexer( {"a|ac*(de)*": "match"} )
		print l.base_state
		self.assertEqual( l.match( "a" ), "match" )
		self.assertEqual( l.match( "acde" ), "match" )
		self.assertEqual( l.match( "ac" ), "match" )
		self.assertEqual( l.match( "ade" ), "match" )
		self.assertEqual( l.match( "accdede" ), "match" )
		self.assertEqual( l.match( "aa" ), None )
		self.assertEqual( l.match( "accd" ), None )
		self.assertEqual( l.match( "acded" ), None )
		self.assertEqual( l.match( "cc" ), None )
		self.assertEqual( l.match( "acdec" ), None )

	def test_nested_groups( self ):
		l = CFGLexer( {"a(b(cd)*e)f": "match"} )
		self.assertEqual( l.match( "abef" ), "match" )
		self.assertEqual( l.match( "abcdcdef" ), "match" )
		self.assertEqual( l.match( "af" ), None )
		self.assertEqual( l.match( "abf" ), None )
		self.assertEqual( l.match( "aef" ), None )

	def test_multiple_options( self ):
		l = CFGLexer( {"a|b|c(d|e|f)*": "match"} )
		print l.base_state
		print l.base_state.edges['a']
		print l.base_state.edges['b']
		print l.base_state.edges['c']
		print l.base_state.edges['c'].edges['e']
		self.assertEqual( l.match( "a" ), "match" )
		self.assertEqual( l.match( "b" ), "match" )
		self.assertEqual( l.match( "c" ), "match" )
		self.assertEqual( l.match( "ce" ), "match" )
		self.assertEqual( l.match( "cfed" ), "match" )
		self.assertEqual( l.match( "cffdee" ), "match" )
		self.assertEqual( l.match( "adef" ), None )
		self.assertEqual( l.match( "bdef" ), None )
		self.assertEqual( l.match( "ac" ), None )
		self.assertEqual( l.match( "acef" ), None )
		self.assertEqual( l.match( "def" ), None )

	def test_floating_point( self ):
		v = lambda d, s, e: float(d)
		s = r"([0-9][0-9]*(\.[0-9]*)?|\.[0-9][0-9]*)([eE][+-]?[0-9][0-9]*)?"
		l = CFGLexer( {s: v} )
		self.assertEqual( l.match( "12" ), float("12") )
		self.assertEqual( l.match( "120" ), float("120") )
		self.assertEqual( l.match( "6.43" ), float("6.43") )
		self.assertEqual( l.match( "9.003" ), float("9.003") )
		self.assertEqual( l.match( "1.04e-4" ), float("1.04e-4") )
		self.assertEqual( l.match( "54.2E+2" ), float("54.2E+2") )
		self.assertEqual( l.match( "0" ), float("0") )
		self.assertEqual( l.match( "a123" ), None )
		self.assertEqual( l.match( ".e" ), None )
		self.assertEqual( l.match( "." ), None )


