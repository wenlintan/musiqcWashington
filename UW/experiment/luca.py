
import time
#import numpy

from ctypes import *
from ctypes.wintypes import HANDLE
#import win32event

class Luca:
    exposure_time = 0.1
    EMCCD_gain = 200
    bin_size = 1
    acquiring = False
    
    atmcd = windll.atmcd32d
    
    AC_ACQMODE_SINGLESCAN = 1
    AC_ACQMODE_RUNTILABORT = 5
    #AC_ACQMODE_VIDEO = 2
    #AC_ACQMODE_ACCUMULATE = 4
    #AC_ACQMODE_KINETIC = 8
    #AC_ACQMODE_FRAMETRANSFER = 16
    #AC_ACQMODE_FASTKINETICS = 32
    #AC_ACQMODE_OVERLAP = 64
    
    AC_READMODE_IMAGE = 4
    #AC_READMODE_FULLIMAGE = 1
    #AC_READMODE_SUBIMAGE = 2
    #AC_READMODE_SINGLETRACK = 4
    #AC_READMODE_FVB = 8
    #AC_READMODE_MULTITRACK = 16
    #AC_READMODE_RANDOMTRACK = 32
    #AC_READMODE_MULTITRACKSCAN = 64

    AC_TRIGGERMODE_INTERNAL = 0
    AC_TRIGGERMODE_EXTERNAL = 1
    #AC_TRIGGERMODE_EXTERNAL_FVB_EM = 4
    #AC_TRIGGERMODE_CONTINUOUS = 8
    #AC_TRIGGERMODE_EXTERNALSTART = 16
    #AC_TRIGGERMODE_EXTERNALEXPOSURE = 32
    #AC_TRIGGERMODE_INVERTED = 0x40
    #AC_TRIGGERMODE_EXTERNAL_CHARGESHIFTING = 0x80
    
    def __init__( self ):
        self.initialize()
        self.acquiring = False
        self.event = None
        
    def initialize( self ):
        he = self._handle_error
        
        try:
            camera_handle, ncameras = c_long( 0 ), c_long( 0 )
            he( self.atmcd.GetAvailableCameras( byref(ncameras) ), "GetAvailableCameras" )
            print "Andor SDK has {0} camera(s) available, choosing first available".format( ncameras.value )
            
            for i in range( ncameras.value ):
                he( self.atmcd.GetCameraHandle( c_long(i), byref(camera_handle) ), "GetCameraHandle" )
                he( self.atmcd.SetCurrentCamera( camera_handle ), "SetCurrentCamera" )
                self.handle = camera_handle
                
                try:
                    print "Initializing Andor software, this will take a few moments"
                    he( self.atmcd.Initialize( c_char_p( "" ) ), "Initialize" )
            
                    serial = c_int( 0 )
                    he( self.atmcd.GetCameraSerialNumber( byref(serial) ), "GetCameraSerialNumber" )
                    print "Initialized camera {0} with serial {1}".format( i, serial.value )
                    break
                    
                except ValueError:
                    print "Failed to initialize camera {0}.".format( i )
                    self.atmcd.ShutDown()

            he( self.atmcd.SetAcquisitionMode( self.AC_ACQMODE_RUNTILABORT ), "SetAcquisitionMode" )
            he( self.atmcd.SetReadMode( self.AC_READMODE_IMAGE ), "SetReadMode" )
            he( self.atmcd.SetFrameTransferMode( c_long(1) ), "SetFrameTransferMode" )
            he( self.atmcd.SetTriggerMode( self.AC_TRIGGERMODE_INTERNAL ), "SetTriggerMode" )
            he( self.atmcd.SetShutter( c_int(0), c_int(0), c_int(0), c_int(0) ), "SetShutter" )
            
            self.set_image_and_binning()            
            
            num_vs_speeds = c_long( 0 )
            he( self.atmcd.SetHSSpeed( c_long(0), c_long(0) ), "SetHSSpeed" )
            he( self.atmcd.GetNumberVSSpeeds( byref( num_vs_speeds ) ), "GetNumberVSSpeeds" )
            he( self.atmcd.SetVSSpeed( c_long( num_vs_speeds.value-1 ) ), "SetVSSpeed" )
            
            he( self.atmcd.SetKineticCycleTime( c_float(0.) ), "SetKineticCycleTime" )
            self.set_gain_and_exposure()
        except ValueError as exc:
            print exc
        
    def _exposure_time_changed( self ):
        self.set_gain_and_exposure()
        
    def _EMCCD_gain_changed( self ):
        self.set_gain_and_exposure()
        
    def set_gain_and_exposure( self ):
        if self.acquiring: 
            return False
            
        he = self._handle_error
        try:
            he( self.atmcd.SetExposureTime( c_float(self.exposure_time) ), "SetExposureTime" )
            he( self.atmcd.SetEMCCDGain( c_long(self.EMCCD_gain) ), "SetEMCCDGain" )
        except ValueError as exc:
            print exc
            return False
        return True
        
    def _bin_size_changed( self ):
        self.set_image_and_binning()
        
    def set_image_and_binning( self ):
        if self.acquiring: 
            return False
            
        he = self._handle_error
        try:
            width, height = c_int(0), c_int(0)
            he( self.atmcd.GetDetector( byref(width), byref(height) ), "GetDetector" )
            
            bin = self.bin_size
            width, height = c_int( (width.value / bin)*bin ), c_int( (height.value / bin)*bin )
            he( self.atmcd.SetImage( c_long(bin), c_long(bin), c_long(1), width, c_long(1), height ), "SetImage" )
            
            self.width, self.height = width.value / bin, height.value / bin
            print width.value, height.value, self.width, self.height
            #self.image = numpy.zeros( (self.height, self.width), numpy.uint16 )
            self.image = (c_uint16 * (self.height*self.width) )()
        except ValueError as exc:
            print exc
            return False
        return True
        
    def _acquire( self, callback ):
        he = self._handle_error
        
        try:
            self.acquiring = True
            self.event = win32event.CreateEvent( None, 0, 0, None )
            
            he( self.atmcd.StartAcquisition(), "StartAcquisition" )
            he( self.atmcd.SetDriverEvent( self.event.handle ), "SetDriverEvent" )
            
            npixels = self.width*self.height
            #image = self.image.ctypes.data_as( POINTER(c_uint16) )
            while self.acquiring:
                win32event.WaitForSingleObject( self.event, 1000 )
                he( self.atmcd.GetMostRecentImage16( self.image, c_long(npixels) ), "GetMostRecentImage16" )
                if callback:    callback( self.image )
                
            he( self.atmcd.AbortAcquisition(), "AbortAcquisition" )
            
        except ValueError as exc:
            self.acquiring = False
            print exc
            
        finally:
            self.atmcd.SetDriverEvent( None )
            self.event.Close()
            self.event = None
            
    def start_acquiring( self, callback = None ):
        if self.acquiring or self.event:
            return
        self._handle_error( self.atmcd.SetAcquisitionMode( self.AC_ACQMODE_RUNTILABORT ), "SetAcquisitionMode" )
        self.thread = Thread(target=self._acquire, args=(callback,))
        self.thread.start()
            
    def stop_acquiring( self, join = False ):
        self.acquiring = False
        if join:
            self.thread.join()

    def get_image( self ):
        he = self._handle_error
        he( self.atmcd.SetAcquisitionMode( self.AC_ACQMODE_SINGLESCAN ), "SetAcquisitionMode" )
        he( self.atmcd.StartAcquisition(), "StartAcquisition" )
        he( self.atmcd.WaitForAcquisition(), "WaitForAcquisition" )

        npixels = self.width*self.height
        he( self.atmcd.GetMostRecentImage16( self.image, c_long(npixels) ), "GetMostRecentImage16" )
        return self.image

    def save_image( self, filename ):
        he = self._handle_error
        he( self.atmcd.SetAcquisitionMode( self.AC_ACQMODE_SINGLESCAN ), "SetAcquisitionMode" )
        he( self.atmcd.StartAcquisition(), "StartAcquisition" )
        he( self.atmcd.WaitForAcquisition(), "WaitForAcquisition" )
        he( self.atmcd.SaveAsFITS( c_char_p(filename), c_int(0) ), "SaveAsFITS" )
        
    def shutdown( self ):
        he = self._handle_error
        try:                
            print "Shutting down Andor."
            he( self.atmcd.FreeInternalMemory(), "FreeInternalMemory" )
            he( self.atmcd.ShutDown(), "ShutDown" )
            
        except ValueError as exc:
            print "Error shutting down"
            print exc
        
    def _handle_error( self, err_code, fn_name = "<unknown function>" ):
        if err_code != 20002:
            msg = "Error in Andor SDK: {0} returned {1}".format( fn_name, err_code )
            raise ValueError( msg )
            
if __name__ == "__main__":
    luca = Luca()
    luca.save_image( "test.fits" )
    
    
    luca.shutdown()
    
    
