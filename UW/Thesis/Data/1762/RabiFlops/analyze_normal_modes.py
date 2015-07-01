#!/usr/bin/env python
"Find radial mode occupations using rabi flops and scans."

import numpy
import numpy.linalg

import scipy.optimize
from sympy import *

from ctypes import *
import argparse
import pickle
import random
import itertools

import matplotlib
#matplotlib.use( 'Agg' )
from matplotlib import pyplot

amu = 1.66053892e-27
e = 1.60217657e-19
oofpez= 8.987551e9
hbar = 1.055e-34

class TrapFrequencies:
    "Rescale trap parameters for different masses."
    def __init__( self, measured_mass, wx, wy, waxial, slope=0, slope2=0 ):
        "Initialize with trap parameters for one mass."
        self.mass = float(measured_mass)
        self.ws = (wx, wy, waxial)
        self.slope = slope
        self.slope2 = slope2

    def wx( self, mass ):
        "Get rescaled x secular frequency."
        scale = (self.mass / mass)
        return self.ws[0] * scale
    def wy( self, mass ):
        "Get rescaled y secular frequency."
        scale = (self.mass / mass)
        return self.ws[1] * scale
    def waxial( self, mass ):
        "Get rescaled z secular frequency."
        scale = (self.mass / mass) ** 0.5
        return self.ws[2] * scale

def radial_freqs( masses, trap_freqs ):
    "Solve for radial mode frequencies given ion masses and trap strength."
    nions = len( masses )
    wx, wy, waxial = trap_freqs.wx, trap_freqs.wy, trap_freqs.waxial
    zpos = symbols( ' '.join( 'z'+str(i) for i in range(nions) ) )
    axial_trap = sum( m * amu * waxial(m)**2 / 2 * zpos[i]**2 
        for i, m in enumerate( masses ) )
    coulomb = sum( oofpez * e**2 / 1 * sqrt( 1 / (zpos[j] - zpos[k])**2 ) 
        for k in range(1, nions) for j in range(k) )

    eqns = [ diff( axial_trap + coulomb, zpos[i] ) for i in range(nions) ]
    initial = [10e-6 * (i - (nions-1) / 2.0) for i in range(nions)]
    axial_positions = nsolve( eqns, zpos, initial )
    
    xpos = symbols( ' '.join( 'x'+str(i) for i in range(nions) ) )
    ypos = symbols( ' '.join( 'y'+str(i) for i in range(nions) ) )
    radial_trap = sum( 
        m*amu*wx(m)**2 / 2 * xpos[i]**2 + m*amu*wy(m)**2 / 2 * ypos[i]**2
        for i, m in enumerate( masses ) )
    full_coulomb = sum( oofpez * e**2 / 1 * 
        sqrt( 1 / ((xpos[i] - xpos[j])**2 + (ypos[i] - ypos[j])**2 +
            (zpos[i] - zpos[j])**2) )
        for j in range(1, nions) for i in range(j) )
    rpos = xpos + ypos

    Vx = numpy.array([[ 
        ( diff( diff(1 / sqrt( amu*masses[i] * amu*masses[j] ) * 
        (axial_trap + radial_trap + full_coulomb), xpos[i]), xpos[j] )
        .subs( zip( rpos, [0.0]*2*nions ) )
        .subs( zip( zpos, axial_positions ) )).evalf()
        for j in range(nions)] for i in range(nions)], dtype=numpy.float64)
    wsx, vsx = numpy.linalg.eig( Vx )
    wsx = numpy.sqrt( wsx )
    wsx += (trap_freqs.slope + 2*numpy.pi*10e3) * (wsx < 2*numpy.pi*1.1e6)
    wsx += (trap_freqs.slope2 - 2*numpy.pi*15e3) * (wsx < 2*numpy.pi*.99e6)
    #wsx += (trap_freqs.slope - 4.5/60) * (wsx - 2*numpy.pi*0.9e6) 

    Vy = numpy.array([[ 
        ( diff( diff(1 / sqrt( amu*masses[i] * amu*masses[j] ) * 
        (axial_trap + radial_trap + full_coulomb), ypos[i]), ypos[j] )
        .subs( zip( rpos, [0.0]*2*nions ) )
        .subs( zip( zpos, axial_positions ) )).evalf()
        for j in range(nions)] for i in range(nions)], dtype=numpy.float64)
    wsy, vsy = numpy.linalg.eig( Vy )
    wsy = numpy.sqrt( wsy )
    wsy += (trap_freqs.slope + 2*numpy.pi*10e3) * (wsy < 2*numpy.pi*1.1e6)
    wsy += (trap_freqs.slope2 - 2*numpy.pi*15e3) * (wsy < 2*numpy.pi*.99e6)
    #wsy += (trap_freqs.slope - 4.5/60) * (wsy - 2*numpy.pi*0.9e6)
    print( wsx/2/numpy.pi/1e6 )
    print( wsy/2/numpy.pi/1e6 )

    Vz = numpy.array([[ 
        ( diff( diff(1 / sqrt( amu*masses[i] * amu*masses[j] ) * 
        (axial_trap + radial_trap + full_coulomb), zpos[i]), zpos[j] )
        .subs( zip( rpos, [0.0]*2*nions ) )
        .subs( zip( zpos, axial_positions ) )).evalf()
        for j in range(nions)] for i in range(nions)], dtype=numpy.float64)
    wsz, vsz = numpy.linalg.eig( Vz )
    wsz = numpy.sqrt( wsz )

    return (numpy.concatenate( (wsx, wsy), axis=0 ), 
        numpy.concatenate( (vsx, vsy), axis=1 ))

