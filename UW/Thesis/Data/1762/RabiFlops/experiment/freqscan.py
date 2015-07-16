
import time

from luca import Luca
from freq import FreqDriver
from ni_digital_io import NiDriver
from ni_simple_digital_io import NiDriver as NiSimpleDriver
import numpy as np

class ExperimentBase:
    Pockels = 1 << 2
    Red = 1 << 7
    Blue = 1 << 6
    Orange = 1 << 5
    Shelve = 1 << 1
    
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
        self.freq_driver = freq_driver
        self.ni_driver = ni_driver
        self.freq_driver.set_frequency( self.frequency, 2.5 )

    def step( self, freq_driver, ni_driver ):
        if self.current_time > self.stop_time:
            return False
        self.ni_driver.set_samples( self.build_waveform( 0, self.current_time ) )
        self.current_time += self.time_step
        return True

    def control_var( self ):
        return self.current_time - self.time_step

class FreqScan( ExperimentBase ):
    def __init__( self, start_freq, stop_freq, freq_step, pulse_duration ):
        self.current_freq = start_freq
        self.stop_freq = stop_freq
        self.freq_step = freq_step
        self.pulse_duration = pulse_duration

    def setup( self, freq_driver, ni_driver ):
        self.freq_driver = freq_driver
        self.ni_driver = ni_driver
        self.ni_driver.set_samples( self.build_waveform( 0, self.pulse_duration ) )

    def step( self, freq_driver, ni_driver ):
        if self.current_freq > self.stop_freq:
            return False
        self.freq_driver.set_frequency( self.current_freq, 2.5 )
        self.current_freq += self.freq_step
        return True

    def control_var( self ):
        return self.current_freq - self.freq_step

