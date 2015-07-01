
from common import *
    
class modifier( linked ):
    def __init__( self, name ):
        linked.__init__( self, name )
        self.resistivity = 100
        
    def use( self ):
        if self.resistivity:
            self.resistivity -= 1    
        
class word( linked ):
    pass
        
class phrase( linked ):
    def __init__( self, words = None ):
        self.words = []
        if words is not None:
            self.words = words
            
        linked.__init__( self, self.words )
        
    def add_word( self, word ):
        self.words.append( word )
            
      
class parser:
    def __init__( self, know ):
        self.knowledge = know
        
        self.words = {}
        self.punctuation = "`~!@#$%^&*()-_=+[{]}\|;:'\",<.>/?"
        self.punc = dict( [ ( x, modifier(x) ) for x in self.punctuation ] )
        
        self.changes = []
        
    def _get_word( self, wrd ):
        if hasattr( wrd, "real_word" ):
            return wrd.real_word
        return wrd
            
    def __call__( self, str ):
        words = self.preprocess( str )
        
        
    def preprocess( self, str ):
        split = str.split()        
        if not len(split):
            return
        
        split = [ word(text) for text in split ]
        for wrd in split:
            if self.words.has_key( wrd.name ):
                wrd.real_word = self.words[ wrd.name ]
                
        last = split[0]
        for wrd in split[1:]:
            if wrd in self.punctuation:
                last.append(wrd)
            
            if last[-1] in self.punctuation:
                l = link().bind( last, wrd, self.punc[ last[-1] ] )
            elif wrd[0] in self.punctuation:
                l = link().bind( last, wrd, self.punc[ wrd[0] ] )
            else:
                l = link().bind( last, wrd )
                
            wrd.add_link( l )
            last.add_link( l )
            last = wrd
            
        return split
            