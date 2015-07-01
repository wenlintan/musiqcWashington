#!/usr/bin/env python
"""
show how to add a matplotlib FigureCanvasGTK or FigureCanvasGTKAgg widget to a
gtk.Window
"""

import gtk

from matplotlib.figure import Figure
from matplotlib import pyplot, cm

from numpy import arange, sin, pi
import numpy as np

# uncomment to select /GTK/GTKAgg/GTKCairo
#from matplotlib.backends.backend_gtk import FigureCanvasGTK as FigureCanvas
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas
#from matplotlib.backends.backend_gtkcairo import FigureCanvasGTKCairo as FigureCanvas


win = gtk.Window()
win.connect("destroy", lambda x: gtk.main_quit())
win.set_default_size(400,300)
win.set_title("Embedding in GTK")

bent_z = np.genfromtxt( 'bent_z.csv', dtype=None, delimiter=',' )
groundzs, needlezs, pseudozs, xs, ys, zs = bent_z[1:,0], bent_z[1:,1], bent_z[1:,2], bent_z[1:,4], bent_z[1:,5], bent_z[1:,6]

#bent_z = np.genfromtxt( 'straight_z.csv', dtype=None, delimiter=',' )
#groundzs, needlezs, pseudozs, xs, ys, zs = bent_z[1:,3], bent_z[1:,0], bent_z[1:,1], bent_z[1:,4], bent_z[1:,5], bent_z[1:,6]


size = 256
sscale = 255.
pseudoz = np.zeros((size, size))
for p, y, z in zip( pseudozs, ys, xs ):
	pseudoz[ int( (float(y) + 1.) / 2. * sscale ), int( (float(z) + 1.) / 2. * sscale ) ] = 1.2e-8 * (1. / .8e-3)**2 * float(p)
		
needlez = np.zeros((size, size))
for n, y, z in zip( needlezs, ys, xs ):
	needlez[ int( (float(y) + 1.) / 2. * sscale ), int( (float(z) + 1.) / 2. * sscale ) ] = float(n)

groundz = np.zeros((size, size))
for g, y, z in zip( groundzs, ys, xs ):
	groundz[ int( (float(y) + 1.) / 2. * sscale ), int( (float(z) + 1.) / 2. * sscale ) ] = float(g)

bent_x = np.genfromtxt( 'bent_x.csv', dtype=None, delimiter=',' )
groundxs, needlexs, pseudoxs, xs, ys, zs = bent_x[1:,0], bent_x[1:,1], bent_x[1:,2], bent_x[1:,4], bent_x[1:,5], bent_x[1:,6]

#bent_x = np.genfromtxt( 'straight_x.csv', dtype=None, delimiter=',' )
#groundxs, needlexs, pseudoxs, xs, ys, zs = bent_x[1:,3], bent_x[1:,0], bent_x[1:,1], bent_x[1:,4], bent_x[1:,5], bent_x[1:,6]

pseudox = np.zeros((size, size))
for p, y, z in zip( pseudoxs, ys, zs ):
	pseudox[ int( (float(y) + 1.) / 2. * sscale ), int( (float(z) + 1.) / 2. * sscale ) ] = 1.2e-8 * (1. / .8e-3)**2 * float(p)
		
needlex = np.zeros((size, size))
for n, y, z in zip( needlexs, ys, zs ):
	needlex[ int( (float(y) + 1.) / 2. * sscale ), int( (float(z) + 1.) / 2. * sscale ) ] = float(n)

groundx = np.zeros((size, size))
for g, y, z in zip( groundxs, ys, zs ):
	groundx[ int( (float(y) + 1.) / 2. * sscale ), int( (float(z) + 1.) / 2. * sscale ) ] = float(g)

f = Figure(figsize=(5,4), dpi=100)
canvas = FigureCanvas(f)  # a gtk.DrawingArea

hbox = gtk.HBox()
hbox.set_spacing( 10 )
hbox.pack_start( canvas, expand=True, fill=True )

needle_slider = gtk.VScale()
needle_slider.set_range( -50., 50. )
needle_slider.set_inverted( True )
needle_slider.set_update_policy( gtk.UPDATE_CONTINUOUS )
hbox.pack_end( needle_slider, expand=False )

ground_slider = gtk.VScale()
ground_slider.set_range( -50., 50. )
ground_slider.set_inverted( True )
ground_slider.set_update_policy( gtk.UPDATE_CONTINUOUS )
hbox.pack_end( ground_slider, expand=False )

rf_slider = gtk.VScale()
rf_slider.set_range( 0., 100. )
rf_slider.set_inverted( True )
rf_slider.set_update_policy( gtk.UPDATE_CONTINUOUS )
hbox.pack_end( rf_slider, expand=False )

def update_plot():
	rf_scale = rf_slider.get_value()
	n_scale = needle_slider.get_value()
	g_scale = ground_slider.get_value()
			
	f.clear()

	a = f.add_subplot(211)
	cmap = cm.get_cmap('spectral', 100)
	im = rf_scale**2*pseudoz + n_scale*needlez + g_scale*groundz
	implot = a.imshow( im, interpolation='nearest', cmap=cmap )
	f.colorbar(implot)
	
	m = np.mean( im )
	s = np.std( im )

	implot.set_clim(m-s, m+s)

	a = f.add_subplot(212)
	cmap = cm.get_cmap('spectral', 100)
	im = rf_scale**2*pseudox + n_scale*needlex + g_scale*groundx
	implot = a.imshow( im, interpolation='nearest', cmap=cmap )
	f.colorbar(implot)
	
	m = np.mean( im )
	s = np.std( im )

	implot.set_clim(0., m+0.1*s)
	canvas.draw()
	
needle_slider.connect( 'value-changed', lambda x: update_plot() )
needle_slider.set_value( 1. )

ground_slider.connect( 'value-changed', lambda x: update_plot() )
ground_slider.set_value( 0. )

rf_slider.connect( 'value-changed', lambda x: update_plot() )
rf_slider.set_value( 10. )

win.add( hbox )

win.show_all()
gtk.main()
