import pygame
from pygame.locals import *

import random

import base, city, area, resource
from vector3 import *
from global_info import *

class grid(base.base):
    "Provides graphical representation of simulation"
    
    def __init__( self, out, screen, tile_size, generator ):

        #avoid our attribute management system
        self.recurse_attributes = False
        
        self.screen = screen
        
        self.window = screen.get_size()

        self.tile_size = tile_size
        self.tile_dim = ( self.window[0]/tile_size[0],
                          self.window[1]/tile_size[1] )
        
        self.window = ( self.tile_dim[0] * tile_size[0],
                        self.tile_dim[1] * tile_size[1] )
        
        self.start_rect = Rect( (0,0), tile_size)

        self.ts = ts = tile_size
        self.hts = hts = (ts[0]/2, ts[1]/2)

        self.areas = [ [ area.area( vector3( x*ts[0] + hts[0],
                                             y*ts[1] + hts[1],
                                             0 ),
                                    ts,
                                    potential = resource.resource(
                                                    food = generator(x, y),
                                                    wood = generator(x, y),
                                                    gold = generator(x, y),
                                                    stone = generator(x, y)
                                                                 )
                                   ) for y in range( self.tile_dim[1] )
                       ] for x in range( self.tile_dim[0] )
                     ]

        self.cities = [ city.city( vector3( x + (hts[0]-5) * random.random(),
                                            y + (hts[1]-5) * random.random(),
                                            0.0 ),
                                   out,
                                   area = self.get_area_at( x/ts[0], y/ts[1] ) )
                        for x in range(0, self.window[0], hts[0])
                        for y in range(0, self.window[1], ts[1])
                      ]
                                   

    def draw( self ):
        "Draw the grid as a background for other rendering"
        ts = self.tile_size
        rect = Rect( self.start_rect )
        
        for y in range( self.tile_dim[1] ):
            for x in range( self.tile_dim[0] ):
                area = self.areas[x][y]

                # sum of faction colors scaled by faction control in area
                color = vector3()
                for i in range( global_info.num_factions ):
                    
                    color += (global_info.faction_colors[i] *
                              (area.faction_control[i]/100.0))
                             
                pygame.draw.rect( self.screen, color.raw, rect )
                rect.move_ip( ts[0], 0 )

            rect.move_ip( -ts[0] * self.tile_dim[0] , ts[1] )

        for city in self.cities:

            #draw an outer white band
            pos = Rect( (city.pos.x, city.pos.y), (6,6) )
            pygame.draw.rect( self.screen, (255,255,255), pos )

            #select a ligher version of faction color
            if city.faction_ident == -1:
                color = (0,0,0)
            else:
                color = global_info.faction_colors[ city.faction_ident ]
                color = color + vector3(150, 150, 150)
                color.cut_max(255)
                color = color.raw

            #move the rect inside our outline
            pos.inflate_ip(-2,-2)

            pygame.draw.rect( self.screen, color, pos )


    def get_area_at( self, x, y ):
        return self.areas[x][y]

    def get_random_unclaimed_area( self ):
        while True:
            x = int( random.random() * self.tile_dim[0] )
            y = int( random.random() * self.tile_dim[1] )

            area = self.get_area_at( x, y )
            if area.faction_control == [0] * global_info.num_factions:
                return area

    def get_city_location( self, area ):
        pos = area.pos
        x = int( pos.x / self.ts[0] )
        y = int( pos.y / self.ts[1] )

        print x,y

        index = 2 * self.tile_dim[1] * x + y
        return index

    def linearize_areas( self ):
        return [ self.areas[x][y] for x in range( self.tile_dim[0] )
                                  for y in range( self.tile_dim[1] ) ]

    def linearize_cities( self ):
        return self.cities

    
                       
        

