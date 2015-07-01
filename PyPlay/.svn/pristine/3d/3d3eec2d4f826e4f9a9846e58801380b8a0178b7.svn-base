
from ctypes import *
from time import sleep

wlmdata = windll.wlmdata
SetExposureMode = wlmdata.SetExposureMode
SetResultMode = wlmdata.SetResultMode
SetRange = wlmdata.SetRange
SetPulseMode = wlmdata.SetPulseMode
SetWideMode = wlmdata.SetWideMode
SetFastMode = wlmdata.SetFastMode
SetDisplayMode = wlmdata.SetDisplayMode
SetExposure = wlmdata.SetExposure
SetPattern = wlmdata.SetPattern

GetMaxPeak = wlmdata.GetMaxPeak
GetMinPeak = wlmdata.GetMinPeak
GetFrequency = wlmdata.GetFrequency
GetPatternData = wlmdata.GetPatternData
GetPatternItemCount = wlmdata.GetPatternItemCount

# From wlmData.h
cRange_400_725 = 1
cSignal1Interferometers = 0

class WavemeterController:
	on_threshold = 150

	def __init__( self ):
		SetExposureMode( False )
		SetResultMode( 2 )
		SetRange( cRange_400_725 )
		SetPulseMode( 0 )
		SetWideMode( 0 )
		SetFastMode( True )
		
		SetDisplayMode( 0 )		# show no interference pattern
		self.exposure_time( 0.1 )

	def exposure_time( self, t ):
		self.exp_time = t
		SetExposure( self.exp_time )

	def light_on( self ):
		sleep( self.exp_time + 0.01 )
		return (GetMaxPeak(0) - GetMinPeak(0) > self.on_threshold

	def frequency( self, ave_n = 1 ):
		freq = 0
		for i in range( ave_n ):
			sleep( self.exp_time ):
			freq += GetFrequency( 0 )
		return freq / ave_n

	def contrast( self ):
		return GetMaxPeak(0) - GetMinPeak(0)

	def interference_pattern( self ):
		SetPattern( cSignal1Interferometers, 1 )
		n = GetPatternItemCount( cSignalInterferometers )
		data = c_ulong * n
		GetPatternData( cSignalInterferometers, data )
		return array(data)


