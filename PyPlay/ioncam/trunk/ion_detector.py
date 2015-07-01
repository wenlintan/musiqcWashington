
from analysis import IonDetector as CIonDetector
from analysis import IonData

from ctypes import *
from threading import Thread

from enthought.traits.api import Float, String, HasTraits
from enthought.traits.ui.api import View, Item, Group
    
class IonDetector( HasTraits ):
    
    canny_threshold = Float( 4.0, label="Edge Base Threshold" )
    canny_continue_threshold = Float( 1.0, label="Edge Continue Threshold" )
    hough_threshold = Float( 4.0, label="Ion Shape Threshold" )
    blob_threshold = Float( 10.0, label="Ion Blob Threshold" )
    results = String("", label="Detected Ions")
    
    view = View(    Group(  Item('canny_threshold'),
                            Item('canny_continue_threshold'),
                            Item('hough_threshold'),
                            Item('blob_threshold'),
                            Item('results', style='custom'),
                            label = "Detection Settings",
                            show_border = True
                         )
                )
    
    def __init__( self ):
        super( IonDetector, self ).__init__()
        self.detector = CIonDetector()
        self.thread = None
        
    _canny_threshold_changed = lambda self: self._update()
    _canny_continue_threshold_changed = lambda self: self._update()
    _hough_threshold_changed = lambda self: self._update()
    _blob_threshold_changed = lambda self: self._update()
        
    def start_analyzing( self, data, callback = None ):
        if self.thread and self.thread.isAlive():
            return
            
        self.thread = Thread( target=self._analyze, args=(data, callback) )
        self.thread.start()
        
    def _analyze( self, numpy_data, callback ):
        ions = self.detector( numpy_data )  
      
        self.results = ""
        for ion in ions:
            self.results += "Ion at {0}, {1}\n".format( ion.x, ion.y )
            
        if callback:
            callback( ions )
        
    def _update( self ):
        self.detector.canny_threshold = self.canny_threshold
        self.detector.canny_continue_threshold = self.canny_continue_threshold
        self.detector.hough_threshold = self.hough_threshold
        self.detector.blob_threshold = self.blob_threshold
        
        
        
    
        
  