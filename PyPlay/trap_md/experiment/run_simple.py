
import sys, time

from luca import Luca
from ni_digital_io import NiDriver

if len(sys.argv) < 4:
    print "usage: {0} <runs> <prefix> <wait time (ms)>".format( sys.argv[0] )
    sys.exit( 0 )
    
runs = int( sys.argv[1] )
prefix = sys.argv[2]
wait = int( sys.argv[3] )
# scramble_wait = int( sys.argv[4] )

camera = Luca()
ni = NiDriver( "PXI1Slot9/port0/line7" )

for i in range( runs ):
    print "Run Number {0}".format( i )
    filename = "{0}_{1}ms_{2}_initial.fits".format( prefix, wait, i )
    camera.save_image( filename )

    
    ni.write_single( False )
    time.sleep( 0.001 * wait )
    ni.write_single( True )
    time.sleep(0.1)

    #filename = "{0}_{1}ms_{2}_final.fits".format( prefix, wait, i )
    #camera.save_image( filename )

"""    if scramble_wait:
        ni.write_single( False )
        time.sleep( 0.001 * scramble_wait )
        ni.write_single( True )
"""        
