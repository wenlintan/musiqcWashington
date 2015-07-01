
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

class RequestHandler( BaseHTTPRequestHandler ):
	def do_GET( self ):
		self.send_response( 200 )
		f = file('index.html', 'r')
		d = '\n'.join( f.readlines() )
		self.wfile.write( d )

server = HTTPServer(('', 5321), RequestHandler)
server.serve_forever()