from libs.WaveformModule import *
import math
    
# Load basis set of waveforms
Wvf_Harmonic = LoadWaveform('Waveforms\\138Ba+\\GenIII_138Ba_0.5MHz_Harmonic_20deg.csv')
Wvf_MassAMU = 138
Wvf_FreqMHz = 0.5
#Wvf_Harmonic = LoadWaveform('Waveforms\\Base_40Ca+\\GenIII_Harmonic.csv')
#Wvf_MassAMU = 40
#Wvf_FreqMHz = 1
Wvf_Quad45   = LoadWaveform('Waveforms\\Base_40Ca+\\GenIII_Uniform_Quad45.csv')
Wvf_Ex       = LoadWaveform('Waveforms\\Base_40Ca+\\GenIII_Ex.csv')
Wvf_Ey       = LoadWaveform('Waveforms\\Base_40Ca+\\GenIII_Ey.csv')
Wvf_Ez       = LoadWaveform('Waveforms\\Base_40Ca+\\GenIII_Ez.csv')

# Desired waveform specifications
ZPosMicron   = 0        # [micron] Trapping z position
IonMassAmu   = 138      # [AMU] Mass of ion being trapped
IonCharge    = 1        # [e] Ion charge
AxialFreqMHz = 0.5      # [MHz] Desired axial frequency
Ex           = 0        # [V/m] Field to apply in x         
Ey           = -500     # [V/m] Field to apply in y
Ez           = 0        # [V/m] Field to apply in z
Quad45       = 0        # [scale] Quadrupole rotation

# Calculate resulting waveform
HarmonicScale = (IonMassAmu/float(Wvf_MassAMU)) \
               *math.pow(AxialFreqMHz/float(Wvf_FreqMHz),2)/IonCharge
result = PotentialsAtIndex(Wvf_Harmonic,ZPosMicron)
result = ScalePotentials(result,HarmonicScale)
field = PotentialsAtIndex(Wvf_Ex,ZPosMicron)
field = ScalePotentials(field,Ex/1000.)
result = AddPotentials(result,field)
field = PotentialsAtIndex(Wvf_Ey,ZPosMicron)
field = ScalePotentials(field,Ey/1000.)
result = AddPotentials(result,field)
field = PotentialsAtIndex(Wvf_Ez,ZPosMicron)
field = ScalePotentials(field,Ez/1000.)
result = AddPotentials(result,field)
quad = PotentialsAtIndex(Wvf_Quad45,ZPosMicron)
quad = ScalePotentials(quad,Quad45)
result = AddPotentials(result,quad)

# Remove small potentials (< 1 mV)
result = RemoveSmall(result,0.001)

# Display waveform
DisplayVal(result)
#raw_input('\nPress ENTER to exit\n')

# Write to file mimicking Sandia's format
names = ''
vals = ''
for k in range(0,51):
    names = names + 'e%02d      ' % k
    ch = 'GenIII_%02d' % k
    if ch in result.keys():
        vals = vals + '%+.3f   ' % result[ch]
    else:
        vals = vals + '0.       '
f = open('electrodes.txt','w')
f.write(names+'\n')
f.write(vals+'\n')
f.close()

