import numpy as np
import scipy.fftpack as fft
from matplotlib.pyplot import *

xs = np.arange(0, 20)
plot( np.sin( xs ) )
plot( fft.dct( np.sin(xs), type=2 ) )
show()

