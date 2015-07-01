#!/usr/bin/python
import socket, struct

class FPGAUpload:
	def __init__( self, start_address = 0 ):
		self.fpga = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
		#self.fpga.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
		self.fpga.bind( ('', 4325) )

		self.address = start_address

	def upload( self, chip, voltage_data ):
		d = struct.pack( 'hhhh', 
			self.address >> 16, self.address & (1<<16-1), 
			chip << 8 | voltage_data >> 16, voltage_data & (1<<16-1) )
		
		response = None
		while response != d:
			self.fpga.sendto( d, 0, ('192.168.1.101', 4325) )
			response = self.fpga.recvfrom( 1024 )

		self.address += 1

