
from properties import *
from objects import *
from collections import defaultdict

class Recognizer(object):
    def __init__( self ):
        self.occurences = defaultdict( set )

    def add( self, thing, *refs ):
        if isinstance( thing, Propertied ):
            for p in thing.list_props():
                self.add( p.base, thing, *refs )

        if isinstance( thing, Property ):
            self.add( p.base, *refs )

        if isinstance( thing, BaseProperty ):
            for r in refs:
                self.occurences[ thing.name ].add( r )
                for v in thing.vals:
                    self.occurences[ v ].add( r )

    def get( self, *props )
            
            
