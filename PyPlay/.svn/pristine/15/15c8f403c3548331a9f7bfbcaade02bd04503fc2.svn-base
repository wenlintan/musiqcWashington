#!/usr/bin/env python

import numpy as np 
from scipy.optimize import curve_fit

try:
    import Tkinter as tk
    from tkFileDialog import askopenfilename, asksaveasfilename
    import ttk
except ImportError:
    # Python 3 renaming things
    import tkinter as tk
    from tkinter.filedialog import askopenfilename, asksaveasfilename
    import tkinter.ttk as ttk

import matplotlib.mlab as mlab
import matplotlib.figure as mplfig
import matplotlib.backends.backend_tkagg as tkagg

class App:
    def __init__( self ):
        self.phonemes = []
        self.mus = []
        self.sigmas = []

        self.master = tk.Tk()

        self.button_frame = tk.Frame( self.master )
        self.button_frame.pack( side=tk.TOP, fill=tk.X, expand=0 )

        self.open_button = tk.Button( self.button_frame, 
            text='OPEN', command=self.load_data_file )
        self.save_button = tk.Button( self.button_frame, 
            text='SAVEFIG', command=self.save_figure )

        for button in (self.open_button, self.save_button):
            button.pack( side=tk.LEFT )

        self.main_window = tk.Frame( self.master )
        self.main_window.pack( side=tk.BOTTOM, fill=tk.BOTH, expand=1 )

        self.notebook = ttk.Notebook( self.main_window )
        self.notebook.pack( side=tk.RIGHT, fill=tk.Y, expand=0  )

        self.data_select = tk.Frame( self.notebook )

        tk.Label( self.data_select, anchor=tk.W, 
            text="File Info:" ).pack( fill=tk.X )
        self.ds_fileinfo = tk.Frame( self.data_select,
            border=2, relief=tk.SUNKEN )
        self.ds_filename = tk.Label( self.ds_fileinfo, 
            anchor=tk.W, justify=tk.LEFT, text='File: ' )
        self.ds_nphonemes = tk.Label( self.ds_fileinfo, 
            anchor=tk.W, justify=tk.LEFT, text='NPhonemes: ' )
        self.ds_filename.pack( side=tk.TOP, fill=tk.X )
        self.ds_nphonemes.pack( side=tk.TOP, fill=tk.X )
        self.ds_fileinfo.pack( fill=tk.X, padx=5, pady=5 )

        def build_entry( master, name, width ):
            frame = tk.Frame( master )
            tk.Label( frame, text=name, anchor=tk.W ).pack( side=tk.LEFT )
            entry = tk.Entry( frame, width=width )
            entry.pack( side=tk.LEFT )
            return frame, entry

        tk.Label( self.data_select, anchor=tk.W, 
            text="Configuration:" ).pack( fill=tk.X )
        self.ds_configuration = tk.Frame( self.data_select,
            border=2, relief=tk.SUNKEN )
        self.ds_conf_enable_var = tk.IntVar()
        self.ds_conf_enable = tk.Checkbutton( self.ds_configuration,
            anchor=tk.W, text="Filter Configurations", 
            variable=self.ds_conf_enable_var )
        eframe, self.ds_conf = build_entry( self.ds_configuration, 
            "Configuration:", 10 )
        self.ds_symmetry_var = tk.IntVar()
        self.ds_symmetry = tk.Checkbutton( self.ds_configuration,
            anchor=tk.W, text="Accept Symmetric", 
            variable=self.ds_symmetry_var )
        self.ds_conf_enable.pack( side=tk.TOP, fill=tk.X )
        eframe.pack( side=tk.TOP )
        self.ds_symmetry.pack( side=tk.TOP, fill=tk.X )
        self.ds_configuration.pack( fill=tk.X, padx=5, pady=5 )

        self.notebook.add( self.data_select, text='Data' )

        self.shelves = tk.Frame( self.notebook )

        self.sh_fit = tk.Frame( self.shelves )
        tk.Label( self.sh_fit, anchor=tk.W,
            text="Initial Parameters:" ).pack(
            fill=tk.X )
        frame, self.sh_initial_n = build_entry( self.sh_fit, "N:", 8 )
        frame.pack( fill=tk.X )
        frame, self.sh_initial_w = build_entry( self.sh_fit, "W:", 8 )
        frame.pack( fill=tk.X )
        frame, self.sh_initial_s = build_entry( self.sh_fit, "S:", 8 )
        frame.pack( fill=tk.X )
        self.sh_fit_enable = tk.Checkbutton( self.sh_fit,
            anchor=tk.W, text='Enable Fit' )
        self.sh_fit_enable.pack( side=tk.TOP, fill=tk.X )
        self.sh_fit.pack( fill=tk.X )

        self.sh_plot = tk.Button( self.shelves, text="PLOT",
            command=self.plot_gmms )
        self.sh_plot.pack( side=tk.TOP )

        self.notebook.add( self.shelves, text='Shelving' )

        self.figure = mplfig.Figure( figsize=(6.5, 6.5) )
        self.axes = self.figure.add_axes( [0.1, 0.1, 0.8, 0.8] )
        self.canvas = tkagg.FigureCanvasTkAgg( self.figure,
            master = self.main_window )
        self.canvas.get_tk_widget().pack( side=tk.LEFT,
            fill=tk.BOTH, expand=1 )

        tk.mainloop()

    def load_data_file( self ):
        filename = askopenfilename()
        if not filename:
            return

        with open( filename, 'r' ) as fp:
            data = iter( fp.read().splitlines() )
            try:
                while True:
                    self.phonemes.append( next(data) )
                    count = next(data)
                    self.mus.append( np.array( list(map( 
                        float, next(data).split() ))) )
                    next(data)
                    print(self.mus)

                    sigma = []
                    for i in range(  len(self.mus[-1]) ):
                        sigma.append( list(map( float, next(data).split() )) )
                    self.sigmas.append( np.array(sigma) )
                    next(data)
                    next(data)
            except StopIteration:
                pass

        filename = '...' + filename[-15:]
        self.ds_filename.config( text='File: {}'.format(filename) )
        self.ds_nphonemes.config( text='NPhonemes: {}'.format(
            len(self.phonemes)) )

        self.plot_gmms()

    def plot_gmms( self ):
        self.axes.clear()
        xs = [ mu[0] for mu in self.mus ]
        ys = [ mu[1] for mu in self.mus ]
        sigxxs = [ np.sqrt(sigma[0][0]) for sigma in self.sigmas ]
        sigyys = [ np.sqrt(sigma[1][1]) for sigma in self.sigmas ]
        sigxys = [ sigma[0][1] for sigma in self.sigmas ]

        xmin = min( x-2*sxx for x, sxx in zip( xs, sigxxs ) )
        xmax = max( x+2*sxx for x, sxx in zip( xs, sigxxs ) )
        ymin = min( y-2*syy for y, syy in zip( ys, sigyys ) )
        ymax = max( y+2*syy for y, syy in zip( ys, sigyys ) )

        xr = np.linspace( xmin, xmax, 100 )
        yr = np.linspace( ymin, ymax, 100 )
        X, Y = np.meshgrid( xr, yr )
        for x, y, sxx, syy, sxy in zip( xs[:10], ys, sigxxs, sigyys, sigxys ):
            Z = mlab.bivariate_normal( X, Y, sxx, syy, x, y, sxy )
            self.axes.contour( X, Y, Z, 2 )

        self.axes.set_xlim( xmin, xmax )
        self.axes.set_ylim( ymin, ymax )
        self.canvas.draw()

    def save_figure( self ):
        filename = asksaveasfilename()
        if filename:
            self.figure.savefig( filename )



if __name__ == "__main__":
    App()
