
from ctypes import *
from time import sleep
from itertools import izip_longest

import urlparse, urllib, urllib2
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

daqmx = windll.nicaiu
TaskHandle = c_void_p
DAQmxCreateTask = daqmx.DAQmxCreateTask
DAQmxStartTask = daqmx.DAQmxStartTask
DAQmxStopTask = daqmx.DAQmxStopTask
DAQmxClearTask = daqmx.DAQmxClearTask
DAQmxResetDevice = daqmx.DAQmxResetDevice

DAQmxCreateDOChan = daqmx.DAQmxCreateDOChan
DAQmxWriteDigitalU8 = daqmx.DAQmxWriteDigitalU8
DAQmxWaitUntilTaskDone = daqmx.DAQmxWaitUntilTaskDone

#From NIDAQmx.h
DAQmx_Val_ChanForAllLines = 1
DAQmx_Val_GroupByScanNumber = 1
DAQmx_Val_WaitInfinitely = c_double(-1.0)

class DACController:
	# Specify DAC voltage range
	min_voltage = -10
	max_voltage = 20 + min_voltage
	precision = 1 << 16
	
	# Specify NI output ports to use
	device = "Dev1/port0/line0:4"
	timeout = c_double( 10.0 )

	# Specify which of output ports to use for each function
	update_data_type = c_uint8 * 50
	frame_bit = 1 << 4
	clock_bit = 1 << 3
	data3_bit = 1 << 2
	data2_bit = 1 << 1
	data1_bit = 1 << 0
	init_data = update_data_type( *([0]*50) )

	# Map electrode number to chip and channel number
	nelectrodes = 89
	ring_electrode_map = {
		1:  (1, 4),
		2:  (1, 3),
		3:  (2, 28),
		4:  (2, 30),
		5:  (2, 31),
		6:  (2, 27),
		7:  (2, 8),
		8:  (2, 10),
		9:  (2, 12),
		10: (2, 14),
		11: (2, 17),
		12: (2, 21),
		13: (2, 20),
		14: (2, 3),
		15: (2, 5),
		16: (2, 7),
		17: (2, 2),
		18: (0, 27),
		19: (0, 29),
		20: (0, 31),
		21: (0, 9),
		22: (0, 10),
		23: (0, 12),
		24: (0, 17),
		25: (0, 19),
		26: (0, 21),
		27: (0, 16),
		28: (0, 23),
		29: (0, 1),
		30: (0, 3),
		31: (0, 5),
		32: (0, 6),
		33: (1, 26),
		34: (1, 9),
		35: (1, 31),
		36: (1, 30),
		37: (1, 8),
		38: (1, 12),
		39: (1, 14),
		40: (1, 18),
		41: (1, 20),
		42: (1, 22),
		43: (1, 23),
		44: (1, 1),
		45: (2, 26),
		46: (1, 6),
		47: (1, 5),
		48: (1, 7),
		49: (2, 29),
		50: (2, 9),
		51: (2, 11),
		52: (2, 13),
		53: (2, 15),
		54: (2, 16),
		55: (2, 18),
		56: (2, 1),
		57: (2, 23),
		58: (2, 22),
		59: (2, 0),
		60: (2, 4),
		61: (2, 6),
		62: (0, 26),
		63: (0, 28),
		64: (0, 30),
		65: (0, 8),
		66: (0, 11),
		67: (0, 14),
		68: (0, 13),
		69: (0, 15),
		70: (0, 18),
		71: (0, 20),
		72: (0, 22),
		73: (0, 0),
		74: (0, 2),
		75: (0, 4),
		76: (0, 7),
		77: (1, 27),
		78: (1, 28),
		79: (1, 11),
		80: (1, 13),
		81: (1, 15),
		82: (1, 10),
		83: (1, 16),
		84: (1, 17),
		85: (1, 19),
		86: (1, 21),
		87: (1, 0),
		88: (1, 2),
		89: (2, 19)
	}

	gtri_genIII_electrode_map = {
                1: (None, None),
                2: (None, None),
                3: (2, 17),   
                4: (2, 20),   
                5: (1, 9),
                6: (1, 26),
                7: (1, 28),
                8: (0, 7),
                9: (1, 11),
                10: (0, 4),
                11: (1, 30),
                12: (0, 5),
                13: (1, 13),
                14: (0, 2),
                15: ( (1, 15), (1, 8) ),
                16: ( (0,0), (0,3) ),
                17: ( (1, 17),  (1,20) ),
                18: ( (0,21), (0,15) ),
                19: (1, 19), 
                20: (0, 19),
                21: (1, 22),
                22: (0, 13),
                23: (1, 21),
                24: (0, 17),
                25: ( (1, 1), (1, 23) ),
                26: ( (0, 25), (0, 14) ),
                27: (1, 0),
                28: (0, 12),
                29: (1, 3),
                30: (0, 11),
                31: ( (2, 26), (1, 6) ), 
                32: ( (1, 22), (0, 10) ),
                33: (2, 28),
                34: (0, 8),
                35: (1, 5),
                36: (0, 9),
                37: (2, 30),
                38: (0, 30),
                39: ( (2, 31), (1, 7) ),
                40: ( (0, 28), (0, 31) ),
                41: ( (2, 10), (2, 13) ),
                42: ( (2, 7), (2, 0) ),
                43: (2, 12),
                44: (2, 5), 
                45: (2, 15),
                46: (2, 22),
                47: (2, 14),
                48: (2, 3),
                49: (None, None),
                50: (None, None)
        }

	SandiaRingTrap = 0
        GTRIGenIIITrap = 1
        trap_map = {
                SandiaRingTrap: ring_electrode_map,
                GTRIGenIIITrap: gtri_genIII_electrode_map
        }

	def __init__( self, trap ):
                self.electrode_map = self.trap_map[ trap ]
		self.hDAC = TaskHandle(0)
		samples_written = c_int32(0)
		
		# Create NI digital out task
		DAQmxCreateTask( c_char_p("DAC"), byref(self.hDAC) )
		DAQmxCreateDOChan( self.hDAC, self.device, None, 
			DAQmx_Val_ChanForAllLines )
		DAQmxStartTask( self.hDAC )
		
		# Write some initial data (maybe unnecessary?)
		DAQmxWriteDigitalU8( self.hDAC, 50, c_int32(True), self.timeout, 
			DAQmx_Val_GroupByScanNumber, self.init_data, 
			byref(samples_written), None )
		DAQmxStopTask( self.hDAC );

		self.offset( 0x2000 )		# Set range to center about 0
		self.voltage( None, 0. )	# Set all voltages to 0 initially
		self.voltages = [0]*self.nelectrodes

	def _build_frame( self, data1, data2, data3 ):
		"""Return the 24 bits of data at the falling clock cycles 
		with frame boundary signals packed into ctypes array."""
		# Initialized output with frame boundary signal
		out = [0] * 50
		out[0] = out[-1] = self.frame_bit
		
		data = [ data1, data2, data3 ]
		dbits = [ self.data1_bit, self.data2_bit, self.data3_bit ]
		or_fn = lambda x, y: x | y

		for i in range( 24 ):
			# Set data bit in val is corresponding bit in data set
			vals = (b if d>>i & 1 else 0 for b, d in zip( dbits, data ))
			val = reduce( or_fn, vals )

			# While outputing val output a clock pulse
			out[ 48 - i*2 ] |= val
			out[ 48 - i*2 - 1 ] |= val | self.clock_bit
		return self.update_data_type( *out )
		
	def _write_frame( self, data ):
		"Write data to NIDaqmx channel and assert all data written."
		samples_written = c_int32(0)

		# DAQmxWriteDigitalU8 arguments: 
		# 		channel, nsamp, autostart, timeout, 
		# 		grouping, data, output samples written, reserved
		DAQmxWriteDigitalU8( self.hDAC, c_int32(50), c_int32(True), 
			self.timeout, DAQmx_Val_GroupByScanNumber, 
			data, byref(samples_written), None )
		DAQmxWaitUntilTaskDone( self.hDAC, c_double(5.0) )

	def _voltage_data( self, channel, v ):
		"""Generate voltage data setting channel to v in volts, 
		sets all channels if channel is None."""
		if channel is not None and (channel < 0 or channel >= 32):
			return 0

		# Map voltage to digital value using min/max voltage
		r = self.max_voltage - self.min_voltage
		val = int( (v - self.min_voltage) / r * self.precision )
		val = max( 0, min( val, self.precision-1 ) )

		# target is 0 to update all channels, or as described below
		target = 0
		if channel is not None:
			group, channel = channel / 8, channel % 8
			target = (group+1) << 19 | channel << 16

		# Set first two bits to indicate we're writing to DAC register
		update_data_mode = 1 << 23 | 1 << 22
		data = update_data_mode | target | val
		return data

	def voltage( self, electrode, v ):
		"""Set electrode to v in volts. 
		If electrode is None, set all channels"""
		if electrode is not None:
			if electrode not in self.electrode_map:
				return
			# Get chip and channel from map and generate data
			chip, channel = self.electrode_map[ electrode ]
			vdata = self._voltage_data( channel, v )

			# Update given chip, send 0 (NOP) to others
			data = [0, 0, 0]
			data[ chip ] = vdata
			self.voltages[ electrode ] = v
		else:
			# Generate voltage data and send to all chips
			vdata = self._voltage_data( None, v )
 			data = [vdata]*3
			self.voltages = [v]*self.nelectrodes
		self._write_frame( self._build_frame( *data ) )

	def update( self, updates ):
		for electrode, v in updates:
			self.voltages[ electrode ] = v 

		# Get chip and channel including repeats
		tupled = lambda i: i if isinstance( i[0], tuple ) else ( i, )
		updates = sorted( (emap, v)
                                  for e, v in updates
                                  for emap in tupled(self.electrode_map[e]) )
		print updates

		# Iterate through 1 update per chip
		chips = [ filter( lambda v: v[0][0] == i, updates ) for i in range(3) ]
		for updates in izip_longest( *chips, fillvalue = (None,0) ):
			print updates

			# Build data or NOP if no more updates for this chip
			f = lambda ch, v: self._voltage_data( ch[1], v )
			data = [ (f(ch, v) if ch is not None else 0) for ch, v in updates ]

			# Write data
			self._write_frame( self._build_frame( *data ) )		
		
	def offset( self, off ):
		"Set offset registers to raw offset value given by off."
		off = max( 0, min( off, 1<<14 -1 ) )
		
		# Write offset to all OFS0 and OFS1 registers
		self._write_frame( self._build_frame( *[2<<16 | off]*3 ) )
		self._write_frame( self._build_frame( *[3<<16 | off]*3 ) )
		
	def __del__( self ):
		DAQmxClearTask( self.hDAC )
		DAQmxResetDevice( "Dev1" )

