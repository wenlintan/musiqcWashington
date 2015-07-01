import math
import pygame
from pygame.locals import *

class BSpline:
    def __init__(self):
        self.knots = []
        self.points = []

    def basis(self, i, p, t):
        knots = self.knots
        if p == 0:
            if knots[i] < knots[i+1] and knots[i] <= t and t < knots[i+1]:
                return 1
            return 0

        f1 = (t - knots[i])/(knots[i+p] - knots[i]) * basis(i,p-1,t)
        f2 = (knots[i+p+1]-t)/(knots[i+p+1]-knots[i+1]) * basis(i+1,p-1,t)
        final = f1 + f2
        return final

    def point(self, t):
        m = len(self.knots) + 1
        n = len(self.points) + 1
        p = m - n - 1
        
        seq = [ self.points[i] * self.N(i,p,t) for i in range(n) ]
        return sum(seq)

    def draw(self, screen, res)
