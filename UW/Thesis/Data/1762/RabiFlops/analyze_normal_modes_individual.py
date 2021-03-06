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

    Vy = numpy.array([[ 
        ( diff( diff(1 / sqrt( amu*masses[i] * amu*masses[j] ) * 
        (axial_trap + radial_trap + full_coulomb), ypos[i]), ypos[j] )
        .subs( zip( rpos, [0.0]*2*nions ) )
        .subs( zip( zpos, axial_positions ) )).evalf()
        for j in range(nions)] for i in range(nions)], dtype=numpy.float64)
    wsy, vsy = numpy.linalg.eig( Vy )
    wsy = numpy.sqrt( wsy )

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

def radial_peak( masses, ws, vs, exptime, widths, rabi_freqs, nbars, offs, freqs ):
    nions = len(masses)

    output = []
    for i in range( nions ):
        shelves = []
        m, r = masses[i], rabi_freqs[i]
        for f in freqs:
            res = 0.0
            for j, (n, w) in enumerate( zip(nbars, ws) ):
                v = vs[i,j]
                eta = numpy.sqrt( hbar / 2 / m / amu / w ) * 2 * numpy.pi / \
                    1.762e-6 / numpy.sqrt(2) * v
            
                res += (0.25 * r ** 2 * eta ** 2 * abs(n) * exptime ** 2 * 
                    numpy.sin( (f-w+offs[j])/widths[j] ) ** 2 /
                    ((f-w+offs[j])/widths[j]) ** 2)
            shelves.append( res )
        output.append( numpy.array(shelves) )
    return output

