
import time

from luca import Luca
from freq import FreqDriver
from ni_digital_io import NiDriver
from ni_simple_digital_io import NiDriver as NiSimpleDriver

class ExperimentBase:
    def build_waveform( self, dark_time, shelve_time ):
        waveform = [self.Pockels | self.Red | self.Blue] * 2000
        waveform.extend( [self.Pockels | self.Red] * 10 )
        waveform.extend( [self.Pockels] * 10 )

        waveform.extend( [self.Orange] * dark_time )
        waveform.extend( [0] * 10 )

        waveform.extend( [self.Shelve] * shelve_time )
        waveform.extend( [0] * 10 )
        waveform.extend( [self.Red | self.Blue] * 10 )
        return waveform

class RabiFlop( ExperimentBase ):
    def __init__( self, start_time, stop_time, time_step, frequency ):
        self.current_time = start_time
        self.stop_time = stop_time
        self.time_step = time_step
        self.frequency = frequency
        
    def setup( self, freq_driver, ni_driver ):
        self.freq_driver.set_frequency( self.frequency, 2.5 )

    def step( self, freq_driver, ni_driver ):
        self.current_time += self.time_step
        if self.current_time > self.stop_time:
            return False
        self.ni_driver.set_samples( self.build_waveform( 0, self.current_time ) )
        return True
    def control_var()
        return self.current_time

class FreqScan( ExperimentBase ):
    def __init__( self, start_freq, stop_freq, freq_step, pulse_duration ):
        self.current_freq = start_freq
        self.stop_freq = stop_freq
        self.freq_step = freq_step
        self.pulse_duration = pulse_duration

    def setup( self, freq_driver, ni_driver ):
        self.ni_driver.set_samples( self.build_waveform( 0, self.pulse_duration ) )

    def step( self, freq_driver, ni_driver ):
        self.current_freq += self.freq_step
        if self.current_freq > self.stop_freq:
            return False
        self.freq_driver.set_frequency( self.current_frequency, 2.5 )
        return True
    def control_var()
        return self.current_freq



class Experiment:
    PockelsChan = "PXI1Slot9/port0/line2"
    RedChan = "PXI1Slot9/port0/line7"
    BlueChan = "PXI1Slot9/port0/line6"
    OrangeChan = "PXI1Slot9/port0/line5"
    ShelveChan = "PXI1Slot9/port0/line1"
    Chans = ",".join( [PockelsChan, RedChan, 
        BlueChan, OrangeChan, ShelveChan] )

    Pockels = 1 << 2
    Red = 1 << 7
    Blue = 1 << 6
    Orange = 1 << 5
    Shelve = 1 << 1
    
    def __init__( self, nruns, experiment, ions, desired_order, out, conn=None ):

        camera = Luca()
        freq_src = FreqDriver( u'USB0::0x1AB1::0x0641::DG4B142100247::INSTR' )
        output = open( out, 'w' )
        ion_order = []

        try:
            ion_positions = []
            with open( ions, 'r' ) as ionfile:
                for l in ionfile:
                    pos = tuple( int(x) for x in l.split() )
                    ion_positions.append( pos )
	
	    bg = 0
            for i in range(20):
                data = self.build_data(camera, ion_positions, camera.get_image())
                bg += data[-1]/20
            
            experiment.setup()
            while experiment.step():
                for i in range( nruns ):
                    while ion_order_before != desired_order and wrongbrights.all():
                        data = self.build_data( 
				camera, ion_positions, camera.get_image() )
                        ion_order_before = [True if x > bg else False for x in data]
                        ni = NiDriver( self.Chans, wf )
                        data2 = self.build_data( 
                            camera, ion_positions, camera.get_image() )
                        ion_order_after = [True if x > bg else False for x in data]
                        wrongbrights = [False for i,j in zip(desired_order,ion_order_after) if j != i and j == 1]
                        data.extend(data2) 
                    	d = NiSimpleDriver( self.OrangeChan )
                    	d.write_single( True )
                    	d.close()
			if ion_order_before != desired_order and wrongbrights.all():
			    r = NiSimpleDriver( self.RedChan )
			    r.write_single( False )
			    time.sleep( 0.2 )
			    r.write(single( True ) )
			    r.close()
                    outdata = [str(experiment.control_var())]
                    outdata.extend( str(d) for d in data )
                    print '\t'.join(outdata)
                    if conn is not None:
                        conn.send( '\t'.join(outdata) )
                    output.write( '\t'.join(outdata) + '\n' )
                    output.flush()

                    d = NiSimpleDriver( self.OrangeChan )
                    d.write_single( True )
                    d.close()

                    time.sleep( 0.2 )
              
              
        finally:
            camera.shutdown()


    def build_data( self, camera, ionpos, image ):
        data = []
        sum_dist = 20
        for p in ionpos:
            val = 0
            for ox in range( -sum_dist, sum_dist ):
                for oy in range( -sum_dist, sum_dist ):
                    val += image[ (p[1] + oy) * camera.width + p[0] + ox ]
            data.append( val )
        return data

    def fix_order():
        
if __name__ == '__main__':
    import sys
    if len(sys.argv) < 4:
        print "usage: {0} <nruns> <high freq (MHz)> <low freq (MHz)> \
            <freq step(MHz)> <1762 pulse length (us)> <ion_positions> \
            <output>".format( sys.argv[0] )
        sys.exit( 0 )
    nruns = int( sys.argv[1] )
    current_freq = float( sys.argv[2] )
    stop_freq = float( sys.argv[3] )
    freq_step = float( sys.argv[4] )
    pulse_len = int( sys.argv[5] )
    ions = sys.argv[6]
    output = sys.argv[7]

    Experiment( nruns, current_freq, stop_freq, freq_step, pulse_len,
        ions, output, None )

