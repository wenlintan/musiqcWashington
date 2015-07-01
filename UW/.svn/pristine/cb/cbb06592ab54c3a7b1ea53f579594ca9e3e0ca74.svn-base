#!/usr/bin/env python
"""Fit temperature from Rabi flop assuming decoherence is caused by 
interfering carrier transitions."""

import sys

from matplotlib import pyplot

import numpy
import numpy.linalg
import scipy.optimize

class Fitter:
    "Perform temperature fitting."
    def __init__( self, data_file ):
        "Load data and generate fit parameters."

        hbar = 1.055e-34
        mass = 138 * 1.67e-27
        w_trap = 2 * numpy.pi * 1.1e6
        self.lamb_dicke = numpy.sqrt( hbar / 2 / mass / w_trap ) * \
            2 * numpy.pi / 1.762e-6 / numpy.sqrt(2)
        print( "Using lamb dicke parameter {}".format( self.lamb_dicke ) )

        data = numpy.loadtxt( data_file, skiprows=1 )
        self.times = times = data[:, 0]
        self.shelves = shelves = 1.0 - data[:, 1]
        self.sigmas = sigmas = numpy.sqrt( 
            (shelves+0.001) * (1 - shelves + 0.001) / 200. ) #data[:, 2] )

        params = [0.12, 100, 0.45]
        #params = [0.3, 100, 0.45]

        params, cov = scipy.optimize.curve_fit( self._fit_fn_noise,
            times, shelves, params, sigmas )
        self.w_rabi, self.n_bar, self.op_eff = params
        self.w_err, self.n_err, self.op_err = numpy.sqrt( numpy.diag(cov) )

    def _fit_fn( self, times, w_rabi, n_bar, op_eff ):
        "Generate theoretical shelves given parameters."
        #print( "{} {} {}".format( w_rabi, n_bar, op_eff ) )
        return op_eff * (1 - sum( 1/(n_bar + 1) * (n_bar/(n_bar + 1)) ** n *
            numpy.cos( 2 * w_rabi * (1 - self.lamb_dicke**2 * n) * times )
            for n in range( min( 5000, int(n_bar * 10) ) ) ) )

    def _gaussian( self, var, mu, sigma ):
        "Calculate gaussian probability."
        return (1. / sigma / numpy.sqrt(2 * numpy.pi) * 
            numpy.exp( -(var - mu) ** 2 / 2. / sigma**2 ))

    def _fit_fn_noise( self, times, w_rabi, n_bar, op_eff ):
        "Generate theoretical shelves including laser noise."
        print( "{} {} {}".format( w_rabi, n_bar, op_eff ) )
        SIGMA = 2*numpy.pi*5e3 / 1e6
        MEAN = 0
        WRABI = w_rabi #2*np.pi*50e3

        FREQS = numpy.arange( -3*SIGMA, 3*SIGMA, 0.2*SIGMA )
        PROBS = self._gaussian( FREQS, MEAN, SIGMA )
        FLOPS = [ self._fit_fn( times, numpy.sqrt(WRABI**2 + dw**2), 
            n_bar, op_eff * WRABI**2 / (WRABI**2 + dw**2) ) for dw in FREQS ]

        FLOP = numpy.sum( weight*shelves 
            for shelves, weight in zip( FLOPS, PROBS ) )
        FLOP /= numpy.sum( PROBS )
        return FLOP

    def get_theory( self, times ):
        "Return fit result for given times."
        return self._fit_fn_noise( times, self.w_rabi, self.n_bar, self.op_eff )

    def print_parameters( self ):
        "Print fit parameters."
        print( "N_bar: {} +- {}".format( self.n_bar, self.n_err ) )
        print( "Rabi frequency: {} +- {}".format( self.w_rabi, self.w_err ) )
        print( "Optical pumping: {} +- {}".format( self.op_eff, self.op_err ) )

if __name__ == "__main__":
    if len( sys.argv ) < 2:
        print( "usage: {} file_name".format( sys.argv[0] ) )
        sys.exit(0)

    FILENAME = sys.argv[1]
    FITTER = Fitter( FILENAME )
    FITTER.print_parameters()

    pyplot.xlim( 0, 150 )#FITTER.times[-1] )
    pyplot.ylim( 0, 1 )
    pyplot.grid( True )

    pyplot.title( "Shelving Probability vs. 1762 Exposure Time" )
    pyplot.xlabel( "1762 Exposure Times ($\mu$s)" )
    pyplot.ylabel( "Shelving Probability" )

    pyplot.errorbar( FITTER.times, FITTER.shelves, 
            yerr=FITTER.sigmas, fmt='r+' )

    FULLTIMES = numpy.arange( 0, FITTER.times[-1], 0.1 )
    pyplot.plot( FULLTIMES, FITTER.get_theory( FULLTIMES ), 'r' )

    if len( sys.argv ) > 2:
        FILENAME = sys.argv[2]
        FITTER = Fitter( FILENAME )
        FITTER.print_parameters()

        pyplot.errorbar( FITTER.times, FITTER.shelves, 
                yerr=FITTER.sigmas, fmt='g+' )

        FULLTIMES = numpy.arange( 0, FITTER.times[-1], 0.1 )
        pyplot.plot( FULLTIMES, FITTER.get_theory( FULLTIMES ), 'g' )

    pyplot.show()




