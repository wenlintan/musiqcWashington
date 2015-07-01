#!/usr/bin/env python
"""Calculate shelving probabilities given an infinitely narrow laser with a 
varying frequency between runs."""

import numpy as np

SIGMA = 2*np.pi*10e3
MEAN = 0
WRABI = 2*np.pi*50e3

def gaussian( var, mu, sigma ):
    "Calculate gaussian probability."
    return (1. / sigma / np.sqrt(2 * np.pi) * 
        np.exp( -(var - mu) ** 2 / 2. / sigma**2 ))

def rabi_flop( time, w_rabi, detuning ):
    "Calculate shelving probability."
    return (w_rabi**2 / (w_rabi**2 + detuning**2) * 
        np.sin( np.sqrt(w_rabi**2 + detuning**2) * time / 2. ) ** 2)

LAMB_DICKE = 0.0145106
def rabi_flop_temped( time, w_rabi, detuning, nbar ):
    "Calculate shelving probability."
    return 0.5*(1 - sum( (w_rabi**2 / (w_rabi**2 + detuning**2) * 
        (1. / (nbar + 1.)) * (nbar / (nbar + 1.)) ** n *
        np.cos( 2 * np.sqrt(w_rabi**2 + detuning**2) * 
            (1 - LAMB_DICKE**2*n) * time ))
        for n in range( 4000 ) ) )

import matplotlib.pyplot as plt
FREQS = np.arange( -3*SIGMA, 3*SIGMA, 0.05*SIGMA )
PROBS = gaussian( FREQS, MEAN, SIGMA )
TIMES = np.arange( 0, 100e-6, 1e-6 )
FLOPS = [ rabi_flop_temped( TIMES, WRABI, dw, 75 ) for dw in FREQS ]

FLOP = np.sum( weight*shelves for shelves, weight in zip( FLOPS, PROBS ) )
FLOP /= np.sum( PROBS )

np.savetxt( 'sim_nbar_75.txt', np.transpose( (1e6*TIMES, FLOP) ) )
plt.plot( TIMES, FLOP )
plt.ylim( (0, 1) )
plt.show()

