k0 = 0.1
x0 = 83.86e6
d0 = 0.02e6
k1 = 0.3
x1 = 83.92e6
d1 = 0.02e6
filename = 'RadialSidebandsNoOutliers_2014-07-15_17-53-20_1762scanWithPumping.txt'

FIT_MAXITER = 100

f(x) = 1 - k0 * sin((x-x0)/d0) * sin((x-x0)/d0) / ((x-x0)/d0 + 1e-6) / ((x-x0)/d0 + 1e-6) - k1 * sin((x-x1)/d1) * sin((x-x1)/d1) / ((x-x1)/d1 + 1e-6) / ((x-x1)/d1 + 1e-6)

fit f(x) filename every ::1 using 1:2 via k0, x0, d0, k1, x1, d1
plot f(x), filename every ::1 using 1:2
#pause -1

