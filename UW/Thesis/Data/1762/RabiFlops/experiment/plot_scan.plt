
set term pdf 
set output 'YBBBBBscan.pdf'

set xlabel '1762nm Frequency Offset from Carrier (MHz)' offset 0,0.5
set ylabel 'Shelving Probability' offset 2
#set xrange [0.65:1.12]
set yrange [0:1]
set key spacing 0.5
set key samplen 2

set arrow from 0.69,0.75 to 0.69,0.6 head
set label '\scriptsize {Z}' at 0.685,0.8
set arrow from 0.81,0.75 to 0.81,0.6 head
set label '\scriptsize {Z}' at 0.805,0.8
set arrow from 0.87,0.75 to 0.87,0.6 head
set label '\scriptsize {R}' at 0.865,0.8
set arrow from 0.97,0.75 to 0.97,0.6 head
set label '\scriptsize {COM}' at 0.94,0.8
set arrow from 1.01,0.75 to 1.01,0.6 head
set label '\scriptsize {R}' at 1.005,0.8
set arrow from 1.07,0.75 to 1.07,0.6 head
set label '\scriptsize {COM}' at 1.05,0.8

filename = 'YBBBBBplot.txt'
plot filename using ($1):2:(sqrt(($2+0.001)*(1-$2+0.001)/$3)) index 0 lt 1 with lines t '\tiny {Outer barium ion}', \
	filename using ($1):2:(sqrt(($2+0.001)*(1-$2+0.001)/$3)) index 1 lt 2 with lines t '\tiny {Center barium ion}', \
	filename using 1:2:(sqrt(($2+0.001)*(1-$2+0.001)/$3)) index 2 lt 3 with lines, \
	filename using 1:2:(sqrt(($2+0.001)*(1-$2+0.001)/$3)) index 3 lt 4 with lines, \
	filename using 1:2:(sqrt(($2+0.001)*(1-$2+0.001)/$3)) index 4 lt 5 with lines, \
	filename using 1:2:(sqrt(($2+0.001)*(1-$2+0.001)/$3)) index 5 lt 6 with lines
