#!/usr/bin/env python
"""Provide GUI for frequency scan and Rabi flop experiments."""

from time import sleep

import Tkinter as tk
from multiprocessing import Process, Pipe

import numpy as np

import matplotlib.figure as mplfig
import matplotlib.backends.backend_tkagg as tkagg

import argparse



class App:
    "Provide GUI for frequency scan and Rabi Flop experiments."
    def __init__( self, conn ):
        self.master = tk.Tk()
        self.conn = conn

        self.background = []
        self.occurences, self.shelves = {}, {}
        self.before = [0]*3
        self.after = [0]*3

        self.bright_fig = mplfig.Figure( figsize=(2.5, 6.5) )
        self.before_axes = self.bright_fig.add_axes( [0.1, 0.55, 0.8, 0.4] )
        self.after_axes = self.bright_fig.add_axes( [0.1, 0.05, 0.8, 0.4] )
        self.bright_canvas = tkagg.FigureCanvasTkAgg(
            self.bright_fig, master=self.master )
        self.bright_canvas.get_tk_widget().pack( side=tk.LEFT,
            fill=tk.Y, expand=1 )
        self.before_axes.get_xaxis().set_visible(False)
        self.before_axes.get_yaxis().set_visible(False)
        self.after_axes.get_xaxis().set_visible(False)
        self.after_axes.get_yaxis().set_visible(False)

        self.data_fig = mplfig.Figure( figsize=(6.5, 6.5) )
        self.data_axes = self.data_fig.add_axes( [0.1, 0.1, 0.8, 0.8] )
        self.data_canvas = tkagg.FigureCanvasTkAgg( 
            self.data_fig, master=self.master )
        self.data_canvas.get_tk_widget().pack( side=tk.LEFT,
            fill=tk.BOTH, expand=1 )
        self.data_axes.grid( True )

        self.plot()

        self.tick()
        self.master.mainloop()

    def tick( self ):
        "Check for new data from interprocess conn."
        if self.conn.poll():
            new_data = self.conn.recv().split()
            reor_data_flag = False
            if new_data[0] == 'reordata':
                reor_data_flag = True
                new_data = new_data[1:]
            time = float( new_data[0] )
            nions = (len( new_data ) - 3) / 2
            self.background.append( float(new_data[ nions+1 ]) )
            self.background.append( float(new_data[ nions*2+2 ]) )
            if len(self.background) > 1000:
                self.background = self.background[100:]

            bkg = np.mean( self.background )
            thresh = 3*np.std( self.background )

            self.before = np.array( new_data[1:nions+1], dtype=float )
            self.after = np.array( new_data[nions+2:2*nions+2], dtype=float )

            before_ions = self.before - bkg > thresh
            after_ions = self.after - bkg > thresh

            if not self.occurences.has_key( time ):
                self.occurences[ time ] = [0]*nions
                self.shelves[ time ] = [0]*nions

            if not reor_data_flag:
                for i in range( nions ):
                    if before_ions[i]:
                        self.occurences[time][i] += 1
                    if before_ions[i] and not after_ions[i]:
                        self.shelves[time][i] += 1
            self.plot()
        self.master.after( 500, self.tick )

    def plot( self ):
        "Update data plots from new data."
        self.before_axes.clear()
        self.after_axes.clear()
        self.before_axes.bar( np.arange(len(self.before)), self.before )
        self.after_axes.bar( np.arange(len(self.after)), self.after )
        self.before_axes.set_ylim( 800000, 830000 )
        self.after_axes.set_ylim( 800000, 830000 )
        self.bright_canvas.draw()

        keys = list( sorted(self.occurences.keys()) )
        vals = [[ float(s) / o if o else 0
            for s, o in zip( self.shelves[t], self.occurences[t] )]
            for t in keys ]
        
        colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k']
        self.data_axes.clear()
        if vals:
            for i in range( len(vals[0]) ):
                self.data_axes.plot( keys, [v[i] for v in vals], colors[i] )
        self.data_axes.set_ylim( 0, 1 )
        self.data_canvas.draw()


def experiment( conn, args):
    "Run experiment and route incoming data to conn."
    from freqscan import Experiment, RabiFlop, FreqScan

    ionpos = args.ionpos
    order = [True if x > .5 else False for x in map(int,args.order)]+ [False]
    nions, ndark = len(order), order.count(False)
    nruns = int(args.nruns)
    outdata = args.out

    if args.freqscan:
        highfreq, lowfreq, freqstep, pulse_duration = float(args.freqscan[0]), \
                float(args.freqscan[1]), float(args.freqscan[2]), int(args.freqscan[3])
        freqscan = FreqScan(lowfreq, highfreq, freqstep, pulse_duration )
    if args.rabiflop:
        starttime, stoptime, timestep, frequency = int(args.rabiflop[0]), int(args.rabiflop[1]), \
                int(args.rabiflop[2]), float(args.rabiflop[3])
        rabiflop = RabiFlop(starttime, stoptime, timestep, frequency)

    if args.freqscan: #running low to high in frequency
        Experiment(nruns, freqscan, ionpos, order, outdata, conn )
    elif args.rabiflop:
        Experiment(nruns, rabiflop , ionpos, order, outdata, conn )
    else:
        print("No experiment type specified")

if __name__ == '__main__':

#command line arguments 

    parser = argparse.ArgumentParser(description='Freq Scan Prgrm')
    parser.add_argument('ionpos', help='ionpos filename. Must have extra ionpos at dark position at end of file for background')
    parser.add_argument('out', help='output filename')
    parser.add_argument('nruns', help='number of runs to do')
    #parser.add_argument('nions', type=int, help='number of ions, bright or dark, in chain')
    #parser.add_argument('ndark', type=int, help='number of dark ions in chain')
    parser.add_argument('-order', dest='order', help='order of ions, 1 = bright 0 = dark. Must have correct # of bright/dark regardless of whether using order')
    #parser.add_argument('-symmetry', action='store_const', const='True', help='0 = no sym, use order 1 = symmetrize on order 2 = no order specificity')
    parser.add_argument('-freqscan', nargs = 4, help='Run Freqscan. Params: High Freq, Low Freq, freqstep, pulse_duration')
    parser.add_argument('-rabiflop', nargs = 4, help='Run RabiFlop. Params: start time, stop time, timestep, frequency')
    
    arguments = parser.parse_args()

#

    PARENT_CONN, CHILD_CONN = Pipe()

    PROCESS = Process( target=experiment, args=(CHILD_CONN,arguments) )
    PROCESS.start()

    App( PARENT_CONN )

    PROCESS.join()

