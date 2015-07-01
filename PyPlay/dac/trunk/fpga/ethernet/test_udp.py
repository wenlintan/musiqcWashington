#!/usr/bin/python

import socket
fpga = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
#fpga.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
fpga.settimeout( 0.5 )
fpga.bind( ('', 4325) )

data = [
    '\x00\x00\x00\x00\x01\xd9\x01\xf6',#*4,
    '\x00\x00\x00\x02\x0c\x00\x00\x00'
    ]

for d in data:
    response, tries = None, 0
    while response != d and tries < 5:
        try:
            print repr(d)
            fpga.sendto( d, 0, ('192.168.1.101', 4325) )
            response = fpga.recvfrom( 1024 )[0]
        except socket.error:
            tries += 1
    if tries == 5:
            raise ValueError( "No connection." )
        


