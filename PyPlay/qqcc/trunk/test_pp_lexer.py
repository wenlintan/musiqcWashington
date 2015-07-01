
import unittest
from lexer import *

class PPLexerTestCase(unittest.TestCase):
    def check_result( self, data, result, compare_pos = False ):
        ri = RawIterator.from_text( data )
        pp = PPLexer( ri )

        for i in result:
            pi = pp.next()            
            self.assertEqual( i.__class__, pi.__class__ )
            self.assertEqual( i, pi )
                
        self.assertRaises( StopIteration, pp.next )

class BasicTokensTestCase(PPLexerTestCase):
    def test_basic_tokens( self ):
        res = [CharLiteral((1,0), (1,3), None, "h", None)]
        self.check_result( "'h'", res, True )

        res = [PPNumber((1,0), (1,3), "4e3")]
        self.check_result( "4e3", res, True )

    def test_pp_number( self ):
        res = [PPNumber((1,0), (1,5), "4ae+3")]
        self.check_result( "4ae+3", res, True )


class OperatorTestCase(PPLexerTestCase):
    def test_pp_number_and_ops( self ):
        res = [PPOpOrPunc((1,0), (1,2), "++"),
               PPNumber((1,2), (1,7), "4qE-3"),
               PPOpOrPunc((1,7), (1,8), "+"),
               PPNumber((1,8),(1,9), "8"),
               PPOpOrPunc((1,9), (1,10), "+")]
        self.check_result( "++4qE-3+8+", res, True )

    def test_aborted_ops( self ):
        res = [PPOpOrPunc((1,0), (1,2), "#"),
               PPOpOrPunc((1,2), (1,3), ":")]
        self.check_result( ":%:", res, True )
if __name__ == "__main__":
    unittest.main()
