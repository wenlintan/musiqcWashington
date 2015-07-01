import pygame
from pygame.locals import *

import random

import geneticist, faction, city, output, grid, area, global_info
from vector3 import *

#create a random number generator
class random_generator:
    def __init__(self, minimum, maximum):
        self.mi = minimum
        self.ma = maximum
        
    def __call__(self, *args):
        return (random.random() * (self.ma-self.mi)) + self.mi


#create some information about the factions we're going to create
info = global_info.global_info()
info.num_factions = 4
info.faction_colors = [ vector3(255,0,0), vector3(0,0,255),
                        vector3(255,255,0), vector3(0,255,255) ]
info.faction_names = [ "orcs", "humans", "elves", "fairies" ]

grid.global_info = info
area.global_info = info

#initialize pygame
pygame.init()
screen = pygame.display.set_mode( (800,600), 0, 24 )
screen.fill( (0,0,0) )

#create information display structures
out = output.output( screen, 14 )
world = grid.grid( out, screen, (64,64), random_generator(10000, 15000) )

#create the factions
factions = []
for ident in range( info.num_factions ):
    area = world.get_random_unclaimed_area()
    area.faction_control[ ident ] = 100

    citypos = world.get_city_location( area )
    newcity = world.cities[ citypos ]

    newcity.faction_ident = ident
    newcity.population = 100
    
    fac = faction.faction( ident, out,
                           name = info.faction_names[ ident ],
                           cities = [ newcity ],
                           potential_cities = world.linearize_cities(),
                           areas = world.linearize_areas() )

    fac.preprocess()
    factions.append( fac )

genes = geneticist.genetic( factions )

running = True
while running:
    
    #poll input
    event = pygame.event.poll()
    while event.type != pygame.NOEVENT:
        
        if event.type == pygame.QUIT:
            running = False
            
        event = pygame.event.poll()

    #update the simulation
    out.log("Begining simulation tick:")
    
    for fac in factions:
        fac.tick()
        
    out.log("Tick complete.\n\n", output.output.SUCCESS)

    #draw representation
    screen.fill( (0,0,0) )
    world.draw()
    pygame.display.flip()

    #wait
    pygame.time.wait(1000)


#doned
pygame.quit()