def radial_scan( masses, trap_freqs, exptime, width, rabi_freqs, nbars, freqs ):
    nions = len(masses)
    ws, vs = radial_freqs( masses, trap_freqs )

    output = []
    for i in range( nions ):
        shelves = []
        m, r = masses[i], rabi_freqs[i]
        for f in freqs:
            res = 0.0
            for j, n, w in zip( range(2*nions), nbars, ws ):
                v = vs[i,j]
                eta = numpy.sqrt( hbar / 2 / m / amu / w ) * 2 * numpy.pi / \
                    1.762e-6 / numpy.sqrt(2) * v
            
                res += (0.25 * r ** 2 * eta ** 2 * abs(n) * exptime ** 2 * 
                    numpy.sin( (f-w)/width ) ** 2 /
                    ((f-w)/width) ** 2)
            shelves.append( res )
        output.append( numpy.array(shelves) )
    return output

def rabi_flop( masses, trap_freqs, s, rabi_freqs, coherence, times ):
    "Generate theoretical rabi flop for fitting."
    nions = len(masses)

    fit_temperature = False
    if fit_temperature:
        masses = masses * amu
        ws, vs = radial_freqs( masses, trap_freqs )

        c_masses = masses.ctypes.data_as( POINTER(c_double) )
        c_rabis = rabi_freqs.ctypes.data_as( POINTER(c_double) )

        c_ws = ws.ctypes.data_as( POINTER(c_double) )
        c_vs = vs.ctypes.data_as( POINTER(c_double) )
        #c_nbars = nbars.ctypes.data_as( POINTER(c_double) )
        c_times = times.ctypes.data_as( POINTER(c_double) )

        result = numpy.zeros( (nions, len(times)), dtype=numpy.float64 )
        c_result = result.ctypes.data_as( POINTER(c_double) )

        try:
            rabi_flop = cdll.rabi_flop
        except:
            rabi_flop = cdll.LoadLibrary( 'librabi_flop.so' )

        rabi_flop.rabi_flop( c_size_t(2000000), 
            c_size_t(nions), c_size_t(len(times)), c_double(s),
            c_masses, c_rabis, c_ws, c_vs, c_nbars, c_times, c_result
            )
        return result

    output = []
    for i in range( nions ):
        shelves = []
        m, r = masses[i], rabi_freqs[i]

        for t in times:
            res = s * (1. - numpy.exp( -t / coherence ) * numpy.cos( 2*r*t ))
            shelves.append( res )
        output.append( numpy.array(shelves) )
    return output


