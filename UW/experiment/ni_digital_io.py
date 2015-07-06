
from ctypes import *

class NiDriver:
    daqmx = windll.nicaiu
    TaskHandle = c_void_p
    CreateTask = daqmx.DAQmxCreateTask
    StartTask = daqmx.DAQmxStartTask
    StopTask = daqmx.DAQmxStopTask
    ClearTask = daqmx.DAQmxClearTask
    WaitUntilTaskDone = daqmx.DAQmxWaitUntilTaskDone
    ResetDevice = daqmx.DAQmxResetDevice

    CfgSampClkTiming = daqmx.DAQmxCfgSampClkTiming
    CfgImplicitTiming = daqmx.DAQmxCfgImplicitTiming
    CfgDigEdgeStartTrig = daqmx.DAQmxCfgDigEdgeStartTrig
    CreateDOChan = daqmx.DAQmxCreateDOChan
    CreateCOPulseChanFreq = daqmx.DAQmxCreateCOPulseChanFreq
    WriteDigitalU8 = daqmx.DAQmxWriteDigitalU8
    WriteDigitalLines = daqmx.DAQmxWriteDigitalLines

    # From NIDAQmx.h
    DAQmx_Val_ChanForAllLines = 1
    DAQmx_Val_GroupByChannel = 0
    DAQmx_Val_GroupByScanNumber = 1
    DAQmx_Val_WaitInfinitely = c_double(-1.0)

    DAQmx_Val_FiniteSamps = 10178
    DAQmx_Val_Rising = 10280
    DAQmx_Val_Hz = 10373
    DAQmx_Val_Low = 10214

    hExp = TaskHandle(0)
    hClock = TaskHandle(0)

    samples_written = c_int32(0)
    timeout = c_double( 10.0 )
    
    def __init__(self, channel_names):
        self.channel_names = channel_names
        self.samples = None

    def set_samples( self, samples ):
        self.nsamples = len( samples )
        self.samples = (c_uint8 * len(samples))( *samples)

    def run( self ):
        if self.samples is None:
            return

        # Create NI digital out task
        self.CreateTask( c_char_p("Exp"), byref(self.hExp) )
        self.CreateDOChan( self.hExp, c_char_p(self.channel_names), None, 
            self.DAQmx_Val_ChanForAllLines )
        self.CfgSampClkTiming( self.hExp, 
            c_char_p("/PXI1Slot9/ctr1InternalOutput"),
            c_double(1000000), self.DAQmx_Val_Rising, 
            self.DAQmx_Val_FiniteSamps, c_int64(self.nsamples) )

        # Create NI clock/triggering task
        self.CreateTask( c_char_p("Clock"), byref(self.hClock) )
        self.CreateCOPulseChanFreq( self.hClock, 
            c_char_p("/PXI1Slot9/ctr1"), None,
            self.DAQmx_Val_Hz, self.DAQmx_Val_Low, c_double(0),
            c_double(1000000), c_double(0.5) )
        self.CfgImplicitTiming( self.hClock,
            self.DAQmx_Val_FiniteSamps, c_int64(self.nsamples) )
        self.CfgDigEdgeStartTrig( self.hClock,
            c_char_p("/PXI1Slot9/PFI2"), self.DAQmx_Val_Rising )
        

        self.WriteDigitalU8( self.hExp, c_int32(self.nsamples),
            c_int32(False), self.timeout, 
            self.DAQmx_Val_GroupByChannel, self.samples, 
            byref(self.samples_written), None )
        
        self.StartTask( self.hExp )
        self.StartTask( self.hClock )
        self.WaitUntilTaskDone( self.hClock, self.timeout )
        self.WaitUntilTaskDone( self.hExp, self.timeout )
        self.StopTask( self.hClock )
        self.StopTask( self.hExp )
        
        self.ClearTask( self.hExp )
        self.ClearTask( self.hClock )
    
