
import os, sys, serial, struct
NCHANNELS = 1

serial.CR = b'\r\n'
ser = serial.Serial(3,19200, timeout=10, stopbits=serial.STOPBITS_TWO)
f = open( "out.txt", "w" )

while True:
	s = ser.readline()

	try:
		nojoy = True
		string = s.decode()
		if string[:-2] == "Start":
			f.write( "Start\n" )
			print("Start")
			#d = ""
			#while len(d) < struct.calcsize("<" + "l"*100)+2:
			#	d += ser.readline()
			#	print len(d)

			#print len(d)
			#print d
			#derivs = struct.unpack("<" + "l"*100, d[:400])
			#print derivs

			success = ser.readline().decode()[:-2]
			print(success)
			if success == "Yes":
				d = ""
				while len(d) < struct.calcsize("<L")+2:
					d += ser.readline()

				n = struct.unpack("<L", d[:4])[0]
				for i in range(n):
					d = ""
					while len(d) < struct.calcsize("<LLL")+2:
						d += ser.readline()
					center, val, max = struct.unpack("<LLL", d[:-2])
					print "Data", center, val, max
			else:
				print("Not found.")
			nojoy = False
	except Exception, e:
		print(e)
		nojoy = True
		
	if nojoy:
		while len(s) <  struct.calcsize("<L")+2:
			s += ser.readline()


		pt = struct.unpack("<L", s[:4])[0]
		f.write( str(pt) + '\n' )
	
ser.close()
f.close()