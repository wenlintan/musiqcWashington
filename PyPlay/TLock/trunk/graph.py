
import sys

from numpy import *
#from scipy.fftpack import *

from matplotlib.pyplot import *

def make_plot( cutoff = 5000, show_plot = True, save = None ):
    f = open("data.txt", "r")
    data = array([[int(d.strip()) for d in l.split()] for l in f.readlines()])
    f.close()

    #Clear figure in case we're being called from somewhere
    clf()
    if cutoff > len(data):
        cutoff = len(data)
    recent = data[-cutoff:,:]
    plot(recent[:,1])
    plot(recent[:,4])
    plot(recent[:,7])
    #small, big = min( recent[:,5] ), max( recent[:,5] )
    #print big, small, recent[0,:], recent[:,3]
    #plot(recent[:,3]*(big - small)/64. + small)
    #figure()
    #plot(abs(rfft(recent[:,1]))[1:100])
    if save is not None:
        savefig( save )

    if show_plot:
        show()

if __name__ == "__main__":
    cutoff = 5000
    if len(sys.argv) > 1:
        cutoff = int(sys.argv[1])
    make_plot(cutoff)
