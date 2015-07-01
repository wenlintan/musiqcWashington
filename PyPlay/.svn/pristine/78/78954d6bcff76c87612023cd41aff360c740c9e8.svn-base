
import sys, time
import httplib

from luca import Luca
from ni_digital_io import NiDriver

if len(sys.argv) < 4:
    print "usage: {0} <runs> <wait time (ms)> <ion_positions> <output>".format( sys.argv[0] )
    sys.exit( 0 )
    
runs = int( sys.argv[1] )
wait = int( sys.argv[2] )
ions = sys.argv[3]
output = open( sys.argv[4], 'a+' )

tlock = httplib.HTTPConnection( '192.168.1.100', 8321, timeout=10 )
tlock.connect()
tlock.request( 'POST', '/feedback_parameters', 'ch=0&pg={0}&ig={1}&lim={2}'.
    format( 5, 1, 30 ) )
response = tlock.getresponse()
if response.status != 200:
    print( "Could not communicate with temperature lock." )

camera = Luca()
ni = NiDriver( "PXI1Slot9/port0/line6" )

try:
    ion_positions = []
    with open( ions, 'r' ) as ionfile:
        for l in ionfile:
            pos = tuple( int(x) for x in l.split() )
            ion_positions.append( pos )

    for i in range( runs ):
        print "Run Number {0}".format( i )
        #filename = "{0}_{1}ms_{2}_initial.fits".format( prefix, wait, i )
        #camera.save_image( filename )
        image = camera.get_image()
        
        data = []
        sum_dist = 20
        for p in ion_positions:
            val = 0
            for ox in range( -sum_dist, sum_dist ):
                for oy in range( -sum_dist, sum_dist ):
                    val += image[ (p[1] + oy) * camera.width + p[0] + ox ]
            data.append( val )

        if not i % 10:
            flourescence = sum( d-data[-1] for d in data[:-1] )
            flourescence /= float( len(data)-1 )
            print( flourescence )
                
            tlock.request( 'POST', '/feedback', 'ch=0&err={0}'.
                format( int((flourescence - 45000) / 1000.) ) )
            response = tlock.getresponse()
            if response.status != 200:
                print( "Could not communicate with temperature lock." )
		
        output.write( '\t'.join( str(d) for d in data ) + '\n' )
        output.flush()

        
        ni.write_single( False )
        time.sleep( 0.001 * wait )
        ni.write_single( True )
        time.sleep(3.0)
      
finally:
    #tlock.close()
    camera.shutdown()
    ni.close()
