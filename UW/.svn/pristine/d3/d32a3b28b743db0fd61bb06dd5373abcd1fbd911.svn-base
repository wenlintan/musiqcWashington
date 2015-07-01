
set term epslatex color size 3.5in,2.5in
set output 'HeatingRateOrange.tex'

set xlabel 'Dark Time Before 1762nm Exposure (ms)' offset 0,0.5
set ylabel 'Total Motional Quanta' offset 2
set samples 300
unset key

filename = 'temperatures_orange.dat'
f(x) = a*x + b

fit f(x) filename using 1:2:3 via a, b
plot f(x), filename with errorbars

