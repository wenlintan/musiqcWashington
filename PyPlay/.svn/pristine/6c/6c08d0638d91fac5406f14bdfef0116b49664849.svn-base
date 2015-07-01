set terminal postscript eps color lw 4 "Helvetica" 20 size 5in, 4in
set out 'data.eps'
set ylabel 'Probability of Chain Order Stability'
set xlabel 'Dark Time (ms)'
set title 'Probability of Chain Stability During Doppler Recooling' 
plot 'data81' every ::1 u ($1):($2) t '8 ions, 1 Yb' lt 1 w lp