class FitParams:
    def __init__( self, nions, trap_freqs ):
        self.nions = nions
        self.trap_freqs = trap_freqs
        self.slope = trap_freqs.slope
        self.slope2 = trap_freqs.slope2

    def initialize( self, width, optpump, cohtime, rabis, nbars ):
        self.width, self.optpump, self.cohtime = width, optpump, cohtime
        self.rabis, self.nbars = rabis, nbars

    def to_list( self ):
        result = [self.trap_freqs.ws[0], self.trap_freqs.ws[1],
            self.trap_freqs.ws[2], self.width, self.optpump, self.cohtime]
        #result = [self.width, self.optpump, self.cohtime]
        result.append( self.trap_freqs.slope )
        result.append( self.trap_freqs.slope2 )
        result.extend( self.nbars )
        result.extend( self.rabis )
        return result

    def from_list( self, l ):
        wx, wy, wz, self.width, self.optpump, self.cohtime, \
            self.slope, self.slope2 = l[:8]
        self.trap_freqs = TrapFrequencies( self.trap_freqs.mass, wx, wy, wz,
            self.slope, self.slope2 )
        #self.width, self.optpump, self.cohtime = l[:3]
        self.nbars = l[8: 8+2*self.nions]
        self.rabis = l[8+2*self.nions:]

    def to_list_all( self ):
        result = [self.trap_freqs.ws[0], self.trap_freqs.ws[1],
            self.trap_freqs.ws[2], self.width, self.optpump, self.cohtime]
        result.append( self.trap_freqs.slope )
        result.append( self.trap_freqs.slope2 )
        result.extend( self.nbars )
        result.extend( self.rabis )
        return result
        
def fit( fitparamfile, rabifilename, freqfilename, 
        carrier_freq, exptime, trap_freqs ):

    rabidata = numpy.loadtxt( rabifilename )
    freqdata = numpy.loadtxt( freqfilename )
    nions = int( (len( rabidata[0] ) - 1) / 2 )
    bright = numpy.array( list( x != 0 for x in rabidata[0, 1+nions:] ) )
    masses = numpy.array( list( 138. if b else 174. for b in bright ), 
            dtype=numpy.float64 )

    times = rabidata[:,0] * 1e-6
    freqs = (freqdata[:,0] - carrier_freq) * 2*numpy.pi*1e6
    rabishelves = [rabidata[:,1+i] for i in range(nions) if bright[i]]
    freqshelves = [freqdata[:,1+i] for i in range(nions) if bright[i]]

    width = 2*numpy.pi*8e3
    #rabi_freqs = [0.07e6, 0.10e6, 0.11e6, 0.11e6, 0.10e6, 0.07e6]
    rabis = [0.11e6, 0.14e6, 0.14e6, 0.11e6]
    nbars = [10., 10., 3000., 3000., 10., 10., 3000., 3000.]#[10.] * 2 * nions
    params = FitParams( nions, trap_freqs )
    params.initialize( width, 0.45, 50e-6, rabis, nbars )

    def fit_fn( lparams ):
        "Error function for fitting."
        print( lparams )
        params.from_list( lparams )
        riter = iter( params.rabis )
        rabis = [ next(riter) if bright[i] else 0.0 for i in range(nions) ]
        rabis = numpy.array( rabis, dtype=numpy.float64 )
        nbars = numpy.array( params.nbars, dtype=numpy.float64)

        tfreqs = params.trap_freqs
        rabitheory = rabi_flop( masses, tfreqs, params.optpump, 
            rabis, params.cohtime, times )
        freqtheory = radial_scan( masses, tfreqs, exptime, params.width, 
            rabis, nbars, freqs )
        rabitshelves = [t for i, t in enumerate( rabitheory ) if bright[i]]
        freqtshelves = [t for i, t in enumerate( freqtheory ) if bright[i]]

        err = []
        for s, t in zip( rabishelves, rabitshelves ):
            err = numpy.concatenate( (err, s - t) )
        for s, t in zip( freqshelves, freqtshelves ):
            err = numpy.concatenate( (err, s - t) )
        print( "Error: {}".format( (err**2).sum( axis=0 ) ) )
        return err

    lparams, _ = scipy.optimize.leastsq( fit_fn, params.to_list(), ftol=1e-4 )
    params.from_list( lparams )

    riter = iter( params.rabis )
    rabis = [ next(riter) if bright[i] else 0.0 for i in range(nions) ]
    rabis = numpy.array( rabis, dtype=numpy.float64 )
    nbars = numpy.array( params.nbars, dtype=numpy.float64)

    tfreqs = params.trap_freqs
    theorytimes = numpy.arange( min(times), max(times), 1e-6 )
    theoryfreqs = numpy.arange( min(freqs), max(freqs), 2*numpy.pi*1e3 )
    rabitheory = rabi_flop( masses, tfreqs, params.optpump, 
        rabis, params.cohtime, theorytimes )
    freqtheory = radial_scan( masses, tfreqs, exptime, params.width, 
        rabis, nbars, theoryfreqs )

    storedinfo = [params.to_list_all(), freqs, freqdata, theoryfreqs, 
            freqtheory, times, rabidata, theorytimes, rabitheory] 
    outfile = open(fitparamfile, 'wb')
    pickle.dump(storedinfo, outfile)
    outfile.close()