def radial_peak_blur( masses, ws, vs, exptime, widths, rabi_freqs, nbars, offs, freqs ):
    nions = len(masses)

    output = []
    for i in range( nions ):
        shelves = []
        m, r = masses[i], rabi_freqs[i]
        for f in freqs:
            res = 0.0
            for j, (n, w) in enumerate( zip(nbars, ws) ):
                laser_freqs = numpy.arange( -abs(widths[j])*3, 
                    abs(widths[j])*3, 2*numpy.pi*0.1e3 )
                probs = 1. / widths[j] / numpy.sqrt(2 * numpy.pi) * \
                    numpy.exp( -laser_freqs**2 / 2 / widths[j]**2 )
                v = vs[i,j]
                eta = numpy.sqrt( hbar / 2 / m / amu / w ) * 2 * numpy.pi / \
                    1.762e-6 / numpy.sqrt(2) * v
            
                cont = (0.25 * 2**2 * r ** 2 * eta ** 2 * abs(n) *  
                    numpy.sin( (f-w-laser_freqs+offs[j])*exptime/2 ) ** 2 /
                    ((f-w-laser_freqs+offs[j])/2.) ** 2)
                res += sum( p*c for p, c in zip( probs, cont ) ) / sum(probs)
                #rabisq = 2**2 * r **2 * eta**2 * abs(n)
                #wsq = (f-w-laser_freqs+offs[j])**2 + rabisq
                #cont = rabisq/wsq * \
                    #numpy.sin( numpy.sqrt(wsq) * exptime / 2)**2
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

    #rabis = [0.07e6, 0.10e6, 0.11e6, 0.11e6, 0.10e6, 0.07e6]
    rabis = [0.11e6, 0.14e6, 0.14e6, 0.11e6]
    nbars = [10.] * 2 * nions
    #nbars = [10., 10., 3000., 3000., 10., 10., 3000., 3000.]

    params = [ 0.45, 50e-6 ]
    barium_rabis = [ rabis[i] for i in range(nions) if bright[i] ]
    params.extend( barium_rabis )

    def rabi_fit( lparams ):
        optpump, cohtime = lparams[:2]
        rabiiter = iter( lparams[2:] )
        rabis = [ next(rabiiter) if bright[i] else 0. for i in range(nions) ]

        rabitheory = rabi_flop( masses, trap_freqs, optpump, 
            rabis, cohtime, times )
        rabitshelves = [t for i, t in enumerate( rabitheory ) if bright[i]]
        err = []
        for s, t in zip( rabishelves, rabitshelves ):
            err = numpy.concatenate( (err, s - t) )
        return err

    params, _ = scipy.optimize.leastsq( rabi_fit, params, ftol=1e-4 )
    optpump, cohtime = params[:2]
    rabiiter = iter( params[2:] )
    rabis = [ next(rabiiter) if bright[i] else 0. for i in range(nions) ]
    print( "Rabis: {}".format( ', '.join( str(r) for r in rabis ) ) )

    ws, vs = radial_freqs( masses, trap_freqs )
    used = [ False ] * len(ws)
    offsets = [ 0. ] * len(ws)
    widths = [ 0. ] * len(ws)
    nbars = [ 0. ] * len(ws)

    while not all(used):
        w = 0
        while used[w]:
            w += 1

        cur_ix = [w]
        used[w] = True
        w = ws[w]

        fit_width = 0.06e6
        #fit_width = 0.11e6
        for i, other_w in enumerate( ws ):
            if not used[i] and abs(w - other_w) < 2*numpy.pi*fit_width:
                cur_ix.append( i )
                used[ i ] = True

        cur_vs = vs[:,cur_ix]
        cur_ws = ws[cur_ix]
        print( cur_ws / 2/ numpy.pi / 1e6)

        cur_freqs, cur_shelves = [], []
        for i in range(len(freqshelves)):
            cur_shelves.append([])
            for f, s in zip( freqs, freqshelves[i] ):
                if abs(f - w) < 2*numpy.pi*fit_width:
                    if i == 0:
                        cur_freqs.append( f )
                    cur_shelves[-1].append( s )
        cur_freqs = numpy.array( cur_freqs )
        cur_shelves = numpy.array( cur_shelves )
        print( cur_freqs / 2 / numpy.pi / 1e6 )

        width = 2*numpy.pi*13e3
        params = [ width, 0.0 ]
        params.extend( [10000.]*len(cur_ws) if cur_ws[0] < 1.1e6*2*numpy.pi else [10.] * len(cur_ws) )

        def peak_fit( lparams ):
            width, offset = lparams[:2]
            widths, offsets = [width]*len(cur_ws), [offset]*len(cur_ws)
            nbars = lparams[2:]

            scantheory = radial_peak_blur( masses, cur_ws, cur_vs, exptime,
                widths, rabis, nbars, offsets, cur_freqs )

            scantshelves = [t for i, t in enumerate(scantheory) if bright[i]]
            err = []
            for s, t in zip(cur_shelves, scantshelves):
                sig = numpy.sqrt((1. - s)*(s+0.005) / 100)
                err = numpy.concatenate( (err, (s - t) / sig) )
            return err

        params, cov = scipy.optimize.leastsq( peak_fit, params, ftol=1e-4 )
        #print( cov )
        #errs = numpy.sqrt( numpy.diag(cov) )
        width, offset = params[:2]
        print( "Width: {}, Offset: {}".format( width, offset ) )
        print( "NBars: {}".format( ', '.join( str(p) for p in params[2:] )))
        #print( "NBar Errs: {}".format(
            #', '.join( str(e) for e in errs[2:] ) ) )
        for i, nb in zip( cur_ix, params[2:] ):
            offsets[i] = offset
            widths[i] = width
            nbars[i] = nb

    theorytimes = numpy.arange( min(times), max(times), 1e-6 )
    theoryfreqs = numpy.arange( min(freqs), max(freqs), 2*numpy.pi*1e3 )
    rabitheory = rabi_flop( masses, trap_freqs, optpump, 
        rabis, cohtime, theorytimes )
    freqtheory = radial_peak_blur( masses, ws, vs, exptime, widths, 
        rabis, nbars, offsets, theoryfreqs )

    params = [ trap_freqs, optpump, rabis, cohtime, widths, nbars, offsets ]
    storedinfo = [params, freqs, freqdata, theoryfreqs, 
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

    trap_freqs, s, rabis, cohtime, widths, nbars, offsets = lparams
    offx = sum( offsets[:nions] ) / nions
    offy = sum( offsets[nions:] ) / nions
    new_trap_freqs = TrapFrequencies( trap_freqs.mass, 
        trap_freqs.ws[0] - offx,
        trap_freqs.ws[1] - offy, trap_freqs.ws[2] )

    wx, wy, wz = trap_freqs.ws
    nbars = numpy.abs( nbars )
    print( "Trap frequencies: {}, {}, {}".format(
        wx / 2 / numpy.pi / 1e6, wy / 2 / numpy.pi / 1e6, 
        wz / 2 / numpy.pi / 1e6 ) )
    print( "OP efficiency: {}".format( s ) )
    print( "1762 Decoherence Time: {}".format( cohtime ) )
    print( "Rabi frequencies: {}".format(
        ', '.join( str(r) for r in rabis ) ) )
    print( "NBars: {}".format(
        ', '.join( str(n) for n in nbars ) ) )
    print( "Widths: {}".format(
        ', '.join( str(w) for w in widths ) ) )

    ws, vs = radial_freqs( masses, trap_freqs )
    new_ws, new_vs = radial_freqs( masses, new_trap_freqs )
    #rabitheory = rabi_flop( masses, trap_freqs, s, 
    #    rabis, nbars, theorytimes )

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

    #freqtheory = radial_scan( masses, params.trap_freqs, exptime, 
    #    params.width, rabis, nbars, theoryfreqs )

    freqs = freqs / 2 / numpy.pi / 1e6
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
    pyplot.ylim( (-0.1, 2.1) )
    pyplot.xlim( (0.8, 1.35) )

    pyplot.text( 0.81, 0.1, 'Ba', size=20 )
    pyplot.text( 0.81, 0.6, 'Ba', size=20 )
    pyplot.text( 0.81, 1.1, 'Yb', size=20 )
    pyplot.text( 0.81, 1.6, 'Yb', size=20 )

    for ion, nbar, w, new_w, off in zip( range(2*nions), nbars, ws, new_ws, offsets ):
        #pyplot.plot( (new_w / 2 / numpy.pi / 1e6, new_w /2 / numpy.pi / 1e6), (-0.1, 2.2), 'k-' )
        bestion = max( (v**2, i) for i, v in enumerate( vs[:,ion] )
            if bright[i % nions] )[1]
        pyplot.annotate( str(int(nbar)), 
            ((w-off) / 2 / numpy.pi / 1e6, bestion*space + 0.25 + 0.3 * (ion%nions==3)),
            xytext=(-40 - 5 * (ion==6) + 40 * (ion==2 or ion==3), 30), textcoords='offset points',
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
    parser.add_argument('-modeplot', nargs =4,
            help = 'Maximum barium eigenvector plot. Params: conf, wx, wy, wz (MHZ')

    args = parser.parse_args()
    carrier_freq = 84.37
    #carrier_freq = 84.65
    exp_time = 300e-6

    if args.freqs:
        masses = [138 if int(x) else 174 for x in args.freqs[0]]
        wx, wy, wz = (2*numpy.pi*float(x)*1e6 for x in args.freqs[1:])
        ws, vs = radial_freqs( masses, TrapFrequencies(138, wx, wy, wz) )

        ax = matplotlib.pyplot.axes()

        for i in range( 2*len(masses) ):
            print( "Frequency: {}".format( ws[i] / 2 / numpy.pi / 1e6 ) )
            print( "Vector: {}".format(
                ', '.join( str(vs[c,i]) for c in range(len(masses)) ) ) )


        def arrow_shrink(mag):
            if numpy.abs(mag) < .05:
                if numpy.abs(mag) <.005:
                    return .3
                return .5
            else:
                return 1

            
#        for mode in range(len(masses)):
#            for ion in range(len(masses)):
#                arrow_len = vs[ion,mode]
#                ax.arrow((ion/4+.125)/3, 1.5-mode, 0, -arrow_len/2.8,
#                    width =arrow_shrink(arrow_len)*.007, head_width =
#                    arrow_shrink(arrow_len)*0.017, head_length =
#                    arrow_shrink(arrow_len)*0.1, fc=('c' if ion == 0
#                        or ion == 2 else 'm'), ec='k')
#        ax.arrow(0.1, 0, 0, .6 - .1, width = .007, head_width = 0.017,
#                head_length = 0.1, fc='c', ec='k')
#        ax.arrow(0.15, 0, 0, .6*24/34 -.1, width = .007, head_width = 0.017,
#                head_length = 0.1, fc='c', ec='k')
#        ax.arrow(0.2, 0, 0, .6*33/34 -.1, width = .007, head_width = 0.017,
#                head_length = 0.1, fc='c', ec='k')
#        ax.arrow(0.25, 0, 0, .6*19/34 -.1, width = .007, head_width = 0.017,
#                head_length = 0.1, fc='c', ec='k')
#
#        matplotlib.pyplot.text(.093, -.5, r'3', fontsize = 30)
#        matplotlib.pyplot.text(.093+.05, -.5, r'3', fontsize = 30)
#        matplotlib.pyplot.text(.093+.1, -.5, r'Z', fontsize = 30)
#        matplotlib.pyplot.text(.093+.15, -.5, r'Z', fontsize = 30)
#        matplotlib.pyplot.axis([0,.5*2/3,-2,2.1])
        matplotlib.pyplot.axis([0,.5*2/3,-.034*.7/.6,.034*.85/.6])
        matplotlib.pyplot.hlines(0.035,0,.5*2/3, linestyles=u'dashed')
        fig = matplotlib.pyplot.gcf()
        fig.set_size_inches(8,4)
        matplotlib.pyplot.tick_params(
                axis = 'both',
                which = 'both',
                bottom = 'off',
                top = 'off',
                left = 'off',
                right = 'off',
                labelbottom = 'off',
                labelleft = 'on')

#        matplotlib.pyplot.show()


    if args.fit:
        fitparamfile = args.fit[0]
        wx, wy, wz = (2*numpy.pi*float(x)*1e6 for x in args.fit[1:])
        fit( fitparamfile, args.rabi, args.freq, carrier_freq, exp_time,
                TrapFrequencies(138, wx, wy, wz))

    if args.plot:
        draw_plot(args.plot[0], exp_time)

    if args.modeplot:
        masses = [138 if int(x) else 174 for x in args.modeplot[0]]
        wx, wy, wz = (2*numpy.pi*float(x)*1e6 for x in args.modeplot[1:])
        ws, vs = radial_freqs( masses, TrapFrequencies(138, wx, wy, wz) )

        for i in range(2* len(masses) ):
            print( "Frequency: {}".format( ws[i] / 2 / numpy.pi / 1e6 ) )
            print( "Vector: {}".format(
                ', '.join( str(vs[c,i]) for c in range(len(masses)) ) ) )
            print(vs)

        print(numpy.hsplit(vs,4))
#        matplotlib.pyplot.plot(numpy.abs(vs), 'ro')
#        matplotlib.pyplot.axis([0,4,0,.3])
#        matplotlib.pyplot.show()
#        print(vs)
    
