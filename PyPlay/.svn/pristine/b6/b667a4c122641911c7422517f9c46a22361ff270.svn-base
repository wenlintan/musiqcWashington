
import math
import socket, time, struct

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 7777))
s.listen(1)

conn, addr = s.accept()
print 'Connected by', addr
i = 0
while 1:
	#data = conn.recv(1024)
	i = (i+1) % 2000
	o = [ 1e8*math.sin(i * 2 * math.pi / 2000 + j)**2 for j in [0, 500, 1000] ]
	data = struct.pack( "<LLLLlLllLllLl", 8, 2, 0, 16, 0, o[0], 0, 0, o[1], 0, 0, o[2], 0 )
	conn.send( data )
	conn.send( '\r\n' )
	time.sleep(1)
conn.close()
