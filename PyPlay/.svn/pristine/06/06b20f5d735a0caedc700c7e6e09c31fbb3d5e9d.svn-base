
import sys, socket, select, signal

from vector import *
import action

class client:
    def __init__( self, host, port ):
        self.host = host
        self.port = port
        
        self.name = raw_input( "Enter username: " )
        self.name = '@'.join((self.name, socket.gethostname().split('.')[0]))

        print "Username is : %s" % self.name
        print "Connecting to %s:%s" % (self.host, self.port)
    
        try:
            self.sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            self.sock.connect( (host, port) )

        except socket.error, e:
            raise AttributeError( "Server not found." )

        print "Connection established."
        ident = action.action_name( action.NAME, vector3() )
        ident.name = self.name
        self.send = ident.pack()
        self.recv = ""

    def send_data( self, data ):
        self.send += data

    def __del__( self ):
        print "Shutting down client..."
        self.sock.close()

    def update( self ):
        try:
            inready, out, exc = select.select( [self.sock], [], [], 0 )
        except select.error, e:
            print "ERROR: Problem in select: ", e
        except socket.error, e:
            print "ERROR: Problem in socket: ", e

        for i in inready:
            try:
                data = self.sock.recv( 4096 )
                if not len( data ):
                    self.sock.close()
                    raise socket.error( "Problems in connection." )
                
                self.recv += data
            except socket.error, e:
                print "ERROR: Problem in socket: ", e
                sys.exit( -1 )

        if len(self.send):
            #send the data, if not all sent, save the rest for next time
            sent = self.sock.send( self.send )
            self.send = self.send[sent:]

class server:
    def __init__( self, port ):
        self.port = port
        print "Hosting on port:%d" % self.port

        self.clients = []
        self.client_data = {}
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind( ('', port) )
        self.sock.listen( 2 )

        self.clients = []
        self.inputs = [ self.sock ]
        self.client_data = {}

        signal.signal(signal.SIGINT, self.sighandler)
        self.recv = ""

        #hold all the actions processed so far, to catch up new clients
        self.sync = ""

    def send_data( self, data, exception = None ):
        for c in self.clients:
            if c is not exception:
                self.client_data[ c ] += data
        self.sync += data

    def add_client( self, conn ):
        
        self.clients.append( conn )
        self.inputs.append( conn )
        self.client_data[ conn ] = ""
        
    def remove_client( self, conn ):
        
        self.clients.remove( conn )
        self.inputs.remove( conn )
        del self.client_data[ conn ]

    def __del__( self ):
        self.sighandler( 0, 0 )
        
    def sighandler(self, signum, frame):
        
        print 'Shutting down server...'
        for client in self.clients:
            client.close()
            
        self.sock.close()

    def update( self ):
        
        try:
            inready, outready, exc = select.select( self.inputs, self.clients, [], 0 )
        except select.error, e:
            print "ERROR: Problem in select: ", e
        except socket.error, e:
            print "ERROR: Problem in socket: ", e

        for i in inready:
            
            if i == self.sock:
                conn, address = self.sock.accept()
                self.add_client( conn )

                #sync = action.action_sync( action.SYNC, vector3() )
                self.client_data[ conn ] = self.sync
                
            else:
                try:
                    data = i.recv( 4096 )
                    if len( data ):
                        self.recv += data
                        self.send_data( data, exception = i )

                    else:
                        i.close()
                        self.remove_client( i )
                        
                except socket.error, e:
                    print "ERROR: ", e
                    self.remove_client( i )

        for c in self.clients:
            
            data = self.client_data[ c ]
            if len(data ):
                sent = c.send( data )
                self.client_data[c] = self.client_data[c][sent:] 


        
        
            
            
                
        
        
    
            
