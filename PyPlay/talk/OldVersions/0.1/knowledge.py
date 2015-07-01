
class word(object):
    
    def __init__( self, name, typ = "u" ):
        self.name = name
        self.type = typ

    def manual( self ):
        print "No specialization for type %s" % self.type

    def __repr__( self ):
        return "Name: '%s' as Type: %s" % (self.name, self.type)

    def get_refs( self ):
        return []
        
class relation(word):

    time_map = { "p":"present", "a":"past" }
    pers_map = { "fs": "first-person singular", "fp": "first-person plural",
                 "ss": "second-person singular",
                 "ts": "third-person singular", "tp": "third-person plural" }
    extr_map = { "pp":"present participle", "ap":"past participle",
                 "g":"gerund", "i":"infinitive" }
    
    def __init__( self, name ):
        super(relation, self).__init__( name, "v" )

        self.args = {}
        self.conj = {}

    def manual( self ):
        print "Specialization for relation('%s'):" % self.name

        for k,v in relation.time_map.items():
            for k2,v2 in relation.pers_map.items():
                self.conj[k+k2] = raw_input( "Input %s conj-> " % (v+" "+v2) )
        for k,v in relation.extr_map.items():
            self.conj[k] = raw_input( "Input %s conj-> " % v )

    def __repr__( self ):
        return "Name '%s' as Type: %s with Conj: %s" % (
                    self.name, self.type, ", ".join( self.conj.values() ) )

    def get_refs( self ):
        return self.conj.values()
        

class item(word):

    def __init__( self, name, rels = None ):
        super(item, self).__init__( name, "n" )

        self.rels = rels
        if self.rels is None:
            self.rels = {}

    def add_rel( self, end ):

        try:
            self.rels[ end.name ].occurence += 1
        except KeyError:
            self.rels[ end.name ] = relation( self, end )

    def common_rels( self, num ):

        prep = [ (x.occurence, x) for x in self.rels.values() ]
        prep.sort()
        prep.reverse()
        prep = [ x[1].end.name for x in prep ]

        num = min( num, len(prep) )
        return prep[:num]

        
class knowledge:

    type_map = { "n":"noun", "v":"verb", "p":"preposition", "r":"pronoun",
                 "a":"article", "j":"adjective", "d":"adverb",
                 "q":"question", "c":"conjunction", "u":"UNKNOWN" }

    type_alloc = { "n":item, "v":relation }

    class ref:
        def __init__( self, name ):
            self.name = name

    def __init__( self ):
        self.info = {}

        import baseknowledge as bk
        for k in bk.base.keys():
            for val in bk.base[k]:
                self.assign( val, k )

    def dump( self, pickle, f ):
        pickle.dump( self.info, f )

    def load( self, pickle, f ):
        self.info = pickle.load( f )
        

    def get_info( self, name ):
        try:
            info = self.info[ name ]
            if isinstance( info, knowledge.ref ):
                print "ref", info.name
                return self.info[ info.name ]
            return info
            
        except KeyError:
            self.info[ name ] = word( name )
            return self.info[ name ]

    def assign( self, name, typ ):
        info = self.get_info( name )
        if info.type == typ:
            return info

        if typ in knowledge.type_alloc:
            self.info[ name ] = knowledge.type_alloc[ typ ]( name )
            return self.info[ name ]

        info.type = typ
        return info

    def manual( self, name ):
        typ = raw_input( "Please enter type(%s)-> " %
                         "".join( knowledge.type_map.keys() ) )

        info = self.assign( name, typ )
        info.manual()
        self.update( info )

    def update( self, info ):
        for ref in info.get_refs():
            if ref != info.name:
                self.info[ref] = knowledge.ref( info.name )

    def add_rel( self, name1, name2 ):
        item1 = self.get_item( name1 )
        item2 = self.get_item( name2 )

        item1.add_rel( item2 )

ref = knowledge.ref