def draw_plot(storeddata, exptime):
    "Plot previously fit data."
    fitfile = open(storeddata, 'rb')
    opendata = pickle.load(fitfile)
    fitfile.close()

    lparams = opendata[0]
    freqs = opendata[1]
    freqdata = opendata[2]
    theoryfreqs = opendata[3]
    freqtheory = opendata[4]
    times = opendata[5]
    rabidata = opendata[6]
    theorytimes = opendata[7]
    rabitheory = opendata[8]

    nions = len( freqtheory )

    bright = list( x!=0 for x in freqdata[0,1+nions:] )
    conf = ''.join( "B" if b else "Y" for b in bright )
    masses = numpy.array( list( 138 if b else 174 for b in bright ), 
            dtype=numpy.float64 )

    params = FitParams( nions, TrapFrequencies( 138, 0, 0, 0 ) )
    params.from_list( lparams )
    wx, wy, wz = params.trap_freqs.ws
    width, s, cohtime = params.width, params.optpump, params.cohtime
    riter = iter( params.rabis )
    rabis = [ next(riter) if bright[i] else 0.0 for i in range(nions) ]
    rabis = numpy.array( rabis, dtype=numpy.float64 )
    nbars = numpy.array( params.nbars, dtype=numpy.float64)

    nbars = numpy.abs( nbars )
    #nbars[2] = (nbars[2]+nbars[3])/2.
    #nbars[3] = nbars[2]
    #nbars[6] = (nbars[6]+nbars[7])/2.
    #nbars[7] = nbars[6]
    print( "Trap frequencies: {}, {}, {}".format(
        wx / 2 / numpy.pi / 1e6, wy / 2 / numpy.pi / 1e6, 
        wz / 2 / numpy.pi / 1e6 ) )
    print( "OP efficiency: {}".format( s ) )
    print( "1762 Decoherence Time: {}".format( cohtime ) )
    print( "Radial line width: {}".format( width / 2 / numpy.pi / 1e6 ) )
    print( "Rabi frequencies: {}".format(
        ', '.join( str(r) for r in rabis ) ) )
    print( "NBars: {}".format(
        ', '.join( str(n) for n in nbars ) ) )


    ws, vs = radial_freqs( masses, params.trap_freqs )
    rabitheory = rabi_flop( masses, params.trap_freqs, s, 
        rabis, nbars, theorytimes )

    times = times * 1e6
    theorytimes = theorytimes * 1e6

    if False:
        pyplot.subplot(211)
        space = 0.0
        colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k']
        for i, b, c in zip( range( nions ), bright, colors ):
            if not b: continue
            d = rabidata[:,1+i]
            n = rabidata[:,1+nions+i]
            e = numpy.sqrt( (d + 1e-6)*(1-d+1e-6)/n )
            pyplot.errorbar( times, d + i*space, 
                    yerr=e, fmt=c+'+', markersize=12 )
            pyplot.plot( theorytimes, rabitheory[i] + i*space, c )
        pyplot.yticks( [] )
        pyplot.xlabel( "1762nm Laser Exposure Time (us)" )
        pyplot.title( "Rabi Flop on 1 Yb and 5 Ba ions ({})".format(conf) )
        pyplot.ylim( (-0.0, 1.0) )
        pyplot.xlim( (0, 50) )

    freqs = freqs / 2 / numpy.pi / 1e6
    freqtheory = radial_scan( masses, params.trap_freqs, exptime, 
        params.width, rabis, nbars, theoryfreqs )
    theoryfreqs = theoryfreqs / 2 / numpy.pi / 1e6

    #pyplot.subplot(212)
    space = 0.5
    colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k']
    for i, b, c in zip( range( nions ), bright, colors ):
        if not b: continue
        d = freqdata[:,1+i]
        n = freqdata[:,1+nions+i]
        e = numpy.sqrt( (d + 1e-6)*(1-d+1e-6)/n )
        pyplot.errorbar( freqs, d + i*space, 
                yerr=e, fmt=c+'+', markersize=12 )
        pyplot.plot( theoryfreqs, freqtheory[i] + i*space, c )
    pyplot.yticks( [] )
    pyplot.xlabel( "1762nm Laser Carrier Offset (MHz)" )
    pyplot.title( "Radial Modes of 2 Yb and 2 Ba ions ({})".format(conf) )
    pyplot.ylim( (-0.1, 2.2) )
    pyplot.xlim( (0.9, 1.35) )

    for ion, nbar, w in zip( range(2*nions), nbars, ws ):
        bestion = max( (v**2, i) for i, v in enumerate( vs[:,ion] )
            if bright[i % nions] )[1]
        pyplot.annotate( str(int(nbar)), 
            (w / 2 / numpy.pi / 1e6, bestion*space + 0.25 + 0.3 * (ion%nions==3)),
            xytext=(-40, 10), textcoords='offset points',
            arrowprops=dict(arrowstyle="->",
                connectionstyle="arc3,rad=.2") )
    pyplot.show()
    #pyplot.savefig( '{}.pdf'.format( conf ), bbox_inches='tight' )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Fit Rabi flops and normal mode scans')
    parser.add_argument('rabi', help='Rabi flop data to be fit/plotted')
    parser.add_argument('freq', help='Frequency scan data to be fit/plotted')
    parser.add_argument('-freqs', nargs = 4,
        help = 'Find normal modes. Params: conf, wx, wy, wz (MHz)')
    parser.add_argument('-fit', nargs = 4, 
        help = 'Do fit, save to file. Params: filename, wx, wy, wz (MHz)')
    parser.add_argument('-plot', nargs = 1, 
        help = 'Plot theory and data. Params: filename')

    args = parser.parse_args()
    carrier_freq = 84.37
    exp_time = 300e-6

    if args.freqs:
        masses = [138 if int(x) else 174 for x in args.freqs[0]]
        wx, wy, wz = (2*numpy.pi*float(x)*1e6 for x in args.freqs[1:])
        ws, vs = radial_freqs( masses, TrapFrequencies(138, wx, wy, wz) )

        for i in range( 2*len(masses) ):
            print( "Frequency: {}".format( ws[i] / 2 / numpy.pi / 1e6 ) )
            print( "Vector: {}".format(
                ', '.join( str(vs[c,i]) for c in range(len(masses)) ) ) )

    if args.fit:
        fitparamfile = args.fit[0]
        wx, wy, wz = (2*numpy.pi*float(x)*1e6 for x in args.fit[1:])
        fit( fitparamfile, args.rabi, args.freq, carrier_freq, exp_time,
                TrapFrequencies(138, wx, wy, wz))

    if args.plot:
        draw_plot(args.plot[0], exp_time)

