
from common import *
    
class isa( link ):
    pass
class hasa( link ):
    pass
class usesa( link ):
    pass
        
        
class event( propertied, linked ):
    def __init__( self, name ):
        propertied.__init__( self, name )
        linked.__init__( self )
        
    def generalize( self ):        
        links = [ l.other( self ) for l in self.links ]
        
        scored = []
        for l in links:
            sublinks = [ a.other( l ) for a in l.links ] 
            score = sum( [ (isinstance( w, isa )*4) + 1 for w in sublinks ] )
            scored.append( (score, l) )
        scored.sort()
        return scored
    
    def most_general( self, wrd ):
        gen = self._generalize( wrd )        
        return gen[-1][1]
        
class position:
    def __init__( self, prepname = "", relativepos = 0 ):
        self.prepname = prepname
        self.relativepos = 0
        
class metaproperty( propertied, linked ):
    def __init__( self, name, targetpos, val ):
        propertied.__init__( self, name )
        self.target = targetpos
        self.val = val
        
class relation( propertied, linked ):
    def __init__( self, name ):
        propertied.__init__( self, name )
        self.prop_adds = []
        
    def add_effect( self, prep, metaprop ):
        self.prop_adds[ prep ] = metaprop
        
    def process( self ):
        for prop in self.prop:
            pass
    
class knowledge:
    REM = change.REM; ADD = change.ADD
    def __init__( self ):
        self.events = {}
        self.changes = []
        
    def know( self, word, constraints, change, op ):
        events = self.events[ word ]
        events = [ e for e in events if e.meets( constraints ) ]
        
        for e in events:
            c = change( -1, e, change, op )
            self.changes.append( c )
            c.apply()
        
        
    def get_knowledge( self, word ):
        return self.events[ word ]
    