import copy

caps = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
lowers = caps.lower()
alphas = caps + lowers
numbers = "0123456789"
alphanums = alphas + numbers

class parse_error(Exception):
    pass

class parser:

    def __init__( self ):
        self.patterns = []

    def add_pattern( self, pattern ):
        self.patterns.append( pattern )

    def parse( self, data, takeall = True ):
        for p in self.patterns:

            try:                    loc, lev = p.parse( data )
            except parse_error, e:
                print e
                print "Match failure", self.pretty( p.contents )
                print
                continue

            if takeall and loc != len( data.strip() ):
                print "Match failed with '%s' left" % (len(data)-loc)
                print
                return True
            else:
                print "Complete match."
                print self.pretty( p.contents )
                print
                return False


    def pretty( self, d ):
        return "\n".join( ["%s => %s" % i for i in d.items()] )


class element(object):
    no_more_levels = -1
    
    def __init__( self, name = "" ):
        self.name = name
        
        self.parsed = None
        self.contents = {}

    debug = True
    head = lambda self: "Element %s(%s): " % (self.name, self.__class__.__name__)
    def printd( self, mess ):
        if element.debug:
            print element.head( self ) + mess
        
    def __add__( self, elem ):
        if isinstance( elem, basestring ):
            self.printd( "Literal conversion on '%s'" % elem )
            elem = literal( elem )
        if isinstance( elem, composite ):
            return composite( self, *elem.elements )

        comp = composite( self, elem )
        return comp

    def __or__( self, elem ):
        if type(elem) == str:
            elem = literal( elem )

        gro = group( self, elem )
        return gro

    def __call__( self, name ):
        self.name = name
        return self

    def __repr__( self ):
        return "element"

class composite(element):

    def __init__( self, *args ):

        super(composite, self).__init__()
        self.elements = [ copy.deepcopy(x) for x in args ]

        for i in range( len( self.elements ) ):
            if type( self.elements[i] ) == str:
                self.elements[i] = literal( self.elements[i] )

    def parse( self, data, loc = 0, level = 0 ):
        self.printd("start with '%s'" % data[loc:])

        if loc >= len(data):
            self.printd( "past end of data" )
            raise parse_error
        
        restarts = [(loc,0,0)]; parsed=0
        while restarts:
            try:
                start = restarts.pop()
                loc = start[0]
                elem = self.elements[ start[1] ]
                startlev = start[2]

                self.printd( "start %d, %s, %d" % (loc,elem,startlev) )
                
                oldloc = loc
                
                loc, reparselev = elem.parse( data, loc, startlev )
                if reparselev != element.no_more_levels:
                    self.printd( "REPARSE in %s at %s" % ( elem, reparselev ) )
                    restarts.append( (oldloc, start[1], reparselev) )

                restarts.append( (loc, start[1]+1, 0) )
                parsed = start[1]+1

            except parse_error:
                pass
            except IndexError:
                break

        self.contents = {}
        if parsed != len(self.elements):
            self.contents = {}
            raise parse_error()
        
        for e in self.elements:
            oconts = dict( [(self.name+x[0],x[1]) for x in e.contents.items()] )
            self.contents.update( oconts )

        return loc, element.no_more_levels


    def __add__( self, elem ):

        if isinstance( elem, composite ):
            elems = [ copy.deepcopy(x) for x in elem.elements ]
            self.elements.extend( elems )  
            return self
        
        elem = copy.deepcopy( elem )
        self.elements.append( elem )
        return self

    def __repr__( self ):
        return "{%s}" % " + ".join( [ str(e) for e in self.elements ] )

class group(element):
    def __init__( self, *args ):
        
        super(group, self).__init__()
        self.branches = [ copy.deepcopy(x) for x in args ]

        for i in range( len( self.branches ) ):
            if type( self.branches[i] ) == str:
                self.branches[i] = literal( self.branches[i] )
                
    def parse( self, data, loc = 0, level = 0 ):
        self.printd("start with '%s'" % data[loc:])

        if loc >= len(data):
            self.printd( "past end of data" )
            raise parse_error
        
        if level == 0: level = (0,0)
        start_branch = level[0]
        start_inbran = level[1]
        
        for b in self.branches[ start_branch: ]:
            try:
                                    
                loc, reparse = b.parse( data, loc, start_inbran )

                self.parsed = b
                self.contents = dict( [(self.name+x[0],x[1]) for x in b.contents.items()] )

                if reparse == element.no_more_levels:
                    reparse = ( start_branch+1, 0 )
                else:
                    reparse = ( start_branch, reparse )
                
                return loc, reparse

            except parse_error:
                pass

        self.contents = {}
        self.parsed = None
        raise parse_error

    def __or__( self, elem ):

        if isinstance( elem, group ):
            elems = [ copy.deepcopy(x) for x in elem.branches ]
            self.branches.extend( elems )
            return self

        elem = copy.deepcopy(elem)
        self.branches.append( elem )
        return self

    def __repr__( self ):
        return "{%s}" % ( " | ".join( [ str(b) for  b in self.branches ] ) )

