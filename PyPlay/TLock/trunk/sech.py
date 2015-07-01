
import time, logging, sys

from sequencer2 import sequencer, instructions
from sequencer2 import api
from sequencer2 import comm
from sequencer2 import ad9910
from sequencer2 import ptplog

# Set to true for testing without actual hardware
nonet = False

#Init sequencer, API and DDS
my_sequencer=sequencer.sequencer()
my_api=api.api(my_sequencer)
dds_device0 = ad9910.AD9910(0, 800) #args: device_addr, ref_freq, clk_divider=8

#=============================================================================
# Program Start (After boilerplate initialization (including DDS init)
#=============================================================================

#Digital Ramp and DDS Board Init here
my_api.init_dds(dds_device0)
my_api.wait(1.0)

my_api.dac_value(-20, 0) # -12 is the largest signal the DDS can output
my_api.set_dds_freq(dds_device0, 99, 0)

my_api.wait(1.0)
my_api.update_dds(dds_device0)
my_api.wait(1.0)

#my_api.init_digital_ramp_generator('freq', dds_device0, 0.1, 0.1, 0.1, 0.1, 10, 100)

from math import cosh

CFR1 = 0x00
FTW = 0x07
POW = 0x08
RAM_PROFILE_0 = 0x0E
RAM = 0x16

autoclear_phase = 1	# Automatically set in normal api
ram_enable = 1
ram_destination = 2	# Amplitude
ram_profile = 1

ram_enable = 1
ram_profile = 0
cfr1 = ram_enable << 31 | ram_destination << 29 | ram_profile << 17 | autoclear_phase << 13
my_api.dds_to_serial( cfr1, 32, CFR1 )
my_api.dds_to_serial( int(2**32 * 90. / 800.), 32, FTW )
my_api.dds_to_serial( 0, 16, POW )
my_api.update_dds( dds_device0 )

address_step_rate = 1
waveform_start = 1
waveform_end = 100
no_dwell = 0
zero_crossing = 0
mode_control = 3	# Continuous bidirectional ramp

profile = address_step_rate << 40 | waveform_end << 30 | waveform_start << 14 | no_dwell << 5 | zero_crossing << 3 | mode_control
my_api.dds_to_serial( profile, 64, RAM_PROFILE_0 )
my_api.update_dds( dds_device0 )

offset = 0
amplitude = 4095
f = lambda x: amplitude / cosh(x) + offset

lower_bound = -4.
upper_bound = 4.
scale = (upper_bound-lower_bound)/(waveform_end-waveform_start)
profile = [ int( f((x+waveform_start)*scale+lower_bound) ) << 18 for x in range( waveform_end - waveform_start ) ]
#profile = [ 4095 << 18 for x in range( waveform_end - waveform_start ) ]
profile.append( profile[-1] )

profile_val = 0
for i in range( len(profile) ):
	print profile[i] >> 18
	profile_val = profile_val << 32 | profile[i]
	
my_api.dds_to_serial( profile_val, 32*len(profile), RAM )
my_api.update_dds( dds_device0 )

ram_enable = 1
ram_profile = 0
cfr1 = ram_enable << 31 | ram_destination << 29 | ram_profile << 17 | autoclear_phase << 13
my_api.dds_to_serial( cfr1, 32, CFR1 )
my_api.update_dds( dds_device0 )


#=============================================================================
# Program end: Insert Boiler plate compilation below
#=============================================================================

#Compile sequence:
my_sequencer.compile_sequence()
#Debug sequence
# my_sequencer.debug_sequence()
time2=time.time()
# logger.logger.info("compile time: "+str(time2-time1))
ptp1 = comm.PTPComm(nonet=nonet)
ptp1.send_code(my_sequencer.word_list)
# time3=time.time()
# logger.logger.info("ptp time: "+str(time3-time2))

