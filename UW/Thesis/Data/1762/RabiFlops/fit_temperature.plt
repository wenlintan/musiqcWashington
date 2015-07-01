
set term pdf color size 3.5in,2.5in
set output 'HeatingRateT0Orange.pdf'

set xlabel '1762nm Laser Exposure Time (\(\mu\)s)' offset 0,0.5
set ylabel 'Shelving Probability' offset 2
set yrange [0:1]
set samples 400
unset key

s = 0.47
w = 0.12

n1 = 50.0
l1 = sqrt( 1.055e-34 / 2 / 138 / 1.67e-27 /2 / 3.1415/ 1.1e6 ) * \
	2 * 3.141 / 1.762e-6 / sqrt(2)  #0.015
print l1

#filename = '2014-07-14_14-10-03_1762scanWithPumping.txt'
#filename = 'MadeupData.txt'
#filename = '2014-07-26_19-30-26_1762scanWithPumping.txt'
#filename = '2014-07-26_20-35-16_1762scanWithPumping.txt'
#filename = '2014-07-14_14-10-03_1762scanWithPumping.txt'
filename = 'HeatingRateT0Orange.txt'

f(x) = s*( 1 - (sum [i=0:5000] \
	(1 / (n1+1) * (n1 / (n1+1))**i * \
	cos( 2*w*(1 - l1**2*i)*x ))) )

fit f(x) filename \
	every ::1::83 using 1:(1-$2):(sqrt(200*($2+0.001)*(1-$2+0.001))/200) \
	via s, w, n1

plot f(x) lt 1, filename \
	every ::1::83 using 1:(1-$2):(sqrt(200*($2+0.001)*(1-$2+0.001))/200) \
	with errorbars lt 1