class forward(element):
    "Beware: forward instances copies will be modified by assign."
    def __init__( self, name="" ):
        super(forward, self).__init__(name)
        self.copies = []
        
    def assign( self, elem ):
        self.elem = elem

        for cpy in self.copies:
            cpy.assign( elem )
        
    def parse( self, data, loc = 0, level = 0 ):
        self.printd("start with '%s'" % data[loc:])

        if loc >= len(data):
            self.printd( "past end of data" )
            raise parse_error

        self.printd( str( self.elem ) )

        try:
            loc, lev = self.elem.parse( data, loc, level )
            self.contents = self.elem.contents
            return loc, lev
        
        except AttributeError:
            self.contents = {}
            raise parse_error( "Forward element not set" )
        except parse_error:
            self.contents = {}
            raise

    def __str__( self ):
        return "...%s..." % self.name
    
    def __repr__( self ):
        try:        return str( self.elem )
        except AttributeError:
                    raise parse_error( "Forward element not set" )

    def __deepcopy__( self, memo = None, _nil=[] ):
       
        cpy = forward()
        cpy.name = self.name
        self.copies.append( cpy )
        return cpy


                
class literal(element):
    wildcard = ""
    wildcard_compose = alphas
    
    def __init__( self, match, name="" ):

        super(literal, self).__init__(name)
        self.word = match

    def parse( self, data, loc = 0, level = 0 ):
        self.printd("start with '%s'" % data[loc:])

        if loc >= len(data):
            self.printd( "past end of data" )
            raise parse_error
        
        mine = data[ loc: ].strip()
        loc_off = data.index( mine, loc )
        
        mine = mine[ :len( self.word ) ]

        if mine != self.word:
            self.contents = {}

            print "literal wildcard!!!", literal.wildcard
            if len(literal.wildcard) and mine == literal.wildcard:
                print "gots it"
                self.printd( "literal using wildcard" )
                e = word_fixlen( literal.wildcard_compose,
                                 len( literal.wildcard ) )
                
                loc, lev = e.parse( data, loc )
                self.contents = e.contents
                return loc, lev

            self.printd( "match to '%s' failed on '%s'" % (self.word, data[loc:]) )
            raise parse_error

        ##self.contents = { self.name: mine }
        return loc_off + len(self.word), element.no_more_levels

    def __repr__( self ):
        return ( "'%s'" % self.word )

class word(element):
    def __init__( self, compose, name="" ):

        super(word, self).__init__(name)
        self.composition = compose

    def parse( self, data, loc = 0, level = 0 ):
        self.printd("start")

        if loc >= len(data):
            self.printd( "past end of data" )
            raise parse_error
        
        mine = data[ loc: ].strip()
        loc_off = data.index( mine, loc )

        index = 0
        while index < len(mine) and mine[index] in self.composition:
            index += 1

        if index == 0:
            self.printd( "no characters matched in '%s'" % data[loc:] )
            self.contents = {}
            raise parse_error
        
        self.contents = { self.name: mine[ :index ] }
        return loc_off + index, element.no_more_levels

    def __repr__( self ):
        return ( "word('%s')" % self.composition[:3] )

class word_fixlen(element):
    def __init__( self, compose, length, name="" ):

        super(word_fixlen, self).__init__(name)
        self.composition = compose
        self.l = length

    def parse( self, data, loc = 0, level = 0 ):
        self.printd("start")
        
        if loc >= len(data):
            self.printd( "past end of data" )
            raise parse_error

        mine = data[ loc: ].strip()
        loc_off = data.index( mine, loc )

        index = 0
        while index < len(mine) and index < self.l and mine[index] in self.composition:
            index += 1

        if index != self.l:
            self.printd("Incorrect number matched(%d,%d) in '%s'" % (
                            self.l, index, data[loc:] ) )
            self.contents = {}
            raise parse_error

        self.contents = { self.name: mine[ :index ] }
        return loc_off + index, element.no_more_levels

    def __repr__( self ):
        return ( "?" * self.l + "(%s)" % self.composition[:3] )
            

