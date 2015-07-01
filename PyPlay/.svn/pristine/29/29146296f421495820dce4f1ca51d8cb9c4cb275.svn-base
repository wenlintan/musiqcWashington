import pygame
from pygame.locals import *

import grid

pygame.init()
screen = pygame.display.set_mode( (800,600), 0, 32 )
font = pygame.font.Font( None, 25 )

g = grid.Grid( screen, 6, 10 )
g.populate()

running = True
ticks = pygame.time.get_ticks()

while running:
    
    #poll input
    event = pygame.event.poll()
    while event.type != pygame.NOEVENT:
        
        if event.type == pygame.QUIT:
            running = False
            
        event = pygame.event.poll()

    new_ticks = pygame.time.get_ticks()
    deltat = (new_ticks - ticks) / 1000.0
    ticks = new_ticks
    
    g.update( deltat )
    
    screen.fill( (0,0,0) )
    g.draw()
    pygame.display.flip()


pygame.quit()
