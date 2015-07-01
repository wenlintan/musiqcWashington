import pygame
from pygame.locals import *

import goal, city, base
from vector3 import *
        
class person(base.base):
    "Represents a single actor in the simulation."
    def __init__( self, **keys ):

        self.pos = vector3()

        # set initial values
        self.faction_ident = 0
        self.morality = 0
        self.ambition = 0

        self.goals = []

        self.actions = []
        self.possible_actions = {}
        self.possible_actions[ "move" ] = [ (self.move,
                                             None,
                                             [ vector3 ]) ]
                                   
        self.actions = []

        # update based on passed parameter
        super(person, self).__init__( keys )

    def meaning_of_life_shit( self ):
        self.goals.append( goal.personal() )

    def give_act( self, act ):
        self.potential_actions.append( act )

    def move( self, pos ):
        self.actions.append( movement( self, pos ) )



class party(person):
    "Represents a group of people, normally assigned a single task."
    def __init__( self, leader, **keys ):

        self.leader = leader
        self.pos = vector3()
        
        # set initial values
        self.deviance = 0
        
        self.size = 0
        self.military = 0

        # update based on passed parameter
        super(party, self).__init__( keys )

        self.possible_actions[ "build_city" ] = [ (self.build_city,
                                                   None,
                                                   [ faction.faction,
                                                     city.city ]) ]

    def build_city( self, faction, city ):
        self.actions.append( build_city( faction, self, city ) )
        
class movement( object ):
    def __init__( self, obj, pos ):
        self.obj = obj
        self.end = pos
        
        self.dir = self.end - self.obj.pos
        self.dir = self.dir.norm()

    def tick( self ):
        self.obj.pos += self.dir

        to = self.end - self.obj.pos
        if to.mag() < self.dir.mag():
            self.obj.pos = self.end
            return True

        return False
        

    def end( self ):
        self.revert = self.obj.pos
        self.obj.pos = self.end

    def revert( self ):
        self.obj.pos = self.revert

class build_city( object ):
    ticks_to_build = 10
    
    def __init__( self, faction_ident, party, city ):
        self.faction = faction_ident
        self.party = party
        self.city = city

        self.ticks = 0

    def tick( self ):
        if (self.city.faction_ident != 0 or
            (self.party.pos - self.city.pos).mag() < 1):
            #someone already controls this city, oy too far away
            return True

        self.ticks += 1
        if self.ticks < ticks_to_build:
            return False
        
        faction.cities.append( self.city )
        self.city.faction_ident = self.faction
        self.city.population = self.party.size
        self.city.military = self.party.military
        return True

    def end( self ):
        self.revert = self.ticks
        self.ticks = ticks_to_build
        self.tick()

    def revert( self ):
        self.ticks = self.revert
    
