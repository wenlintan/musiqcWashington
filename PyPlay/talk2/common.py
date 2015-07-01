
class linked:
    def __init__( self ):
        self.links = []
        
    def add_link( self, link ):
        self.links.append( link )
        
    def get_link_count( self ):
        return len( self.links )
    lc = property( get_link_count )
        
class link( linked ):
    FORWARD = 1
    BACKWARD = 2
    BIDIRECT = 4
    
    NOMOD = modifier( '' )
    
    def __init__( self ):
        linked.__init__( self, "_UNNAMED_LINK_@1_" )
        
        self.words = ()
        self.score = 0
        self.dir = BIDIRECT
        self.mod = NOMOD
        
    def bind( word1, word2, mod = NOMOD ):
        self.words = ( word1, word2 )
        self.score = 1
        self.mod = mod
        return self
    
    def use( self ):
        self.score += 1
    
    def other( self, one ):
        if words[0] is one:
            return words[1]
        return words[0]
    
    
class propertied:
    def __init__( self, name ):
        self.name = name
        self.props = []
        
    def add_prop( self, prop ):
        self.props.append( prop )
        
    def meets( self, constraints ):
        meet = self.props
        for prop,val in constraints.items():
            meet = [ p for p in meet if p.meets( prop, val ) ]
        return len(meet)
        
    def __eq__( self, other ):
        return self.name == other.name

class property( propertied, linked ):
    def __init__( self, name, val ):
        propertied.__init__( self, name )
        linked.__init__( self )
        self.val = val
        
    def meets( self, name, val ):
        return val == self.val and name == self.name
    
class change:
    type_map = { link: "links", property: "props" }
    REM = 0; ADD = 1
    
    def __init__( self, statementid, word, change, op ):
        self.sid = statementid
        self.word = word
        self.change = change
        self.op = op
        
    def apply( self, override = False ):
        if op == REM and not override:
            return deapply( self, True )
        getattr( self.word, type_map[ change.__class__ ] ).append( change )
        return True
        
    def deapply( self, override = False ):
        if op == REM and not override:
            return apply( self, True )
        try:
            getattr( self.word, type_map[ change.__class__ ] ).remove( change )
        except ValueError:
            return False
        return True
    