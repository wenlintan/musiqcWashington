
import sys, time

from luca import Luca
from freq import FreqDriver
from ni_digital_io import NiDriver
from ni_simple_digital_io import NiDriver as NiSimpleDriver

if len(sys.argv) < 4:
    print "usage: {0} <nruns> <start time (us)> <stop time (us)> \
        <time step(us)> <dark time (us)> <ion_positions> <output>".format( sys.argv[0] )
    sys.exit( 0 )
    
nruns = int( sys.argv[1] )
current_time = int( sys.argv[2] )
stop_time = int( sys.argv[3] )
time_step = int( sys.argv[4] )
dark_time = int( sys.argv[5] )
ions = sys.argv[6]
output = open( sys.argv[7], 'w' )

PockelsChan = "PXI1Slot9/port0/line2"
RedChan = "PXI1Slot9/port0/line7"
BlueChan = "PXI1Slot9/port0/line6"
OrangeChan = "PXI1Slot9/port0/line5"
ShelveChan = "PXI1Slot9/port0/line1"
Chans = ",".join( [PockelsChan, RedChan, BlueChan, OrangeChan, ShelveChan] )

Pockels = 1 << 2
Red = 1 << 7
Blue = 1 << 6
Orange = 1 << 5
Shelve = 1 << 1

camera = Luca()
freqsrc = FreqDriver( u'USB0::0x1AB1::0x0641::DG4B142100247::INSTR' )

def build_waveform( dark_time, shelve_time ):
    waveform = [Pockels | Red | Blue] * 2000
    waveform.extend( [Pockels | Red] * 10 )
    waveform.extend( [Pockels] * 10 )

    waveform.extend( [Orange] * dark_time )
    waveform.extend( [0] * 10 )

    waveform.extend( [Shelve] * shelve_time )
    waveform.extend( [0] * 10 )
    waveform.extend( [Red | Blue] * 10 )
    return waveform

def build_data( ionpos, image ):
    data = []
    sum_dist = 20
    for p in ionpos:
        val = 0
        for ox in range( -sum_dist, sum_dist ):
            for oy in range( -sum_dist, sum_dist ):
                val += image[ (p[1] + oy) * camera.width + p[0] + ox ]
        data.append( val )
    return data
    
try:
    ion_positions = []
    with open( ions, 'r' ) as ionfile:
        for l in ionfile:
            pos = tuple( int(x) for x in l.split() )
            ion_positions.append( pos )

    while current_time < stop_time:
        wf = build_waveform( dark_time, current_time )
        for i in range( nruns ):
            data = build_data( ion_positions, camera.get_image() )
            ni = NiDriver( Chans, wf )
            data.extend( build_data( ion_positions, camera.get_image() ) )
            image = camera.get_image()

            outdata = [str(current_time)]
            outdata.extend( str(d) for d in data )
            print "Data: {0}".format( outdata )
            output.write( '\t'.join(outdata) + '\n' )
            output.flush()

            d = NiSimpleDriver( OrangeChan )
            d.write_single( True )
            d.close()

            time.sleep( 0.2 )
        current_time += time_step

      
finally:
    camera.shutdown()
