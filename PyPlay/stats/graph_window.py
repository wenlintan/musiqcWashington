
import pygtk
pygtk.require('2.0')
import gtk

import variable, math
from util_window import *

class window:

    def __init__( self, x, y ):

        if x.functional and not x.evaluated:
            print "X Variable '%s' not evaluated." % x.name
            raise ValueError

        if y.functional and not y.evaluated:
            print "Y Variable '%s' not evaluated." % y.name
            raise ValueError
        
        self.x = x.eval_var
        self.y = y.eval_var
        
        if self.x.type != variable.ARRAY or self.y.type != variable.ARRAY:
            print "Can only graph arrays ... interestingly at least."
            raise ValueError

        self.xdata = x.eval_data
        self.ydata = y.eval_data

        if len( self.xdata ) != len( self.ydata ):
            print "Must have same number of graph coords."
            raise ValueError
        self.datalen = len( self.xdata )

        self.xdata = [ x_i.data for x_i in self.xdata ]
        self.ydata = [ y_i.data for y_i in self.ydata ]

        xmag, ymag = 1., 1.
        while xmag > min( self.xdata ):     xmag /= 10
        while xmag < max( self.xdata ):     xmag *= 10

        while ymag > min( self.ydata ):     ymag /= 10
        while ymag < max( self.ydata ):     ymag *= 10
        xmag, ymag = xmag / 10., ymag / 10.

        self.xdata = [ xi1/xmag for xi1 in self.xdata ]
        self.ydata = [ yi1/ymag for yi1 in self.ydata ]

        try:
            self.yerrs = y.sub_vars["err"]
            if self.yerrs.type != variable.ARRAY:
                self.yerr_data = [self.yerrs.eval_data for i in range(self.datalen)]
            else:
                self.yerr_data = [ y_i.data for y_i in self.yerrs.data ]

            self.yerr_data = [ yi1/ymag for yi1 in self.yerr_data ]
            self.y_errors_on = self.y_errors_avail = True

        except KeyError:
            self.y_errors_on = self.y_errors_avail = False
        self.linear_fit_on = False
        self.worst_case_lf_on = False
        
        self.x_span = max( self.xdata ) - min( self.xdata )
        self.y_span = max( self.ydata ) - min( self.ydata )

        self.x_range = [ min( self.xdata ) - self.x_span*.15,
                         max( self.xdata ) + self.x_span*.15 ]
        self.y_range = [ min( self.ydata ) - self.y_span*.15,
                         max( self.ydata ) + self.y_span*.15 ]

        self.x_span = self.x_range[1] - self.x_range[0]
        self.y_span = self.y_range[1] - self.y_range[0]
        
        self.window = gtk.Window( gtk.WINDOW_TOPLEVEL )
        self.window.set_title( "Graph '%s' vs '%s'" % (x.name, y.name) )
        self.window.set_size_request( 512, 512 )

        self.destroyed = False
        self.window.connect("delete_event", self.delete_event)

        self.draw = gtk.DrawingArea()
        self.draw.set_size_request(400, 400)
        
        self.hruler = gtk.HRuler()
        self.hruler.set_range( self.x_range[0], self.x_range[1],
                               self.x_range[0], self.x_range[1])
        
        self.vruler = gtk.VRuler()
        self.vruler.set_range( self.y_range[1], self.y_range[0],
                               self.y_range[0], self.y_range[1])

        self.title = gtk.Label( "Title" )
        self.xaxis = gtk.Label( "X-Axis" )
        self.yaxis = gtk.Label( "Y-Axis" )
        self.yaxis.set_property( "angle", 90 )
        
        self.table = gtk.Table(3,3)
        self.table.attach(self.title, 2, 3, 0, 1, yoptions=0)
        self.table.attach(self.yaxis, 0, 1, 1, 2, xoptions=0)
        self.table.attach(self.xaxis, 2, 3, 3, 4, yoptions=0)

        self.table.attach(self.draw, 2, 3, 1, 2)
        self.table.attach(self.hruler, 2, 3, 2, 3, yoptions=0)
        self.table.attach(self.vruler, 1, 2, 1, 2, xoptions=0)
        

        self.main_vert = gtk.VBox()
        self.menu_hort = gtk.HBox()

        self.graph_desc_button = gtk.Button( "Set Graph Labels" )
        self.graph_desc_button.connect( "clicked", create_graph_desc_dialog, self )
        self.menu_hort.pack_start( self.graph_desc_button, False )

        self.linear_fit_button = gtk.Button( "Toggle Linear Fit" )
        self.linear_fit_button.connect( "clicked", self.toggle_linear_fit, None )
        self.menu_hort.pack_start( self.linear_fit_button, False )

        self.worst_case_lf_button = gtk.Button( "Toggle Worst Case LF" )
        self.worst_case_lf_button.connect( "clicked", self.toggle_worst_case_lf, None )
        self.menu_hort.pack_start( self.worst_case_lf_button, False )

        self.y_errors_button = gtk.Button( "Toggle Y Errors" )
        self.y_errors_button.connect( "clicked", self.toggle_y_errors, None )
        self.menu_hort.pack_start( self.y_errors_button, False )
        
        self.main_vert.pack_start( self.table )
        self.main_vert.pack_start( self.menu_hort, False )
        self.window.add(self.main_vert)


        self.draw.connect("expose-event", self.area_expose_callback)
        self.draw.set_events(gtk.gdk.POINTER_MOTION_MASK |
                             gtk.gdk.POINTER_MOTION_HINT_MASK )
        
        def motion_notify(ruler, event):
            return ruler.emit("motion_notify_event", event)
        self.draw.connect_object("motion_notify_event", motion_notify,
                                    self.hruler)
        self.draw.connect_object("motion_notify_event", motion_notify,
                                    self.vruler)

        self.window.show_all()
        
        self.gc = self.draw.window.new_gc( )
        self.color_map = self.gc.get_colormap()

        self.color_names = [ "black", "white", "red" ]
        self.color_obj = [gtk.gdk.color_parse(n) for n in self.color_names]
        self.color_obj = [self.color_map.alloc_color(c) for c in self.color_obj]

        self.colors = {}
        for i, name in enumerate( self.color_names ):
            self.colors[name] = self.color_obj[i]

        self.gc.set_background( self.colors["white"] )
        self.gc.set_foreground( self.colors["black"] )
        

    def set_graph_desc( self, title, xlabel, ylabel ):
        self.title.set_text( title )
        self.xaxis.set_text( xlabel )
        self.yaxis.set_text( ylabel )
        
    def area_expose_callback( self, area, event ):
        self.draw_data()
        
    def draw_data( self ):

        #self.style = self.draw.get_style()
        #self.gc = self.style.fg_gc[ gtk.STATE_NORMAL ]
        #self.gc.set_background( gtk.gdk.color_parse( "white" ) )

        w, h = self.draw.window.get_size()
        self.width, self.height = w, h
        
        self.xscale = xscale = float(w) / self.x_span
        self.yscale = yscale = float(h) / self.y_span

        #draw axes
        self.draw.window.draw_line( self.gc,
            0, h+self.y_range[0]*yscale,
            self.width, h+self.y_range[0]*yscale )
        self.draw.window.draw_line( self.gc,
            -self.x_range[0]*xscale, 0,
            -self.x_range[0]*xscale, self.height )
        
        for i in range( self.datalen ):
            
            x = ( self.xdata[i] - self.x_range[0] ) * xscale
            y = ( self.ydata[i] - self.y_range[0] ) * yscale
            y = h - y
            
            self.draw.window.draw_arc( self.gc, False, x-2, y-2, 5, 5, 0, 64*360 )
            self.draw.window.draw_point( self.gc, x, y )

        self.draw_linear_fit()
        self.draw_worst_case_lf()
        self.draw_y_errors()

    def toggle_linear_fit( self, widget, data = None ):

        #invalidate window so everything will be redrawn
        self.draw.window.invalidate_rect( None, False )
        
        if self.linear_fit_on:
            self.linear_fit_on = False
            return

        self.linear_fit_on = True
        sumx = sum( self.xdata )
        sumy = sum( self.ydata )
        sumxy = sum( [self.xdata[i]*self.ydata[i] for i in range(self.datalen)] )
        sumxx = sum( [x*x for x in self.xdata] )

        delta = float(self.datalen)*sumxx - float(sumx)*sumx
        self.lg_slope = (self.datalen*sumxy - sumx*sumy) / delta
        self.lg_inter = (sumxx*sumy - sumx*sumxy) / delta
        
        print "LF:", self.lg_slope, self.lg_inter

    def draw_linear_fit( self ):
        
        if not self.linear_fit_on:
            return

        yi = self.lg_inter + self.lg_slope*self.x_range[0]
        yo = self.lg_inter + self.lg_slope*self.x_range[1]
        
        self.draw.window.draw_line( self.gc,
            0, self.height - (yi-self.y_range[0])*self.yscale,
            self.width, self.height - (yo-self.y_range[0])*self.yscale )

    def toggle_y_errors( self, widget, data=None ):

        #invalidate window so everything will be redrawn
        self.draw.window.invalidate_rect( None, False )
        
        if self.y_errors_on:
            self.y_errors_on = False
            return

        self.y_errors_on = self.y_errors_avail

    def draw_y_errors( self ):

        if not self.y_errors_on:
            return

        for i in range( self.datalen ):

            x = ( self.xdata[i] - self.x_range[0] ) * self.xscale
            ytop = ( self.ydata[i] + self.yerr_data[i] - self.y_range[0] )
            ybot = ( self.ydata[i] - self.yerr_data[i] - self.y_range[0] )
            ytop = self.height - ytop*self.yscale
            ybot = self.height - ybot*self.yscale

            self.draw.window.draw_line( self.gc, x, ybot, x, ytop )
            self.draw.window.draw_line( self.gc, x-2, ytop, x+2, ytop )
            self.draw.window.draw_line( self.gc, x-2, ybot, x+2, ybot )

    def toggle_worst_case_lf( self, widget, data = None ):

        #invalidate window so everything will be redrawn
        self.draw.window.invalidate_rect( None, False )
        
        if self.worst_case_lf_on:
            self.worst_case_lf_on = False
            return

        if not self.linear_fit_on:
            return

        xdata = self.xdata
        
        self.worst_case_lf_on = True
        estimates = [ self.lg_inter + self.lg_slope*x for x in self.xdata ]
        residuals = [ estimates[i] - self.ydata[i] for i in range(len(xdata)) ]

        sse = sum( [ r*r for r in residuals ] )
        sig_e = math.sqrt( sse / ( len(self.xdata) -2 ) )

        xmean = sum( xdata ) / len( xdata )
        sum_mean = sum( [(x - xmean)**2 for x in xdata] )

        sig_inter = sig_e*math.sqrt( 1 / len(xdata) + xmean**2 / sum_mean )
        sig_slope = sig_e*math.sqrt( 1 / sum_mean )                

        print "Intercept Sigma:", sig_inter
        print "Slope Sigma:", sig_slope
        
        self.worst_lg = [(self.lg_slope + sig_slope, self.lg_inter - sig_inter),
                         (self.lg_slope - sig_slope, self.lg_inter + sig_inter)]
        print "Worst case:", self.worst_lg

    def draw_worst_case_lf( self ):

        if not self.worst_case_lf_on:
            return

        c = self.colors["red"]
        print c.red, c.green, c.blue, c.pixel
        self.gc.set_foreground( self.colors[ "red" ] )
        for slope, inter in self.worst_lg:
            
            yi = inter + slope*self.x_range[0]
            yo = inter + slope*self.x_range[1]
            
            self.draw.window.draw_line( self.gc,
                0, self.height - (yi-self.y_range[0])*self.yscale,
                self.width, self.height - (yo-self.y_range[0])*self.yscale )

        self.gc.set_foreground( gtk.gdk.color_parse( "black" ) )
                

    def delete_event( self, widget, event, data = None ):
        self.window.destroy()
        self.destroyed = True
