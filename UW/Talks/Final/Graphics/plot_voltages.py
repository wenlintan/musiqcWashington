#!/usr/bin/env python

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

font = {'family' : 'normal',
        'weight' : 'normal',
        'size'   : 22}

matplotlib.rc('font', **font)
matplotlib.rc('figure', autolayout=True)
matplotlib.rc('xtick.major', pad=8 )
matplotlib.rc('ytick.major', pad=8 )

volts = [0.718929, 0.778137, 1.58724, -2.09125, 1.56385, 0.90748, 0.463796, 0.001]
volts2 = [0.572676, -0.548656, 2.51127, -1.38724, -0.783095, 2.22243, 0.487476, 0.001]
ind = np.arange( len(volts) )

fig, ax = plt.subplots()
ax.bar( ind, volts, 1.0 )

plt.ylim( -3, 3 )
plt.title( "Trapping Voltages Centered on Electrode", y=1.08 )
plt.xlabel( "Axial Electrode Position" )
plt.ylabel( "Voltage (V)" )
plt.show()

