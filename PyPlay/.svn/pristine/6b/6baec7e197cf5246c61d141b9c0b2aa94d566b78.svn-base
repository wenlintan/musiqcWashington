from matplotlib.pyplot import *

f = open('out.txt', 'r')
data = []
lines = [l for l in f.readlines()]
starts = [ i for i,v in enumerate(lines) if v.strip() == "Start" ]

for s in starts:
	i, d = s+1, [0]
	while i < len(lines) and not lines[i].strip() == "Start":
		try:
			d.append( int(lines[i].strip()) )
		except:
			d.append( d[-1] )
		i = i+1
	data.append( d )

for d in data[:10]:
	plot( d )
show()
