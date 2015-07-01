import serial
ser = serial.Serial(2)  # open first serial port
print ser.portstr       # check which port was really used


while( 1 ):
    for i in range( 10 ):
        s = ser.read( 1 )
        print ord(s),
    print
        
##s = ser.read( 1000 )
##for i in range( 100 ):
##    for j in range( 10 ):
##        print ord( s[i*10+j] ),
##
##    print

ser.close()
