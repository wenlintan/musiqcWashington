#!/usr/bin/env python

import sys
import scipy.integrate
import scipy.optimize
import numpy as np
from matplotlib import pyplot as plt

HBAR = 1.034e-34
AMU = 1.66e-27
M_BA = 138 * AMU
M_MG = 25 * AMU
KB = 1.38e-23

GAMMA_BA = 2*np.pi * 20.1e6
LAMBDA_BA = 0.493e-6
DELTA_BA = -2*np.pi * 16.6e6

GAMMA_MG = 2*np.pi * 41.4e6
LAMBDA_MG = 0.279e-6
DELTA_MG = -2*np.pi * 20e6

SAT = 1.9

E0 = HBAR * GAMMA_BA / 2 * np.sqrt( 1 + SAT )
T0 = 1. / ( GAMMA_BA * SAT / 2 / ( 1 + SAT ) )

RECOIL = (HBAR * 0.71 * 2*np.pi / LAMBDA_BA)**2 / 2 / M_BA / E0
DELTA = HBAR * DELTA_BA / E0

print( "Detuning: {}".format( DELTA ) )
print( "Recoil: {}".format( RECOIL ) )

if len( sys.argv ) < 3:
    print( "usage: {} <data_file> <bins>".format( sys.argv[0] ) )
    sys.exit(0)

FILENAME = sys.argv[1]
DATA = np.loadtxt( FILENAME )

WAIT = DATA[0]
RUNS = DATA[1]
DATA = DATA[2:]

BINS = int( sys.argv[2] )
EXPTIMES = np.arange( 0.01e-3, 1e-0, 0.01e-3*BINS )
DATA = sum( DATA[i::BINS] for i in range( BINS ) ) / float( BINS )

EXPTIMES = EXPTIMES[20:90] - 0.02
DATA = DATA[20:90]
plt.plot( EXPTIMES, DATA )
plt.show()

def Z_fn( energy, delta, recoil ):
    energy = np.clip( energy, 1.e-10, 1e100 )
    return 1j / np.sqrt( 1 - (delta + 1j)**2 / 4 / energy / recoil )

def dEdtau_fn( energy, tau, delta, recoil ):
    energy = np.clip( energy, 1.e-10, 1e100 )
    return 1. / 2 / np.sqrt( energy * recoil ) * \
        (   np.real( Z_fn( energy, delta, recoil ) ) +
            delta * np.imag( Z_fn( energy, delta, recoil ) )
        )

def dNdtau_fn( energy, delta, recoil ):
    energy = np.clip( energy, 1.e-10, 1e100 )
    return 1. / 2 / np.sqrt( energy * recoil ) * \
        np.imag( Z_fn( energy, delta, recoil ) )

def MaxwellBoltzmann( energy, mean_energy ):
    return 1. / mean_energy * np.exp( -energy / mean_energy )

TAU_STEP = 0.01 / RECOIL
TAUS = np.arange( 0, 850 / RECOIL, TAU_STEP )
ES = scipy.integrate.odeint( dEdtau_fn, 40 / RECOIL, TAUS, (DELTA, RECOIL) )
ES = ES[:, 0]
DNDTAUS = dNdtau_fn( ES, DELTA, RECOIL )
TIMES = TAUS * T0

plt.plot( TIMES, DNDTAUS )
plt.show()

def dNdtau_thermal( mean_energy, normalize ):
    print( "Energy: {}, Norm: {}".format( mean_energy*RECOIL, normalize ) )
    dES = -ES[1:] + ES[:-1]
    midES = (ES[1:] + ES[:-1]) / 2
    weights = 2 * np.exp( -midES / mean_energy ) * \
        np.sinh( dES / 2 / mean_energy)
    return np.array([
        np.sum( weights[:-i] * DNDTAUS[i+1:] )
        for i in range( 1, len(weights) ) ]) / normalize

def fit_fn( times, mean_energy, normalize ):
    dNdtau_thermals = dNdtau_thermal( mean_energy, normalize )
    return np.array([
        dNdtau_thermals[ int( t / TAU_STEP / T0 ) ]
        for t in times ])

#params = [ 5 / RECOIL, 0.1 ]
params = [ 7 / RECOIL, .9 ]
params, _ = scipy.optimize.curve_fit( fit_fn, EXPTIMES, DATA, params )

print( "Initial Energy: {}".format( params[0] * E0 ) )
print( "Normalization: {}".format( params[1] ) )


#DNDTAU_THERMALS = dNdtau_thermal( 5.1 / RECOIL, 0.7 )

DNDTAU_THERMALS = dNdtau_thermal( params[0], params[1] )
plt.plot( TIMES[:-2], DNDTAU_THERMALS )
plt.plot( EXPTIMES, DATA, 'r+' )
plt.xlim( -1.e-3, 61.e-3  )
#plt.ylim( 0.3, 0.5 )
plt.show()

