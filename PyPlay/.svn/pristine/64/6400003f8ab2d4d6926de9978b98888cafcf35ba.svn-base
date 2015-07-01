import pygame
from pygame.locals import *

import math

import base, resource, area, person, output

class city(base.base):
    "Represents a city in the simulation."
    def __init__( self, pos, out, **keys ):

        #simulation important things
        self.out = out
        self.pos = pos
        
        #general information about city
        self.area = None
        self.name = ""
        self.faction_ident = -1

        ################################################################
        #primary qualities modified by simulations
        self.growth_rate = 0.0
        self.work_factor = 1.0

        self.morality = 0
        
        self.population = 0
        self.military = 0
        self.youth = 0

        ################################################################
        #secondary qualities, determined by primaries
        self.controlled_area = 0

        # our resources
        self.stockpile = resource.resource()
        self.consumption = resource.resource()
        self.production = resource.resource()
        self.change = resource.resource()

        self.security = 0
        self.happiness = 0
        self.violence = 0
        self.sexuality = 0
        self.graft = 0

        self.actions = []
        self.possible_actions = {}
        self.possible_actions[ "form_party" ] = [ (self.form_party,
                                                   person.party,
                                                   [ person.person,
                                                     int,
                                                     int ]) ]

        # update based on passed parameter
        super(city, self).__init__( keys )

    def preprocess( self ):
        self.controlled_area = self.population
        self.expansion = self.growth_rate * self.population

        #reparse attributes after change
        self.reparse()

    def lock_effects( self ):
        "Lock effects to detect changes or revert later."
        self.prev_attr = self.attr.copy()
        
    def change( self, **keys ):
        "Set new values to find effect on secondary qualities."
        
        for k,v in keys.items():
            if hasattr( self, k ):

                #update actual value and attr representation
                setattr( self, k, v )
                self.attr[ k ] = v

        #propogate changes
        self.update()

    def revert( self ):
        "Revert to original values before a call to change."
        for k,v in self.prev_attr.items():
            setattr(self, k, v)
            
    def update( self ):
        self.calculate_production()
        self.consumption.calculate_needs( self.population,
                                          self.military,
                                          self.growth_rate )

        #rectify and do final calculations
        self.production.rectify()
        self.consumption.rectify()
        self.change = self.production - self.consumption

        self.security = 300.0 * self.military / float(self.population)
        self.happiness = 0.5 * self.security / float(self.work_factor)

        immorality = 100 - self.morality
        self.violence = immorality * self.security / 100.0
        self.sexuality = immorality - self.violence
        self.graft = self.production.mag() * immorality / 100.0

        #reparse attributes after change
        self.reparse()
        
    def tick( self ):
        self.stockpile += self.production - self.consumption
        self.population = self.population * math.exp( self.growth_rate )

        #reparse attributes after change
        self.reparse()

    def untick( self ):
        self.stockpile -= self.production + self.consumption
        self.population = self.population / math.exp( self.growth_rate )

        #reparse attributes after change
        self.reparse()
        
    def calculate_production( self ):
        if self.area is None:
            self.out.log( "City does not know area.", output.output.ERROR )
            
        frac = self.work_factor * self.controlled_area / float(self.area.area)
        self.production = self.area.potential * frac

    def form_party( self, leader, size, military ):
        self.size -= size
        self.military -= military
        return person.party( leader, size=size, military=military )
        
