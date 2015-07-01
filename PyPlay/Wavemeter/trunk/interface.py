
import threading, time
import urlparse, urllib, urllib2
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

from switch import SwitchController
from dac import DACController
from wm import WavemeterController

class Update:
	LockParameter = 1		# PID Controller parameters updated
	ChannelState = 2		# Channel locking/switch active state changed
	WavemeterData = 3		# Frequency/interference pattern data

	def __init__( self ):
		pass
		
class Channel:
	def __init__( self ):
		self.locking = False
		self.frequency = None

		self.updates = []

class WMInterface( threading.Thread ):
	def __init__( self, channels, update_queue ):
		threading.Thread.__init__( self )
		self.queue = update_queue

		self.switch = SwitchController()
		self.dac = DACController()
		self.wm = WavemeterController()

		self.channel = None
		self.channels = channels

		self.channel( 1 )
		self.running = True

	def run( self ):
		while self.running:
			freq = self.wm.frequency()
			pattern = self.wm.interference_pattern()
			self.queue.put( WavemeterUpdate( freq, pattern ) )

			if self.channel.locking:
				self.channel.lock( freq )

			dt = time.clock() - self.switch_time
			if self.rotating and dt > self.channel.lock_time:
				pass
		print "Done."

	def _switch( self, ch ):
		if self.channel is not None:
			self.queue.put( ChannelState( self.channel.index, ChannelState.INACTIVE ) )

		self.switch.switch( ch )
		self.channel = self.channels[ ch ]

		self.switch_time = time.clock()
		self.queue.put( ChannelState( self.channel.index, ChannelState.ACTIVE ) )

		self.wm.exposure_time( self.channel.exp_time / 1000. )
		contrast = self.wm.contrast()
		freq = self.wm.frequency()
		
		while abs(self.wm.contrast() - contrast) > 10 or abs(self.wm.frequency() - freq) > 5:
			contrast = self.wm.contrast()
			freq = self.wm.frequency()

	def rotating( self, state ):
		self.rotating = state

	def channel( self, ch ):
		self.rotating( False )
		self._switch( ch )

	def stop( self ):
		self.running = False
		self.join()

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

		else:
			self.send_response( 404 )
			
class JSONAPIServer( HTTPServer ):
	def __init__( self, addr, handler ):
		HTTPServer.__init__( self, addr, handler )
		self.interface = WMInterface( channels )
		self.interface.start()	
		
		self.data = []

	def recent( self, last, filter_fn ):
		return filter( self.data[last:], filter_fn )
		
	def _data_recv( self, data ):
		result = ['[' + ','.join(str(d) for d in l) + ']' for l in zip(*data)]
		self.data.append( result )
		
	def _param_recv( self, params ):
		result = list( zip(["ps", "pg", "is", "ig", "dg", "lp"], zip(*params)) )
		result = '{' + ','.join( '"%s":%s' % (name, str(list(val))) for name, val in result ) + '}'

		self.parameters = result
		self.parameters_set = len( self.data )
		
	def set_parameters( self, channel, *data ):
		self.tlock.set_parameters( channel, *data )
server = JSONAPIServer(('', 8321), JSONAPIRequestHandler, tlock)

while True:
	try:
		r, w, e = select.select([server], [], [], 1)
		for ri in r:
			ri.handle_request()
	except socket.error, msg:
		sys.stderr.write("[ERROR] %s\n" % msg[1])
		sys.exit(3)
	except KeyboardInterrupt:
		break

