
def comb_dict( d1, d2 ):
    for k in d2.keys():

        if k in d1:
            d1[k] += d2[k]
        else:
            d1[k] = d2[k]
            
class positionals:
    def __init__( self ):
        self.positionals = { }

    def add_positional( self, name ):
        self.positionals[name] = 1

    def match( self, data ):

        split = data.split( " " )
        first = "st"

class parser:

    unguided_match = 2.0
    
    class p_o_s:
        class link:
            def __init__( self, typ, mod ):
                self.mod = mod
                self.typ = typ

                self.occurences = 0
                self.score = 0.0

            def __eq__( self, other ):
                return self.mod == other.mod and self.typ == other.typ

            def add_occurence( self ):
                self.occurences += 1
            def rescore( self, total ):
                self.score = 3.0 * (float(self.occurences) / total) * min(1.0, float(total)/5.0)
            
        def __init__( self, name ):
            self.name = name
            self.next = []
            self.prev = []

        def _next_total( self ):
            return sum( [n.occurences for n in self.next] )
        def _prev_total( self ):
            return sum( [n.occurences for n in self.prev] )

        next_total = property( _next_total )
        prev_total = property( _prev_total )

        def add_link( self, otherpos, mod, arr ):
            if parser.p_o_s.link( otherpos, mod ) in arr:
                arr[ arr.index( parser.p_o_s.link( otherpos, mod ) ) ].add_occurence()
            else:
                l = parser.p_o_s.link( otherpos, mod )
                l.add_occurence()
                arr.append(l)
            self.rescore()

        add_next = lambda s,o,m: s.add_link( o, m, s.next )
        add_prev = lambda s,o,m: s.add_link( o, m, s.prev )

        def get_link( self, mod, arr ):
            
            if arr:
                new_arr = [ (i.score, i) for i in arr if i.mod == mod ]
                new_arr.sort()
                new_arr.reverse()

                return dict( [(i.typ,s) for s,i in new_arr] )
            
            return {}

        get_next = lambda s,m: s.get_link( m, s.next )
        get_prev = lambda s,m: s.get_link( m, s.prev )

        def rescore( self ):
            for n in self.next:
                n.rescore( self.next_total )
            for p in self.prev:
                p.rescore( self.prev_total )

    class p_o_s_sent:
        class sub:
            def __init__( self, sub ):
                self.sub = sub
                self.links = []
                self.occurences = 0
                
            def add_link( self, sub ):
                self.links.append( [0.0, sub, 0] )

            def use_link( self, sub ):
                subs = [ i[1] for i in self.links ]

                try:
                    index = subs.index( sub )
                except ValueError:
                    print "Invalid sub link access."

                link = self.links[ index ]
                link[2] += 1
                self.occurences += 1

                self.rescore()

            def rescore( self ):
                self.links = [ [ 3.0 * float(i[2])/self.occurences,
                                 i[1],
                                 i[2] ]
                               for i in self.links ]

                self.links.sort()
                
        min_sub_len = 3
        cut_len = 50
        max_len = 100
        
        def __init__( self ):
            self.full = []
            self.subs = []
            self.scores = []
            self.mean = 1

        def gen_sent( self, word_arr ):
            sent = [ word.info.type for word in word_arr ]
            mods = [ word_arr[i].conn.modnext for i in range( len(word_arr) ) ]
            mods = [ (mods[i], i) for i in range(len(mods)) if mods[i] is not None ]

            in_pos_mod = 0
            for mod in mods:
                sent.insert( mod[1]+in_pos_mod+1, mod[0] )
                in_pos_mod += 1

            sent = "".join( sent )
            return sent

        def gen_subs( self, sent ):

            subs = []
            for i in range( len(sent)- parser.p_o_s_sent.min_sub_len +1 ):
                for j in range(i + parser.p_o_s_sent.min_sub_len, len(sent)+1 ):
                    subs.append( sent[i:j] )

            return subs

        def add_sent( self, word_arr ):

            sent = self.gen_sent( word_arr )
            self.full.append( sent )
            self.add_subs( sent )

        def add_subs( self, sent ):

            subs = self.gen_subs( sent )
            for sub in subs:
                
                if sub in self.subs:
                    self.scores[ self.subs.index( sub ) ] += 1
                    continue

                self.subs.append( sub )
                self.scores.append( 1 )

            self.proc_subs()
            print "Subs:", self.subs

        def proc_subs( self ):
            pack = [ (self.scores[i], self.subs[i])
                     for i in range( len(self.subs) ) ]

            pack.sort()
            pack.reverse()

            self.scores = [ packed[0] for packed in pack ]
            self.subs = [ packed[1] for packed in pack ]

            if len( self.subs ) > parser.p_o_s_sent.max_len:
                self.scores = self.scores[:parser.p_o_s_sent.cut_len]
                self.subs = self.subs[:parser.p_o_s_sent.cut_len]

            sum_score = sum( self.scores )
            self.mean = float( sum_score ) / len( self.scores )
                

        def match( self, word_arr ):

            sent = self.gen_sent( word_arr )
            subs = self.gen_subs( sent )

            print sent, subs

            subs = [ [s, sent.index(s)] for s in subs ]
            guesses = [{} for i in range( len( sent ) )]

            #make sure each u has at least one guess
            for i in range( len(sent) ):
                if sent[i] == "u":
                    guesses[i]["u"] = 0.0000001

            for sub in subs:
                
                for ksi in range( len(self.subs) ):
                    known_sub = self.subs[ksi]
                
                    if len(sub[0]) != len(known_sub):
                        continue

                    unknowns = []; match_fail = False
                    for i in range( len(sub[0]) ):
                        if (known_sub[i] in parser.punctuation and
                            sub[0][i] != known_sub[i]):
                            
                            match_fail = True
                            break
                            
                        if sub[0][i] == "u":
                            
                            sub[0] = sub[0][:i] + known_sub[i] + sub[0][i+1:]
                            unknowns.append(i)

                    if not len(unknowns) or match_fail:
                        #nothing to guess about, or punc failed to match
                        continue

                    if known_sub == sub[0]:

                        #add a score factor based on number of unknowns
                        #guessed at, and length of known_sub
                        known = len(known_sub) - len(unknowns)
                        score = float( known**3 ) / len(known_sub)**2
                        score = score * ( self.scores[ksi] / self.mean )
                        print sub, "matches to", known_sub, "score:", score
                        for uk in unknowns:

                            fulli = sub[1] + uk
                            try:
                                guesses[ fulli ][sub[0][uk]] += score
                            except KeyError:
                                guesses[ fulli ][sub[0][uk]] = score

                    for uk in unknowns:
                        sub[0] = sub[0][:uk] + "u" + sub[0][uk+1:]

            guesses = [ [(i[1],i[0]) for i in g.items()] for g in guesses if g ]
            for g in guesses:
                g.sort()
                g.reverse()
            guesses = [ (g[0][1], g[0][0]) for g in guesses ]
            print "Guesses:",guesses
            return guesses

    class gen_sent:
        class elem:
            def __init__( self, pos_sent, nexts ):
                pass
            
        def __init__( self ):
            pass
            
                         
            
    type_map = { "n":"noun", "v":"verb", "p":"preposition", "r":"pronoun",
                 "a":"article", "j":"adjective", "d":"adverb",
                 "q":"qualifier", "c":"conjunction", "u":"UNKNOWN" }
    types = dict( [(k, p_o_s(k)) for k in type_map.keys()] )
    punctuation = ",.':;\"?-()/\\"
    

    def __init__( self, know ):
        self.know = know
        self.sent = parser.p_o_s_sent()

    def dump( self, pickle, f ):
        pickle.dump( self.know, f )
        pickle.dump( self.sent, f )

    def load( self, pickle, f ):
        self.know = pickle.load( f )
        self.sent = pickle.load( f )

    def all_relations( self, data ):

        words = data.split( " " )
        words = [ w.lower() for w in words ]

        l = len(words)
        if l <= 1:
            return

        for i in range(l+1):

            for j in range(i+1, l+1):
                word = " ".join( words[i:j] )
                for k in range(i):
                    before = " ".join( words[k:i] )
                    self.know.add_rel( word, before )

                for k in range(j+1, l+1):
                    after = " ".join( words[j:k] )
                    self.know.add_rel( word, after )
                    

    def __call__( self, data ):
        
        class modstr(str):
            "A fully modifiable subclass of str."

        class nopuncstr(modstr):
            def __new__( cls, word ):

                modprev = None
                if word[0] in parser.punctuation:
                    modprev = word[0]
                    word = word[1:]

                modnext = None
                if word[-1] in parser.punctuation:
                    modnext = word[-1]
                    word = word[:-1]

                capital = False
                if word.istitle():
                    capital = True
                word = word.lower()

                self = modstr.__new__(cls, word)
                self.modprev = modprev
                self.modnext = modnext
                self.capital = capital
                return self
                

        class connect:
            def __init__( self, word, next = None, prev = None ):
                self.next = next
                self.prev = prev

                self.modprev = word.modprev
                self.modnext = word.modnext

                if prev is not None:
                    if prev.conn.modnext is not None:
                        self.modprev = prev.conn.modnext
                    if self.modprev is not None:
                        prev.conn.modnext = self.modprev

        words = [ nopuncstr(x) for x in data.split() ]

        if len(words) < 2:
            print "Sentence too short"
            return

        words[0].conn = connect( words[0], words[1] )
        for i in range( 1, len(words)-1 ):
            words[i].conn = connect( words[i], words[i+1], words[i-1] )
        words[-1].conn = connect( words[-1], None, words[-2] )

        for word in words:
            word.info = self.know.get_info( word )
            
        guesses = self.sent.match( words )
        guess_index = 0

        for word in words:

            if word.info.type == "u":
                guess = guesses[ guess_index ]

                if guess[1] > parser.unguided_match:
                    self.know.assign( word, guess[0] )
                    print "Unguided match '%s' to type '%s'" % (word, guess[0])

                else:
                    print "Collecting information on %s" % word
                    self.know.manual( word )
                    print "Word complete.\n"

                # regrab info because it may have been reallocated
                word.info = self.know.get_info( word )
                guess_index += 1

        self.sent.add_sent( words )

p_o_s = parser.p_o_s              
p_o_s_sent = parser.p_o_s_sent

        
