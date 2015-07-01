import voronoi
from voronoi import vector2

import pygame
from pygame.locals import *

pygame.init()
screen = pygame.display.set_mode( (800, 600) )
voronoi = voronoi.diagram( screen )

running = True
while running:
    
    event = pygame.event.poll()
    while event.type != pygame.NOEVENT:

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            voronoi.add_point( vector2(pos[0], pos[1]) )

        event = pygame.event.poll()

    screen.fill( (0,0,0) )
    voronoi.draw()
    pygame.display.flip()
    
