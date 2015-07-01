import pygame
from pygame.locals import *

import random

import base, resource, area, city, person, action, decision


class faction_actions:
    def __init__(self, fac):
        
        self.build_city = lambda reward, resource: action.action(
                            { "to_city" : decision.decision(
                                                 fac.potential_cities,
                                                 "area.potential." + resource,
                                                 decision.decision.maximum ),
                              "from_city" : decision.decision(
                                                 fac.cities,
                                                 "area.potential." + resource,
                                                 decision.decision.minimum )
                            },

                            [ action.evaluator(
                                  "from_city",
                                  city.change,
                                  { "population": action.evaluator(
                                         "from_city", "population") - 10,
                                    "military": action.evaluator(
                                         "from_city", "military") - 5
                                  }
                                ),
                              action.evaluator(
                                  "to_city",
                                  city.change,
                                  { "faction_ident": fac.ident,
                                    "population": 10,
                                    "military": 5
                                  }
                                )
                            ],
                            
                            { "citizen" : lambda city: create_citizen(
                                                                 fac,
                                                                 city ),
                              "move" : lambda obj, city: action.movement(
                                                                 obj,
                                                                 city.pos,
                                                                 reward=reward),
                              "action" : lambda obj, act: obj.give_action( act )
                            },

                            [ ["from_city"], ["citizen", "to_city"],
                              ["citizen", "move"] ]
                          )

    def get( self ):
        return [ self.build_city ]
        

def mag_dict( d ):
    return sum( d.values() )

def add_dict( d1, d2 ):
    pass
    
class faction(base.base):
    "Represents a faction in the simulation"                                           
    def __init__(self, ident, out, **keys):

        self.out = out
        self.ident = ident

        # set initial values
        self.name = ""
        self.cities = []
        self.areas = []
        self.potential_cities = []

        self.actions = []
        self.potential_actions = [ (self.create_citizen,
                                    person.person,
                                    [ city.city ])
                                 ]
        self.goals = {}

        # our resources, just contain sum of cities needs
        self.stockpile = resource.resource()
        self.consumption = resource.resource()
        self.production = resource.resource()
        self.change = resource.resource()

        # population (military and youth are subsets
        self.population = 0
        self.military = 0
        self.youth = 0

        # current expansion term
        self.expansion = 0

        #civilization characteristics [0,100]
        self.morality = 0
        self.nobility = 0
        self.xenophobia = 0
        self.militaristic = 0
        self.expansionism = 0

        # update based on passed parameter
        super(faction, self).__init__( keys )

    def preprocess( self ):
        
        for area in self.areas:
            for city in self.cities:
                dist = area.pos - city.pos
                mini = min( dist, area.faction_distance[ self.ident ] )
                area.faction_distance[ self.ident ] = mini

        for city in self.cities:
            city.preprocess()

            self.population += city.population
            self.military += city.military
            self.youth += city.youth

        #reparse attributes after change
        self.reparse()

    def lock_effects( self ):
        self.prev_attr = self.attr.copy()

        for city in self.cities:
            city.lock_effects()

    def detect_effects( self ):
        self.changes = {}

        for k,v in self.prev_attr:
            if k in self.attr and v != self.attr[k]:
                self.changes[k] = self.attr[k] - v

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

        for city in self.cities:
            city.revert()
        
    def update( self ):
        self.production.reset()
        self.consumption.reset()
        self.stockpile.reset()

        self.population = 0
        self.military = 0
        self.youth = 0
        
        for city in self.cities:
            city.update()
            self.production += city.production
            self.consumption += city.consumption
            self.stockpile += city.stockpile

            self.population += city.population
            self.military += city.military
            self.youth += city.youth

        self.change = self.production - self.consumption

        #reparse attributes after change
        self.reparse()

    
        

    def tick( self ):
        "Perform one tick of the simulation"

        self.out.log("-" * 79)
        self.out.log("Faction: '%s' beginning tick." % self.name)

        # handle our resources
        self.out.log( "Initial Stockpile: %s." % repr(self.stockpile) )

        for city in self.cities:
            city.update()
            city.tick()
        self.update()
        
        self.out.log( "Consumption: %s." % repr(self.consumption) )
        self.out.log( "Production: %s." % repr(self.production) )
        self.out.log( "Final Stockpile: %s." % repr(self.stockpile) )
        

        self.out.log("Faction has completed tick.")
        self.out.log("-" * 79)

        #reparse attributes after change
        self.reparse()

    def process_goals( self ):
        for goal, action in self.goals.items():
            if action is None:

                for action in self.actions:
                    pass

            else:
                action.tick()

    def create_citizen( self, city ):
        citizen = person.person( morality = self.morality +
                                            (rand * (random.random() - 0.5)),

                                 ambition = 5
                                 )

        return citizen


    def define_actions( self ):

        self.lock_effects()
        for person in self.persons:
            person.lock_effects()
            person.complete_goals()

        self.update()
        self.detect_changes()

        for person in self.persons:
            person.revert()
        self.revert()

        new_goals = {}
        for res in ["food", "wood", "gold", "stone"]:
            res_change_goal = 0

            #if we don't have any stockpile attempt to form one
            if self.attr[ "stockpile." + res ] < 1000:
                res_change_goal = 100

            new_goals[ res ] = self.attr[ "change." + res ] - res_change_goal

        for k,v in new_goals.items():
            if k in self.goals:
                #already have a response defined
                continue
            
            for make_act in self.actions:
                act = make_act( standard_reward, k )

                self.lock_effects()
                act.decide()
                act.effects()
                self.detect_effects()

        
