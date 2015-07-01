
from time import sleep
from ctypes import *

ni4882 = windll.ni4882
SendIFC = ni4882.SendIFC
ibdev = ni4882.ibdev
ibwrt = ni4882.ibwrt
ibonl = ni4882.ibonl

class SwitchController:
	channel_index = [9, 2, 3, 4, 7, 6, 11, 12, 1, 10, 5, 8, 13, 14, 15, 16]
	channel_map = dict( (i, v) for i, v in enumerate( channel_index ) )

	def __init__( self ):
		self.SendIFC( 0 )
		self.channel = 0
		self._send_srs( "OFFS 0.0" )

	def __del__( self ):
		ibonl( 0, 0 )	

	def switch( self, channel ):
		real_channel = self.channel_map[ channel - 1 ]
		
		hSwitch = ibdev( 0, 16, 0, 10, 1, 0 );
		cmd = "SWITCH:{1}".format( real_channel )

		ibwrt( hSwitch, cmd, len(cmd) )
		ibonl( hSwitch, 0 );

		sleep( 0.05 * abs(self.channel - real_channel) )
		self.channel = real_channel

	def _send_srs( self, cmd ):
		hSRS = ibdev( 0, 19, 0, 10, 5, 0 )
		ibwrt( hSRS, cmd, len(cmd) );
		ibonl( hSRS, 0 );

	def frequency( self, freq ):
		self._send_srs( "FREQ %0.2f" )

	def amplitude( self, ampl ):
		self._send_srs( "AMPL %0.2fVP" )
		
		
