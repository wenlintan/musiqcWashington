
import socket, select, sys, random
sys.path.append('/home/crazedfool/lib/python')

from client import TLockClient

class Twiddle:
	nchannels = 3
	def __init__( self, param_file, tlock ):
		self.tlock = tlock
		self.tlock.set_data_callback( self._data_recv )
		self.tlock.set_param_callback( self._param_recv )
		self.test_number = int(random.random() * 10000)

		f = file( param_file )
		self.base_params = [
				[7., 3.8e-6, 22419],
				[7.947, 2.342e-6, 20480],
				[10.7877, 6.589e-6, 12697]
			]

		self.params = [[float(v) for v in f.readline().strip().split()] for i in range(self.nchannels)]
		self.dparams = [[float(v) for v in f.readline().strip().split()] for i in range(self.nchannels)]
		self.best_errs = [float(f.readline().strip()) for i in range(self.nchannels)]

		print( "Starting twiddle:" )
		self._print_params()		

		self.current_param = 0
		self.normal_lpoint, self.test_lpoint = 2047, 2067
		self.set_params = [[0 for i in range(6)] for j in range(self.nchannels)]
		self._set_params()		

		self._set_state()


	def _set_state( self, handler = None ):
		if handler is None:
			handler = self._stabilize

		self.npoints = 0
		self.test_data = [[], [], []]
		self.handler = handler

	def _set_params( self, test_lpoint = False ):
		for i, d in enumerate( self.params ):
			pgain, igain, dgain = d
			pshift, ishift = 0, 0
			
			while pgain < 4.:
				pgain, pshift = pgain * 2., pshift + 1
			while pgain > 64. and pshift > 0:
				pgain, pshift = pgain / 2., pshift - 1

			while igain < 2.:
				igain, ishift = igain * 2., ishift + 1

			lp = self.test_lpoint if test_lpoint else self.normal_lpoint
			data = [int(pshift), int(pgain), int(ishift), int(igain), int(dgain), lp]

			self.set_params[ i ] = data
			self.tlock.set_parameters( i, *data )

	def _print_params( self ):
		for i in range( self.nchannels ):
			print( "Channel: {} (err {})".format(i, self.best_errs[i]) )
			print( "Prop: {} +- {}".format( self.params[i][0], self.dparams[i][0] ) )
			print( "Int: {} +- {}".format( self.params[i][1], self.dparams[i][1] ) )
			print( "Der: {} +- {}".format( self.params[i][2], self.dparams[i][2] ) )
			print()

	def _print_test_data( self, test_data ):
		fname = "test_{}.txt".format( self.test_number )
		self.test_number += 1

		f = file( fname, 'w' )
		for p in self.params:
			f.write( "{} {} {}\n".format( *p ) )

		for d in zip( *test_data ):
			f.write( "{} {} {}\n".format( *d ) )

	def _data_recv( self, data ):
		self.handler( data )
			
	def _param_recv( self, params ):
		for mp, tp in zip( params, self.set_params ):
			if list(mp) != list(tp):
				print( "Current parameters:" )
				print( params )
				print()
				print( "Correct parameters:" )
				print( self.set_params )
				print()
				print( "ERROR: incorrect params set, trying to correct" )
				self._set_params()
				break

	def _stabilize( self, data ):
		# append errors to test data
		for i in range(3):
			self.test_data[i].append( data[i][0] )

		if len( self.test_data[0] ) > 3000:
			errs = [ sum( e*e for e in d[-3000:] ) / 3000. for d in self.test_data ]
			if not len( self.test_data[0] ) % 500:
				print( "Waiting to stabilize: ", errs )
			if all( e < 50. for e in errs ):
				self._set_state( self._tick )

	def _tick( self, data ):
		for i in range( 3 ):
			self.params[i][ self.current_param ] += self.dparams[i][ self.current_param ]
		self._set_params( True )
		self._set_state( self._settle )

	def _settle( self, data ):
		self.npoints += 1
		if self.npoints > 500:
			self._set_state( self._test )

	def _test( self, data ):
		for i in range(3):
			self.test_data[i].append( data[i][0] )

		if len( self.test_data[0] ) > 3000:
			errs = [ sum( e*e for e in data ) / float(len(data)) for data in self.test_data ]
			self._print_test_data( self.test_data )

			for i, (e, be) in enumerate( zip( errs, self.best_errs ) ):
				if e < be:
					self.dparams[i][ self.current_param ] *= 1.1
					self.best_errs[ i ] = e
				else:
					self.params[i][ self.current_param ] -= self.dparams[i][ self.current_param ]
					self.dparams[i][ self.current_param ] *= -0.9

					if self.params[i][ self.current_param ] + self.dparams[i][ self.current_param ] < 0.:
						self.dparams[i][ self.current_param ] = -self.params[i][ self.current_param ]
			
			temp_params = self.params
			self.params = self.base_params
			self._set_params()
			self.params = temp_params

			self._print_params()
			self.current_param = (self.current_param +1) % 3
			self._set_state( self._stabilize )
		

HOST = 'localhost' #'172.28.189.202'
PORT = 7777
tlock = TLockClient.TCP(HOST, PORT)

twiddle = Twiddle( 'twiddle_params.txt', tlock )

while True:
	try:
		r, w, e = select.select([tlock], [], [], 1)
		for ri in r:
			ri.handle_request()
	except socket.error, msg:
		sys.stderr.write("[ERROR] %s\n" % msg[1])
		sys.exit(3)
	except KeyboardInterrupt:
		break





