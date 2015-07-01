
from ctypes import *

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
	channel_index = [ 0, 1, 8, 3, 4, 5, 6, 7, 2 ]
	channel_map = dict( (i, v) for i, v in enumerate( channel_index ) )

	max_voltage = 4.99
	precision = 1 << 12
	timeout = c_double( 10.0 )

	device = "Dev1/port0/line0:7"

	update_data_type = c_uint8 * 34
	init_bit = 1 << 7
	frame_bit = 1 << 6
	clock_bit = 1 << 5
	data_bit = 1 << 4
	init_data = update_data_type( *([init_bit] * 34) )
	

	def __init__( self ):
		self.hDAC = TaskHandle(0)
		samples_written = c_int32(0)

		DAQmxCreateTask( c_char_p("DAC"), byref(self.hDAC) )
		DAQmxCreateDOChan( self.hDAC, self.device, None, DAQmx_Val_ChanForAllLines )
		DAQmxStartTask( self.hDAC )
		
		# arguments: channel, nsamp, autostart, timeout, grouping, data, output samples written, reserved
		DAQmxWriteDigitalU8( self.hDAC, 34, c_int32(True), self.timeout, DAQmx_Val_GroupByScanNumber, self.init_data, byref(samples_written), None )
		DAQmxStopTask( self.hDAC );

	def _build_frame( self, ch, data ):
		out = [ self.init_bit ] * 34
		data = ( self.channel_map[ ch ] -1 ) << 12 | data
		for i in range( 16 ):
			val = self.frame_bit | self.data_bit if data & 1 else self.frame_bit
			out[ 32 - i*2 ] |= val
			out[ 32 - i*2 - 1 ] |= val | self.clock_bit
			data >>= 1
		return self.update_data_type( *out )

	def voltage( self, ch, v ):
		if ch < 0 or ch >= len( self.channel_index ):
			return

		val = int( ( v / self.max_voltage ) * self.precision )
		val = max( 0, min( val, self.precision-1 ) )
		samples_written = c_int32(0)

		data = self._build_frame( ch, val )
		err = DAQmxWriteDigitalU8( self.hDAC, 34, c_int32(True), self.timeout, DAQmx_Val_GroupByScanNumber, data, byref(samples_written), None )
		err = DAQmxWaitUntilTaskDone( self.hDAC, DAQmx_Val_WaitInfinitely )
		print "Wrote:", samples_written

	def __del__( self ):
		DAQmxClearTask( self.hDAC )
		DAQmxResetDevice( "Dev1" )

if __name__ == "__main__":
	c = DACController()
	c.voltage( 2, 3.2 )
	del c


