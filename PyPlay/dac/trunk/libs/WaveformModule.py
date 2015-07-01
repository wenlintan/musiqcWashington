import csv
########################################################3
#
# Waveform load/display/manipulation routines
#
# Developed by:
#   Jason M. Amini
# Company:
#   Quantum Information Systems Group
#   Georgia Tech Research Institute
# Version history:
#   2011.11.10  JA, Created basic functionality
#

def LoadWaveform(FileName):
  waveform = {'Error':False,'Channels':[], 'Index':[],'Potentials':[], \
              'FileName':FileName}
  try:
    # Open file
    f = open(FileName,'rb')
    reader = csv.reader(f)
    # Separate off header
    header = reader.next()
    channels = header[1:]
    for ch in channels:
      waveform['_'+ch] = []
    # Read body
    index = []
    potues = []
    for row in reader:
      if len(row) == 0:
        break
      if len(row)<len(header):
        print('Waveform row does not have the correct number of potues')
        print(FileName)
        break
      index.append(float(row[0]))
      pot = map(float,row[1:])
      potues.append(pot)
      for [v,ch] in zip(pot,channels):
        waveform['_'+ch].append(v)
    # Store waveform
    waveform['Channels'] = header[1:]
    waveform['Index'] = index
    waveform['Potentials'] = potues
    f.close()
    return waveform
  except csv.Error, e:
    print('CSV reader error %s at line %d' % (FileName, reader.line_num))
    waveform['Error'] = True
    return waveform
  except IOError:
    print('Unable to open or process file %s' % FileName)
    waveform['Error'] = True
    return waveform

def PotentialsAtIndex(waveform, index):
  channels = waveform['Channels']
  indices = waveform['Index']
  n = len(indices)
  # Find interpolation fraction, but first handle out of bounds results
  if (n<1):
    print('Waveform is empty')
    print('Waveform: %s' % waveform['FileName'])
    return {}
  elif (n==1):
    pots = {}
    for ch in channels:
      v = waveform['_'+ch]
      pots[ch] = v[0]
    return pots   
  elif (index<indices[0]):
    print('Index %g is less than the waveform minimum index %g.' \
          % (index,indices[0]))
    print('Waveform: %s' % waveform['FileName'])
    i = 1
    frac = 0.
  elif (index>indices[n-1]):
    print('Index %g exceeds the waveform maximum index %g.' \
          % (index,indices[n-1]))
    print('Waveform: %s' % waveform['FileName'])
    i = n-1
    frac = 1.
  else:
    # Find nearest index
    for i in range(1,n):
      if indices[i]>=index:
        break    
    frac = (index-indices[i-1])/round(indices[i]-indices[i-1])
  # Interpolate waveforms 
  pots = {}
  for ch in channels:
    v = waveform['_'+ch]
    pots[ch] = v[i-1]+(v[i]-v[i-1])*frac
  # Return results as an electrode dictionary
  return pots

def AddPotentials(pot1, pot2):
  channels = set(pot1.keys()+pot2.keys())
  sum = {}
  for ch in channels:
    v = 0
    if (ch in pot1.keys()):
      v += pot1[ch]
    if (ch in pot2.keys()):
      v += pot2[ch]
    sum[ch] = v
  return sum

def ScalePotentials(pot, scale):
  result = {}
  for ch in pot.keys():
    result[ch] = scale*pot[ch]
  return result

def RemoveSmall(pot, thresh):
  result = {}
  for ch in pot.keys():
    if (abs(pot[ch])>thresh):
      result[ch] = pot[ch]
  return result

def DisplayVal(pot):
  keys = pot.keys()
  keys.sort()
  for ch in keys:
    print('%s, %g' % (ch, round(pot[ch],3)))
    
