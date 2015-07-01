import netload, pickle

class commands:
    "Handles all direct commands, returns 0 when input doesn't match command"

    def __init__(self, know, pars):
        "Initialize with info dictionary containing all knowledge"
        self.know = know
        self.pars = pars
    
    def __call__(self, data):
        "Searches for a function in the class with this name and runs it."

        #take everything up to first space to be command name
        split = data.split(" ")
        name = split[0]

        #all command names start with "."
        if name[0] != ".":
            return 0

        #skip the "." for purposes of lookup in dictionary
        name = name[1:]

        data = []
        if len( split ) > 1:
            data = split[1:]
        
        try:
            return commands.__dict__[name](self, data)
        except KeyError, e:
            #started with "." so call it a command even though it isn't (typo)
            print "Command not found: %s.\n" % e
            return 1

    def run( self, data ):
        eval( ' '.join( data ) )
        
    def dump( self, data ):
        print "Dumping information to %s." % data[0]

        f = file( data[0], "w" )
        self.know.dump( pickle, f )
        self.pars.dump( pickle, f )
        f.close()

        print "Information saved.\n"
        return 1

    def load( self, data ):
        print "Loading knowledge from %s." % data[0]

        try:
            f = file( data[0], "r" )
            self.know.load( pickle, f )
            self.pars.load( pickle, f )
            f.close()
        except IOError, e:
            print "Load failed => %s" % e

        print "Information loaded.\n"
        return 1

    def manual( self, data ):
        name = data[0]
        self.know.manual( name )
        print "Information updated.\n"
        return 1

    def relations( self, data ):

        data = " ".join( data )
        item = self.know.get_item( data )
        rels = item.common_rels( 5 )

        print "Common relations for %s: %s\n" % ( data, rels )
        return 1

    def info( self, data ):

        info = self.know.get_info( data[0] )
        print info
        print ""
        return 1

    def fileload( self, data ):

        print "Opening file %s and loading data." % data[0]

        try:
            f = file( data[0], "r" )
            data = f.read()
            f.close()
        except IOError, e:
            print "Data load failed => %s" % e
            return 1

        print "Data retrieved, extracting information."
        data = data.split( "." )
        data = [ d.strip() for d in data ]

        for d in data: self.pars( d )
        print "Data extracted.\n"
        return 1
        

    def netload( self, data ):

        addr = data[0]
        if len(data) < 7 or data[:7] != "http://":
            addr = "http://" + addr
            
        links = [ addr ]
        selected = 0

        while selected < len( links ):
            data, links = netload.netload( links[selected] )()

            if data is None:
                break

            print "Data retrieved, extracting information."
            data = data.split( "." )
            data = [ d.strip() for d in data ]

            for d in data:  self.pars( d )
            print "Data extracted, loading links."

            l = links.items()
            links = links.values()

            print "Please select address to link to:"
            print "\n".join( ["%s) %s => %s" % ( i, l[i][0], l[i][1] )
                              for i in range( len(l) )] )

            print "%s) quit" % len(l)

            selected = None
            while selected is None:
                try:                selected = int( raw_input("--->") )
                except ValueError:  print "Invalid entry, try again."


        print "Session complete.\n" 
        return 1

    def quit( self, data ):
        return -1
