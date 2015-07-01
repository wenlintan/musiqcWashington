
import unittest
from lexer import *

class RawIteratorTestCase(unittest.TestCase):
    def check_result( self, data, result ):
        ri = RawIterator.from_text( data )
        for i in result:
            self.assertEquals( ri.next(), i )
        self.assertRaises( StopIteration, ri.next )
        
class TrigraphTestCase(RawIteratorTestCase):
    def test_brackets( self ):
        self.check_result( "??<\n", "{\n" )
        self.check_result( "??<??!,??)\n", "{|,]\n" )

    def test_no_trigraphs( self ):
        self.check_result( "??9\n", "??9\n" )
        self.check_result( "??r?e?#2??0\n", "??r?e?#2??0\n" )

class LineExtensionTestCase(RawIteratorTestCase):
    def test_line_extension( self ):
        self.check_result( "afv\\\noiaf", "afvoiaf" )

    def test_newlines_and_extensions( self ):
        self.check_result( "ao942\n\\\n943\\oif\\\ny", "ao942\n943\\oify" )

if __name__ == '__main__':
    unittest.main()