class Experiment:
    PockelsChan = "PXI1Slot9/port0/line2"
    RedChan = "PXI1Slot9/port0/line7"
    BlueChan = "PXI1Slot9/port0/line6"
    OrangeChan = "PXI1Slot9/port0/line5"
    ShelveChan = "PXI1Slot9/port0/line1"
    Chans = ",".join( [PockelsChan, RedChan, 
        BlueChan, OrangeChan, ShelveChan] )
   
    def __init__( self, nruns, experiment, ions, desired_order, out, conn=None ):
        #0 = no sym, use order 1 = symmetrize on order 2 = no order specificity
        camera = Luca()
        freq_src = FreqDriver( u'USB0::0x1AB1::0x0641::DG4B142100247::INSTR' )
        ni = NiDriver( self.Chans )
        reorder_time = 0.5

        output = open( out, 'w' )
        ion_order = []
        ion_configs = {} #dictionary to hold different ion configurations (keys) and their reordering time (values)
        ion_configs[str(desired_order)] = 0.0 #don't need a reordering time for the desired ordering
        desired_bright_number = sum(map(lambda x: 1 if x else 0, desired_order))

        try:
            ion_positions = []
            with open( ions, 'r' ) as ionfile:
                for l in ionfile:
                    pos = tuple( int(x) for x in l.split() )
                    ion_positions.append( pos )
    
            bg = []
            for i in range(30):
                data = self.build_data(camera, ion_positions, camera.get_image())
                bg.append( data[-1] )
            threshold = np.mean(bg) + 3*np.std(bg)
            
            experiment.setup( freq_src, ni )
            print( ion_positions )

            ##########################################
            #CHANGES BEING MADE BELOW-----------------
            ##########################################			
            while experiment.step( freq_src, ni ):
                num_succ = [0 for i in ion_positions] # number of successes for each ion
                index = 0 #number of time it has run
                while index<nruns: #allows dynamic nruns switching
                    data = self.build_data( 
                        camera, ion_positions, camera.get_image() )
                    ion_order = [ d > threshold for d in data ]

                    for i in  range(len(num_succ)):
                        if ion_order[i]:
                            num_succ[i]+=1 #counts number of successes (bright) for corresponding ion in that position

                    if index+1==20: #since it starts at 0 need to add 1
                        num_succ = [x/float(index+1) for x in num_succ] #array holding proportion of successes for each ion respectively
                        #subtracts from 0.5 so that we can find which is closest to 50%
                        min_prop = np.abs(0.5-num_succ[0]) #minimum modified proportion (the smallest is the one closest to 50%)
                        prop_succ = num_succ[0] #this is the actual proportion we want (could replace this variable
                        #using props[0]+.5

                        #--------finds proportion closest to 50%------------------
                        for i in range(len(num_succ)):
                            mod_prop = np.abs(0.5-num_succ[i])
                            if min_prop > mod_prop:
                                min_prop = mod_prop
                                prop_succ = num_succ[i]

                        binomial_StdErr = self.binStdrderr(index+1,prop_succ) #finds binomial standard error
                        if binomial_StdErr<0.05:
                            nruns = 20 #this will force the program to break out of this while loop
                            #T print binomial_StdErr, nruns
                        else:
                            nruns = 50
                            #T print binomial_StdErr, nruns

                    bg.append( data[-1] )
                    if len( bg ) > 1000:
                        bg = bg[100:]
                    threshold = np.mean(bg) + 3*np.std(bg)

                    while ion_order != desired_order:
                        #seems this loop is designed to allow ions to reorganize
                        #by turning off cooling lasers

                        ion_key =  ['1' if x else '0' for x in ion_order] #these create the key for our ion_configs dictionary
                        ion_key = ''.join(ion_key) # and turns it into a string so the dictionary can use it
                        if ion_key not in ion_configs.keys() and ion_key!=str(desired_order):
                            ion_configs[ion_key] = reorder_time #this initializes the unseen ion order to reorder time of 0.5

                        curr_bright_number = sum(map(lambda x: 1 if x else 0, ion_order))
                        if curr_bright_number == desired_bright_number:
                            
                            r = NiSimpleDriver( self.RedChan )
                            r.write_single( False )
                            time.sleep(ion_configs[ion_key]) #ion_configs[ion_key] accesses the reorder time stored there
                            r.write_single( True )
                            r.close()
                        time.sleep( 1.0 )

                        camera.get_image()
                        data = self.build_data( 
                            camera, ion_positions, camera.get_image() )
                        
                        prev_order, ion_order = ion_order, \
                            [ d > threshold for d in data ]
                        print( "{} -> {}".format( prev_order, ion_order ) )

                        if any( prev_order ):
                            if prev_order == ion_order:
                                ion_configs[ion_key] *= 1.1
                            else:
                                ion_key =  ['1' if x else '0' for x in ion_order] #these create the key for our ion_configs dictionary
                                ion_key = ''.join(ion_key) # and turns it into a string so the dictionary can use it
                                if ion_key not in ion_configs.keys() and ion_key!=str(desired_order):
                                    ion_configs[ion_key] = reorder_time #this initializes the unseen ion order to reorder time of 0.5
                                ion_configs[ion_key] *= 0.9
                            print( "New reorder time: {}".format( ion_configs[ion_key] ) )
                        if ion_configs[ion_key] < 0.1:  ion_configs[ion_key] = 0.1
                        if ion_configs[ion_key] > 10.0: ion_configs[ion_key] = 10.0
                        
                        if conn is not None:
                            outdata = [str( experiment.control_var() )]
                            outdata.extend( str(d) for d in data )
                            outdata.extend( str(d) for d in data )
                            conn.send( 'reordata ' + '\t'.join(outdata) )
                    
                    ni.run()
                    data.extend( self.build_data( 
                        camera, ion_positions, camera.get_image() ) )

                    outdata = [str( experiment.control_var() )]
                    outdata.extend( str(d) for d in data )
                    print '\t'.join(outdata)
                    if conn is not None:
                        conn.send('\t'.join(outdata) )
                    output.write( '\t'.join(outdata) + '\n' )
                    output.flush()

                    d = NiSimpleDriver( self.OrangeChan )
                    d.write_single( True )
                    d.close()

                    time.sleep( 0.2 )
                    index+=1 #new code

        finally:
            camera.shutdown()

    #following builds array of fluorescence for different ions based on camera
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

    def binStdrderr(self, n,p,z=1.0):
    #finds standard error for a binomial distribution
    #n = # of runs, p = proportion of successes
        se = z*np.sqrt((1/(n*1.0))*p*(1-p)+(1/(4.0*n*n))*z*z)
        return se

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

