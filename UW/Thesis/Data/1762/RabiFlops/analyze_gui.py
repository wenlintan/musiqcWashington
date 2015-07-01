#!/usr/bin/env python

import numpy as np 
from scipy.optimize import curve_fit

import Tkinter as tk
from tkFileDialog import askopenfilename, asksaveasfilename
import ttk

import matplotlib.figure as mplfig
import matplotlib.backends.backend_tkagg as tkagg

from analyze import IonDetector, Shelves, Configurations

class App:
    def __init__( self ):
        self.master = tk.Tk()

        self.button_frame = tk.Frame( self.master )
        self.button_frame.pack( side=tk.TOP, fill=tk.X, expand=0 )

        self.open_button = tk.Button( self.button_frame, 
            text='OPEN', command=self.load_data_file )
        self.save_button = tk.Button( self.button_frame, 
            text='SAVEFIG', command=self.save_figure )

        for b in (self.open_button, self.save_button):
            b.pack( side=tk.LEFT )

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
        self.ds_nions = tk.Label( self.ds_fileinfo, 
            anchor=tk.W, justify=tk.LEFT, text='NIons: ' )
        self.ds_ndark = tk.Label( self.ds_fileinfo, 
            anchor=tk.W, justify=tk.LEFT, text='NDark: ' )
        self.ds_filename.pack( side=tk.TOP, fill=tk.X )
        self.ds_nions.pack( side=tk.TOP, fill=tk.X )
        self.ds_ndark.pack( side=tk.TOP, fill=tk.X )
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
            command=self.plot_rabi )
        self.sh_plot.pack( side=tk.TOP )

        self.notebook.add( self.shelves, text='Shelving' )

        self.figure = mplfig.Figure( figsize=(6.5, 6.5) )
        self.axes = self.figure.add_axes( [0.1, 0.1, 0.8, 0.8] )
        self.canvas = tkagg.FigureCanvasTkAgg( self.figure,
            master = self.main_window )
        self.canvas.get_tk_widget().pack( side=tk.LEFT,
            fill=tk.BOTH, expand=1 )

        tk.mainloop()

    def process_data_file( self ):
        order = None
        if self.ds_conf_enable_var.get():
            order = self.ds_conf.get()
            order = [ bool(x) for x in map( int, order ) ]
        detector = IonDetector( order=order, sym=self.ds_symmetry_var.get() )
        self.times, self.before, self.after = detector.detect(self.data)
        self.nions, self.nbright = len(self.before[0]), sum(self.before[0])
        self.ndark = self.nions - self.nbright

    def load_data_file( self ):
        filename = askopenfilename()
        if not filename:
            return

        self.data = np.loadtxt( filename )
        self.process_data_file()

        filename = '...' + filename[-15:]
        self.ds_filename.config( text='File: {}'.format(filename) )
        self.ds_nions.config( text='NIons: {}'.format(self.nions) )
        self.ds_ndark.config( text='NDark: {}'.format(self.ndark) )
        self.ds_conf.config( width=self.nions )

    def plot_rabi( self ):
        self.axes.clear()
        self.process_data_file()
        shelves = Shelves().run( self.times, self.before, self.after )

        def theory( t, s, n, w ):
            eta = 0.015
            comps = [ 1 / (n+1) * (n / (n+1))**i * np.cos(
                2*w*(1-eta**2*i)*t ) for i in range( max(int(n)*5, 200) ) ]
            return s * (1 - sum( comps ))

        times = np.array([s[0] for s in shelves])
        densetimes = np.arange( 0., times[-1], 0.5 )
        colors = ['r', 'g', 'b', 'c', 'y', 'm', 'k']
        for i in range( len(shelves[0][1]) ):
            data = np.array([s[1][i] for s in shelves])
            params, _ = curve_fit( theory, times, data, [0.45, 200., 0.12] )
            print( params )
            self.axes.plot( times, [s[1][i] for s in shelves], 
                colors[i]+'+', markersize=15. )
            self.axes.plot( densetimes, theory( densetimes, *params ),
                colors[i])


        self.axes.set_ylim( 0, 1 )
        self.canvas.draw()

    def save_figure( self ):
        filename = asksaveasfilename()
        if filename:
            self.figure.savefig( filename )



if __name__ == "__main__":
    App()
