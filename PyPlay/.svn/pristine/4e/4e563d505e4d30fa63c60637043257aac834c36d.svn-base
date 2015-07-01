import libxml2dom, urllib2

class netload:

    def __init__( self, address ):
        self.address = address

    def __call__( self ):

        print "Establishing connection to '%s' and downloading." % self.address
        try:
            #look I'm firefox
            headers = {
                "Connection": "close",
                "Accept" : "text/xml,application/xml,application/xhtml+xml,\
                            text/html;q=0.9,text/plain;q=0.8",
                "Accept-Language": "en-us,en;q=0.5",
                "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7"
                }

            req = urllib2.Request( self.address, None, headers )
            opener = urllib2.build_opener()
            opener.addheaders = [('User-Agent',
                                  "Mozilla/5.0 (Windows; U; Windows NT 5.1;en-US;\
                                   rv:1.8.1.1) Gecko/20061204 Firefox/2.0.0.1")]

            f = opener.open( req )
            raw_data = f.read()
            f.close()
            
            print "Download complete."

        except urllib2.URLError, e:
            print "Connection failed => %s" % e.reason
            return None, None
        except urllib2.HTTPError, e:
            print "HTTP failed with code => %s" % e.code
            return None, None

        doc = libxml2dom.parseString( raw_data, html=1 )
        print "Data parsed into DOM."

        links = doc.getElementsByTagName( "a" )
        link_dests = [ self.get_attr( l, "href" ) for l in links ]
        link_texts = [ self.get_text_in_node( l ) for l in links ]
        
        links = dict( [ (link_texts[i], link_dests[i])
                        for i in range( len(link_texts) ) ] )

        for k,v in links.items():
            if not len(k.strip()) or not len(v.strip()) or v.strip()[0] == "#":
                del links[k]

        print "Link data extracted."

        paras = doc.getElementsByTagName( "p" )
        use_text = [ self.get_text_in_node( p ).strip() for p in paras ]

        print "Parsing complete."
        return " ".join( use_text ), links

    def get_attr( self, node, name ):
        "Get an attribute from node and try to convert to ascii."
        
        try:                        return str( node.getAttribute( name ) )
        except UnicodeEncodeError:  pass

    def get_text_in_node( self, node ):
        "Get all the text elements below this node converted to ascii."

        try:
            text = ""
            for child in node.childNodes:
                if child.nodeType == child.TEXT_NODE:

                    try:                        text += str(child.nodeValue)
                    except UnicodeEncodeError:  pass
                    
                else:  text += self.get_text_in_node( child )

            return text
        
        except KeyError, e:

            #some possible parse errors in here
            print "Parse error on accessing %s, continuing" % e
            return ""

        