class JSONAPIRequestHandler( BaseHTTPRequestHandler ):
	def _send_headers( self, content_type, length ):
		self.send_response( 200 )
		self.send_header("Content-Type", content_type)
		self.send_header("Content-Length", length )
		self.send_header("Access-Control-Allow-Origin", "*")
		self.end_headers()
		
	def do_GET( self ):
		parse = urlparse.urlparse(self.path)
		self.path = parse.path

		params = None
		if parse.query:
			items = urlparse.parse_qs( parse.query ).items()
			params = dict([(k,int(v[0])) for k, v in items])
			
		if self.path in ('/recent', '/recent/'):
			self._recent( params["l"] if params else 0 )
			
		elif self.path == '/index.html':
			f = file('index.html', 'r')
			d = ''.join( f.readlines() )
			f.close()
			
			self._send_headers( "text/html", len(d) )
			self.wfile.write( d )
		else:
			self.send_response( 404 )

	def do_POST( self ):
		params = None
		if int(self.headers["Content-Length"]) != 0:
			params = self.rfile.read( int(self.headers["Content-Length"]) )
			params = urlparse.parse_qs( params )
			params = dict([(k,int(v[0])) for k, v in params.items()])
		
		if self.path in ('/recent', '/recent/'):
			self._recent( params["l"] if params else 0 )

		elif self.path in ('/parameters', '/parameters/'):
			if params:
				param_names = ['ch', 'ps', 'pg', 'is', 'ig', 'dg', 'lp'] 
				self.server.set_parameters( *map( lambda s: params[s], param_names ) )
			
			self._send_headers( "application/json", len(self.server.parameters) )
			self.wfile.write( self.server.parameters )

		else:
			self.send_response( 404 )
			
class JSONAPIServer( HTTPServer ):
	def __init__( self, addr, handler, dac ):
		HTTPServer.__init__( self, addr, handler )
		self.dac = dac

	def get_voltages( self ):
		return self.dac.voltages
		
	def set_voltage( self, electrode, v ):
		self.dac.voltage( electrode, v )
#server = JSONAPIServer(('', 8321), JSONAPIRequestHandler)

if __name__ == "__main__":
	c = DACController( DACController.SandiaRingTrap )
        
	# Open file and skip to first data line
	f = file( "electrodes.txt" )
	print "Opened 'electrodes.txt'."
	while f.readline().split()[0].strip() != "e00":
		pass

	# Update chip with first data line
	data = [ float(i.strip()) for i in f.readline().split() ]
	c.update( [(i, d) for i, d in enumerate(data) if d != 0. and i > 0 and i < 90] )
	print "DAC updated."

	#i = 0
	#while True:
	#	sleep(1.0)
	#	r = c.max_voltage - c.min_voltage
	#	c.voltage( None, c.max_voltage if i & 1 else c.max_voltage )
	#	i += 1
	del c


