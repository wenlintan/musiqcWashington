import pygame
from pygame.locals import *

import random

import faction, city, output, grid, area, global_info
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
info.num_factions = 2
info.faction_colors = [ vector3(255,0,0), vector3(0,0,255) ]
info.faction_names = [ "orcs", "humans" ]

grid.global_info = info
area.global_info = info

#initialize pygame
pygame.init()
screen = pygame.display.set_mode( (800,600), 0, 24 )
screen.fill( (0,0,0) )

#create information display structures
out = output.output( screen, 14 )
world = grid.grid( out, screen, (64,64), random_generator(36, 64) )

#create the factions
area = world.get_area_at( 0, 0 )
area.faction_control[0] = 100

Thragg = world.cities[0] = city.city(area.pos,
                                     out,
                                     faction_ident=0,
                                     population=100,
                                     name="Thragg",
                                     area=area)

orcs = faction.faction( 0, out, name = "orcs",
                        cities = [ Thragg ],
                        areas = world.linearize() )
orcs.preprocess()

area = world.get_area_at( world.tile_dim[0]-1, world.tile_dim[1]-1 )
area.faction_control[1] = 100

Detroit = world.cities[ len(world.cities)-1 ] = city.city(area.pos,
                                                          out,
                                                          faction_ident=1,
                                                          population=100,
                                                          name="Detroit",
                                                          area=area)
humans = faction.faction( 1, out, name = "humans",
                          cities = [ Detroit ],
                          areas = world.linearize() )
humans.preprocess()






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
    orcs.tick()
    humans.tick()
    out.log("Tick complete.\n\n", output.output.SUCCESS)

    #draw representation
    screen.fill( (0,0,0) )
    world.draw()
    pygame.display.flip()

    #wait
    pygame.time.wait(1000)


#doned
pygame.quit()