class optional(element):
    
    opt_unmatchable = -2
    def __init__( self, branch, name="" ):

        super(optional, self).__init__(name)
        self.branch = copy.deepcopy( branch )

    def parse( self, data, loc = 0, level = 0 ):
        self.printd("start")
        
        if level == optional.opt_unmatchable:
            #already tried and failed to parse the optional branch
            self.parsed = None
            self.contents = {}
            return loc, element.no_more_levels
        
        try:
            loc, nextlevel = self.branch.parse( data, loc, level )

            self.parsed = self.branch
            contarr = [(self.name+x[0], x[1]) for x in self.branch.contents.items()]
            self.contents = dict( contarr )

            if nextlevel == -1:
                nextlevel = optional.opt_unmatchable
            return loc, nextlevel
            
        except parse_error:
            return self.parse( data, loc, optional.opt_unmatchable )

    def __repr__( self ):
        return ( "(%s)" % str( self.branch ) )

class multiple(element):
    def __init__( self, branch, greedy = True, name="" ):

        super(multiple, self).__init__(name)
        self.branch = copy.deepcopy( branch )
        self.greedy = greedy

    def parse( self, data, loc = 0, level = 0 ):
        self.printd("start")

        if loc >= len(data):
            self.printd( "past end of data" )
            raise parse_error

        conts = {}; matches = []; locked_conts = None
        restarts = [(0,0)]; parsed=0; maxparsed = 0

        while restarts:
            try:
                start = restarts.pop()
                num = start[0]
                startlev = start[1]
                
                loc, reparselev = self.branch.parse( data, loc, startlev )
                contarr = [(self.name+x[0],x[1]) for x in self.branch.contents.items()]
                contarr.append( ("__loc__", loc) )
                conts[self.name + str(num)] = dict( contarr )

                if reparselev != element.no_more_levels:
                    restarts.append( (num, reparselev) )
                    
                restarts.append( (num+1, 0) )
                parsed = num+1

                if parsed > maxparsed:
                    maxparsed = parsed
                    locked_conts = copy.deepcopy( conts )
                    
            except parse_error:
                pass
            except IndexError:
                break

        if maxparsed == 0:
            self.contents = {}
            raise parse_error

        self.contents = locked_conts
        num_to_take = maxparsed - level
        
        newloc = self.contents[ self.name + str(num_to_take-1) ]["__loc__"]
        self.contents = dict( [i for i in self.contents.items() if i[0] < self.name + str(num_to_take) ] )

        for i in self.contents.items():
            for k in i[1].items():
                if k[0] == "__loc__":
                    del self.contents[ i[0] ][ k[0] ]
                
        if num_to_take == 1:
            return newloc, element.no_more_levels
        return newloc, level+1

    def __repr__( self ):
        return ( "%s+" % str( self.branch ) )

def zero_or_more( x ):
    return optional( multiple( x ) )

def partw(name):
    return word( alphas )
def w(name):
    return word( alphas )(name)
def wl(l,name):
    return word_fixlen( alphas, l )(name)

l = literal
literal.wildchar = "u"
element.debug = True
pars = parser()

start = ( optional( l("d") + l(",") ) +     #begin with adverb
          optional( l("i") + l(",") ) )     #begin with interjection
          
sverb = ( zero_or_more( l("d") ) + zero_or_more( l("v") ) + l("v") +
          zero_or_more( l("d") ) )          

snoun = ( optional( l("a")("art") )("oart") +
          optional( l("j")("adj") + zero_or_more( l(",")("cadj") + l("j")("adj2") ) )("oadjs") +
          l("n")("actnoun") )("snoun")
snouns = snoun + optional( zero_or_more( l(",") + snoun ) + l("c") + snoun )

prep = (l("p")("conprep") + snouns)("prep")
apos = (l(",")("capos1") + snouns + l(",")("capos2"))("apos")
qual = optional( l(",") ) + l("q") + snoun + sverb

sent = ( start + snouns + optional( apos ) + zero_or_more(prep)

noun = forward()("noun")
verb = forward()("verb")

prep = (l("p")("conprep") + noun)("prep")
apos = (l(",")("capos1") + noun + l(",")("capos2"))("apos")
qual = optional( l(",") ) + l("q") + noun + verb

singnoun = ( optional( l("a")("art") )("oart") +
             optional( l("j")("adj") + zero_or_more( l(",")("cadj") + l("j")("adj2") ) )("oadjs") +
             l("n")("actnoun") +
             optional( multiple(prep)("mprep") | apos )("oend") )

renoun = singnoun + optional( optional( l(",") + singnoun ) + l("c") + singnoun )
noun.assign( renoun )

pars.add_pattern( snoun )

try:
    print repr(noun)
    #pars.parse( "n" )
    #pars.parse( "aj,jnpan" )
    pars.parse( "aj,un" )
except RuntimeError, e:
    print e
    print "Runtime error"

