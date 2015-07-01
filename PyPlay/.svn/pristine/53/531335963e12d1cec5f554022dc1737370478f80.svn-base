set terminal epslatex color size 3.5in,2.5in
set out 'reorder.tex'
set ylabel 'Probability of Chain Order Stability' offset 2
set xlabel 'Final Ion Temperature (K)' offset 0,0.5
plot 'out81' every ::1 u (0.5*138*1.66e-27*$1*$1/1.38e-23):(1-$2) t '' with lines,\
        'data81' every ::1::60 u (0.209+$1*0.000468):2:(sqrt(($2+0.001)*(1-$2+0.001)/100)) t '' lt 1 with errorbars

#plot 'out52' every ::1 u (0.5*138*1.66e-27*$1*$1/1.38e-23):(1-$2) t '5 ions, 2 Yb' lt 1 with lines, \
	#'data52' every ::1 u (0.00670+$1*3.7847e-5):($2) t '' lt 1, \
	#'out73' every ::1 u (0.5*138*1.66e-27*$1*$1/1.38e-23):(1-$2) t '7 ions, 3 Yb' lt 2 with lines, \
	#'data73' every ::1 u (0.00+$1*7.89e-5):($2) t '' lt 2, \
	#'out91' every ::1 u (0.5*138*1.66e-27*$1*$1/1.38e-23):(1-$2) t '9 ions, 1 Yb' lt 3 with lines, \
	#'data91' every ::1 u (0.00+$1*2.049e-4):($2) t '' lt 3
