
import urlparse, urllib, urllib2
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

class JSONAPIRequestHandler( BaseHTTPRequestHandler ):
	def _send_headers( self, content_type, length ):
		self.send_response( 200 )
		self.send_header("Content-Type", content_type)
		self.send_header("Content-Length", length )
		self.send_header("Access-Control-Allow-Origin", "*")
		self.end_headers()
		
	def _recent( self, last = 0 ):
		recent = min(len(self.server.data) - last, 10)
		if recent <= 0:
			result = '{"l":%d}' % len(self.server.data)
			self._send_headers( "application/json", len(result) )
			self.wfile.write( result )
			return

		result = ['[' + ','.join( l ) + ']' for l in zip( *self.server.data[-recent:] )]
		result = dict( zip(["err", "out", "int"], result) )

		result["l"] = str(len(self.server.data))
		if( self.server.parameters_set >= last ):
			result["params"] = "true"

		result = '{' + ','.join( '"%s":%s' % (name, val) for name, val in result.items() ) + '}'
		self._send_headers( "application/json", len(result) )
		self.wfile.write( result )
		
	def do_GET( self ):
		parse = urlparse.urlparse(self.path)
		self.path = parse.path
		params = dict([(k,int(v[0])) for k, v in urlparse.parse_qs( parse.query ).items()]) if parse.query else None
			
		if self.path in ('/recent', '/recent/'):
			self._recent( params["l"] if params else 0 )
			
		if self.path == '/index.html':
			f = file('index.html', 'r')
			d = ''.join( f.readlines() )
			f.close()
			
			self._send_headers( "text/html", len(d) )
			self.wfile.write( d )

	def do_POST( self ):
		params = None
		if int(self.headers["Content-Length"]) != 0:
			params = self.rfile.read( int(self.headers["Content-Length"]) )
			params = urlparse.parse_qs( params )
			params = dict([(k,int(v[0])) for k, v in params.items()])
		
		if self.path in ('/recent', '/recent/'):
			self._recent( params["l"] if params else 0 )
		
		elif self.path in ('/history', '/history/'):
			self._send_headers( "text/plain; charset=x-user-defined", len("Not implemented.") )
			self.wfile.write( "Not implemented." )

		elif self.path in ('/parameters', '/parameters/'):
			if params:
				param_names = ['ch', 'ps', 'pg', 'is', 'ig', 'dg', 'lp'] 
				self.server.set_parameters( *map( lambda s: params[s], param_names ) )
			
			self._send_headers( "application/json", len(self.server.parameters) )
			self.wfile.write( self.server.parameters )

		elif self.path in ('/feedback_parameters', '/feedback_parameters/'):
			if params:
				param_names = ['ch', 'pg', 'ig', 'lim']
				self.server.set_feedback_parameters( *map( lambda s: params[s], param_names ) )
			self.send_response( 200 )
			self.end_headers()

		elif self.path in ('/feedback', '/feedback/'):
			if params:
				param_names = ['ch', 'err']
				self.server.feedback( *map( lambda s: params[s], param_names ) )
			self.send_response( 200 )
			self.end_headers()

		else:
			self.send_response( 404 )
			self.end_headers()
			
class JSONAPIServer( HTTPServer ):
	def __init__( self, addr, handler, tlock ):
		HTTPServer.__init__( self, addr, handler )
		self.tlock = tlock
		
		self.tlock.set_data_callback( self._data_recv )
		self.tlock.set_param_callback( self._param_recv )
		
		self.data = []
		self.raw_parameters = None
		self.parameters = None
		self.parameters_set = 0

		self.pgain = [0]*3
		self.igain = [0]*3
		self.limit = [0]*3

		self.integral = [0]*3
		self.error = [0]*3
		self.output = [0]*3
		
	def _data_recv( self, data ):
		result = ['[' + ','.join(str(d) for d in l) + ']' for l in zip(*data)]
		self.data.append( result )
		
	def _param_recv( self, params ):
		self.raw_parameters = [list(channel_params) for channel_params in params]
		result = list( zip(["ps", "pg", "is", "ig", "dg", "lp"], zip(*params)) )
		result = '{' + ','.join( '"%s":%s' % (name, str(list(val))) for name, val in result ) + '}'

		self.parameters = result
		self.parameters_set = len( self.data )
		
	def set_parameters( self, channel, *data ):
		self.tlock.set_parameters( channel, *data )

	def set_feedback_parameters( self, channel, *data ):
		self.pgain[ channel ], self.igain[ channel ], self.limit[ channel ] = data
	
	def feedback( self, channel, error ):
		self.error[ channel ] = error
		self.integral[ channel ] += error
		newout = self.pgain[ channel ] * error + self.igain[ channel ] * self.integral[ channel ]
		if newout > self.limit[ channel ]:	newout = self.limit[ channel ]
		if newout < -self.limit[ channel ]:	newout = -self.limit[ channel ]

		diff = newout - self.output[ channel ]
		self.output[ channel ] = newout
		print( "Offset now {0}.".format( self.output[ channel ] ) )

		if diff != 0:
			self.raw_parameters[channel][-1] += diff
			self.set_parameters( channel, *self.raw_parameters[channel] )

