
import sys, socket, struct

class TLockClient:
	header_length = 5
	resend_time = 10

	def __init__( self, conn, logger = None ):
		self.conn = conn
		self.raw_data = ""
		self.logger = logger
		
		self.parameters = [None, None, None]
		self.new_parameters = [None, None, None]

		self.send_requested = 0
		self.params_requested = 0
		
		self.data_callback = lambda d: d
		self.param_callback = lambda p: p
		self._request_params()

	def __del__( self ):
		self.save.close()
		
	@staticmethod
	def TCP( host, port, logger = None ):
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((host, port))
		except socket.error, e:
			sys.stderr.write(e[1])
			sys.exit()
		return TLockClient( sock, logger )
		
	def fileno( self ):
		return self.conn.fileno()

	def set_parameters( self, channel, *params ):
		assert channel in range(3)
		self.new_parameters[channel] = params
		self._request_send_params()
		
	def set_data_callback( self, fn ):
		self.data_callback = fn
		
	def set_param_callback( self, fn ):
		self.param_callback = fn
		
	def handle_request( self ):
		self.raw_data += self.conn.recv( 1024 )
		
		success = True
		while success:
			self.raw_data, success = self._decode_packet( self.raw_data )
		
	def _handle_data( self, s ):
		nchannels = len(s) / struct.calcsize("<lLl")
		data = struct.unpack( '<' + "lLl"*nchannels, s )
		data = [(data[i], data[i+1], data[i+2]) for i in range(0, len(data), 3)]

		self.data_callback( data )
		if self.logger is not None:
			self.logger.handle_data( data )
		#print( data )		

	def _handle_parameters( self, s ):
		self.params_requested = 0

		self.parameters = []
		l = struct.calcsize("<LLLLLL")
		for i in range(len(s) / l):
			self.parameters.append( struct.unpack( "<LLLLLL", s[i*l: i*l + l] ) )
			if self.new_parameters[i] == self.parameters[i]:
				self.new_parameters[i] = None

		if any([ i is not None for i in self.new_parameters ]):
			self._request_send_params()
			
		print "Parameters:", self.parameters
		self.param_callback( self.parameters )

	def _send_parameters( self, s ):
		self.send_requested = 0

		data = ""
		for old, new in zip( self.parameters, self.new_parameters ):
			print old, new
			if new is None:		data += struct.pack( "<LLLLLL", *old )
			else:				data += struct.pack( "<LLLLLL", *new )

		print("Writing parameters.")
		self.conn.send( data )

	def _request_params( self, s = None ):
		if not self.params_requested:
			self.conn.send('b')
			print "Requesting params."
		self.params_requested = 1
	
	def _request_send_params( self, s = None ):
		if not self.send_requested:
			self.conn.send('c')
			print "Requesting send."
		self.send_requested = 1
	
	def _handle_packet( self, s ):
		if self.send_requested:
			self.send_requested = (self.send_requested+1) % self.resend_time
			if not self.send_requested:
				self._request_send_params()
		
		if self.params_requested:
			self.params_requested = (self.params_requested+1) % self.resend_time
			if not self.params_requested:
				self._request_params()
		
		if s[0] == 'a':
			self._handle_data( s[self.header_length:] )
		elif s[0] == 'b':
			self._handle_parameters( s[self.header_length:] )
		elif s[0] == 'c':
			self._send_parameters( s[self.header_length:] )
		elif s[0] == 'd':
			print "Conf. packet."
			self._request_params( s[self.header_length:] )

	def _find_packet_boundary( self, s ):
		for i, v in enumerate( s[:-self.header_length] ):
			if v in "abcd":
				end = i + self.header_length + struct.unpack( "<L", s[i+1: i+self.header_length] )[0]
				if end < len(s) and s[end] in "abcd":
					return s[i:], True
		if len(s) > 1000:
			print "Failing to find boundary."
			return s[-100:], False
		return s, False
		
	def _decode_packet( self, s ):
		if not s:
			return s, False
		
		if s[0] not in "abcd":
			return self._find_packet_boundary( s )
			
		if len(s) < self.header_length:
			return s, False
			
		size = struct.unpack("<L", self.raw_data[1:5])[0]
		if size > len(s) - self.header_length:
			return s, False
			
		self._handle_packet( self.raw_data[:self.header_length+size] )
		return s[ self.header_length+size: ], True	

