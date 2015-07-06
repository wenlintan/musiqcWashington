
set term epslatex color size 3.5in,2.5in
set output 'BBYrabi.tex'

set xlabel '1762nm Laser Exposure Time (\(\mu\)s)' offset 0,0.5
set ylabel 'Shelving Probability' offset 2
set yrange [0:1]
set samples 200
set key spacing 0.5
set key samplen 2
#set key opaque

s = 0.47

w1 = 0.10
n1 = 200.0 
w2 = 0.10
n2 = 200.0 
w3 = 0.10
n3 = 200.0 

l = sqrt( 1.055e-34 / 2 / 138 / 1.67e-27 /2 / 3.1415/ 1.1e6 ) * \
	2 * 3.141 / 1.762e-6 / sqrt(2)  #0.015
print l

filename = 'BBYrabiout.txt'

f(x, y) = (s>0.5)?100000.: s*( 1 - (sum [i=0:5000] \
	((y==0) ? (1 / (n1+1) * (n1 / (n1+1))**i * \
	cos( 2*w1*(1 - l**2*i)*x )) : \
	(y==1) ? (1 / (n2+1) * (n2 / (n2+1))**i * \
	cos( 2*w2*(1 - l**2*i)*x )) : \
	(1 / (n3+1) * (n3 / (n3+1))**i * \
	cos( 2*w3*(1 - l**2*i)*x )))) )

fit [0:81] [0:2] f(x,y) filename \
	using 1:-2:2:(sqrt(($2+0.001) * (1-$2+0.001)/$3)) \
	via s, w1, n1, w2, n2#, w3, n3

plot filename index 0 using 1:2:(sqrt(($2+0.001) * (1-$2+0.001)/$3)) lt 1 with errorbars t '\tiny {Outer barium ion}', \
	filename index 1 using 1:2:(sqrt(($2+0.001) * (1-$2+0.001)/$3)) lt 2 with errorbars t '\tiny {Center barium ion}', \
	f(x,0) lt 1 with lines t '', f(x,1) lt 2 with lines t ''#, f(x,2) lt 3 with lines 




