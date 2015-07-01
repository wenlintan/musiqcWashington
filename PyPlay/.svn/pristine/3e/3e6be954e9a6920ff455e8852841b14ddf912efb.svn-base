#From: http://code.enthought.com/projects/traits/docs/html/tutorials/traits_ui_scientific_app.html
from enthought.traits.api import HasTraits, Instance, String, Button, Float, Range
from enthought.traits.ui.api import View, Item, Group, HSplit, Handler
from enthought.traits.ui.menu import NoButtons

from enthought.chaco.api import *
from enthought.chaco.tools.api import *
from enthought.enable.component_editor import ComponentEditor
import numpy

from threading import Thread, Lock
from luca import Luca
from ion_detector import IonDetector
from compensator import Compensator

class ImagePlot(HasTraits):
    plot = Instance(Plot)
    image_container = Instance(HPlotContainer)
    container = Instance(VPlotContainer)
    
    traits_view = View(
        Item('container', editor=ComponentEditor(), show_label=False),
        width=500, 
        height=500, 
        resizable=True)

    def __init__(self):
        super(ImagePlot, self).__init__()
        
        z = numpy.zeros( (256, 256) )
        self.plotdata = ArrayPlotData(imagedata = z)
        
        plot = Plot(self.plotdata)
        self.renderer = plot.img_plot("imagedata", 
            colormap=jet)[0]
        
        plot.tools.append(PanTool(plot, restrict_to_data=True)) 
        plot.tools.append(ZoomTool(plot, drag_button='right'))
        
        plot.x_grid.visible = True 
        plot.x_grid.line_color = (0, 0, 0) 
        plot.y_grid.visible = True 
        plot.y_grid.line_color = (0, 0, 0) 
        
        plot.padding = 50
        self.plot = plot 
        
        colormap = plot.color_mapper
        colorbar = ColorBar( 
            index_mapper=LinearMapper(range=colormap.range), 
            color_mapper=colormap, 
            orientation='v', 
            resizable='v', 
            width=30) 
            
        colorbar.plot = plot 
        colorbar.padding_top = plot.padding_top 
        colorbar.padding_bottom = plot.padding_bottom

        container = HPlotContainer( plot, colorbar, fill_padding = True ) 
        self.image_container = container 
        
        self.bins = numpy.linspace( -500, 2000, 500 )
        hist, bins = numpy.histogram( z, bins=self.bins )
        self.histdata = ArrayPlotData( hist=hist, bins=bins )
        
        plot = Plot( self.histdata )
        renderer = plot.plot( ("bins", "hist"), 
            render_style='connectedhold')[0]
        
        renderer.active_tool = RangeSelection( renderer, left_button_selects=True )
        renderer.overlays.append( RangeSelectionOverlay( component=renderer ) )
        renderer.active_tool.on_trait_change(self._range_selection_handler, "selection")
        
        plot.height = 50
        plot.resizable = 'h'
        plot.padding_top = 0
        self.histogram = plot
        
        container = VPlotContainer( self.histogram, self.image_container, spacing=0 )
        self.container = container
        
    def _range_selection_handler(self, event):
        if event is not None:
            low, high = event
            self.renderer.value_range.low = low
            self.renderer.value_range.high = high
            
            range = self.bins[-1] - self.bins[0]
            if low < self.bins[0] + range*0.1:
                self.bins = numpy.linspace( int(self.bins[0] - range * 0.5), self.bins[-1], 500 )
            if high > self.bins[-1] - range*0.1:
                self.bins = numpy.linspace( self.bins[0], int(self.bins[-1] + range * 0.5), 500 )
            if high - low < range * 0.3:
                if low > self.bins[0] + range*0.4:
                    self.bins = numpy.linspace( int(self.bins[0] + range*0.3), self.bins[-1], 500 )
                if high < self.bins[-1] - range*0.4:
                    self.bins = numpy.linspace( self.bins[0], int(self.bins[-1] - range*0.3), 500 )
        else:
            self.renderer.value_range.set_bounds("auto", "auto")
        
    def plot_image( self, image ):
        self.plotdata.set_data( "imagedata", image )
        
        hist, bins = numpy.histogram( image, bins=self.bins )
        self.histdata.set_data( "hist", hist )
        self.histdata.set_data( "bins", bins )
        
        x, y = range( 0, image.shape[0] ), range( 0, image.shape[1] )
        self.renderer.index.set_data( x, y, sort_order=('ascending', 'ascending') )
        
        self.plot.request_redraw()
        self.histogram.request_redraw()

class ControlPanel(HasTraits):
    """ This object is the core of the traitsUI interface. Its view is
    the right panel of the application, and it hosts the method for
    interaction between the objects and the GUI.
    """
    camera = Instance(Luca, ())
    ion_detector = Instance(IonDetector, ())
    compensator = Instance(Compensator, ())
    
    start_stop_acquisition = Button("Start/Stop acquisition")
    take_background = Button("Take background")
    
    view = View( 
                Group(  Item('start_stop_acquisition', show_label=False ),
                        Item('take_background', show_label=False ),
                        Item('camera', style='custom', show_label=False )
                     ),
                Item('ion_detector', style='custom', show_label=False),
                Item('compensator', style='custom', show_label=False)
                )

    def _start_stop_acquisition_fired(self):
        """ Callback of the "start stop acquisition" button. This starts
        the acquisition thread, or kills it.
        """
        if self.camera.acquiring:
            self.camera.stop_acquiring()
        else:
            self.camera.start_acquiring( self.got_image )
            self.background_next_image = False
            
    def _take_background_fired( self ):
        if not self.camera.acquiring:
            self.camera.start_acquiring( self.got_background )
            self.background_started_acquisition = True
        else:
            self.background_started_acquisition = False
            self.background_next_image = True
            
    def got_background( self, image ):
        image = image.astype('f')
        if self.background_started_acquisition:
            self.camera.stop_acquiring()
        self.background_next_image = False
        self.background = image.copy()
        self.figure.plot_image( image )

    def got_image(self, image):
        """ Plots an image on the canvas in a thread safe way.
        """
        image = image.astype('f')
        if self.background_next_image:
            self.got_background( image )
            return
            
        if self.background is not None and self.background.shape == image.shape:
            image -= self.background
        self.figure.plot_image( image )
        self.ion_detector.start_analyzing( image, self.compensator.update_ions )
        self.compensator.update_frame( image )

class MainWindowHandler(Handler):
    def close(self, info, is_OK):
        camera = info.object.panel.camera
        if camera.acquiring:
            camera.stop_acquiring( True )
        camera.shutdown()
        return True

class MainWindow(HasTraits):
    """ The main window, here go the instructions to create and destroy the application. """
    figure = Instance(ImagePlot, ())
    panel = Instance(ControlPanel)

    def _panel_default(self):
        return ControlPanel(figure=self.figure, background=None)

    view = View(HSplit(Item('figure', style="custom", dock='vertical'),
                       Item('panel', style="custom"),
                       show_labels=False,
                      ),
                title="Luca Control",
                resizable=True,
                height=0.75, width=0.75,
                handler=MainWindowHandler(),
                buttons=NoButtons)

if __name__ == '__main__':
    MainWindow().configure_traits()
    
