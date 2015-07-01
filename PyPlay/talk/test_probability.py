
import unittest
from probability import *

class TestContinuumDistribution( unittest.TestCase ):

    def setUp( self ):
        self.cont = Continuum( "happy", "fair", "good", "normal", "sad" )
        self.cont.connect( "happy", "fair", "good", "normal", "sad" )

    def test_collapse( self ):
        self.cont.collapse( "happy" )
        self.assertEqual( "happy", self.cont.measure() )

if __name__ == '__main__':
    unittest.main()
