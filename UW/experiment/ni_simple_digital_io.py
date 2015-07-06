
from ctypes import *

class NiDriver:
    
    daqmx = windll.nicaiu
    TaskHandle = c_void_p
    CreateTask = daqmx.DAQmxCreateTask
    StartTask = daqmx.DAQmxStartTask
    StopTask = daqmx.DAQmxStopTask
    ClearTask = daqmx.DAQmxClearTask
    ResetDevice = daqmx.DAQmxResetDevice
    CreateDOChan = daqmx.DAQmxCreateDOChan
    WriteDigitalU8 = daqmx.DAQmxWriteDigitalU8
    WaitUntilTaskDone = daqmx.DAQmxWaitUntilTaskDone

    #From NIDAQmx.h
    DAQmx_Val_ChanPerLine = 0
    DAQmx_Val_ChanForAllLines = 1
    
    DAQmx_Val_GroupByChannel  = 0
    DAQmx_Val_GroupByScanNumber = 1
    DAQmx_Val_WaitInfinitely = c_double(-1.0)
    
    def __init__( self, devname ):
        self.hDAC = self.TaskHandle(0)
        self.samples_written = c_int32(0)
        self.timeout = c_double( 10.0 )
        
        # Create NI digital out task
        self.CreateTask( c_char_p("DAC"), byref(self.hDAC) )
        self.CreateDOChan( self.hDAC, devname, None, self.DAQmx_Val_ChanPerLine )

    def write_single( self, boolean ):
        output = (c_uint8*2)( 0, 0 )
        if boolean:
            output = (c_uint8*2)( 255, 255 )
            
        self.WriteDigitalU8( self.hDAC, 2, c_int32(True), self.timeout, 
            self.DAQmx_Val_GroupByScanNumber, output, 
            byref(self.samples_written), None )
        self.WaitUntilTaskDone( self.hDAC, c_double(5.0) )
        
    def close( self ):
        self.ClearTask( self.hDAC )
        
if __name__ == "__main__":
    import sys
    if len( sys.argv ) < 3:
        print "usage: {0} device boolean".format( sys.argv[0] )
        sys.exit(0)
        
    d = NiDriver( sys.argv[1] )
    d.write_single( int(sys.argv[2]) )
    d.close()
    
        