import pygame
from pygame.locals import *

import goal, action, base

class person_actions:
    def __init__( self, pers ):
        self.pers = pers
        
class person(base.base):
    "Represents a single actor in the simulation."
    def __init__( self, **keys ):

        # set initial values
        self.morality = 0
        self.ambition = 0

        self.goals = []
        self.actions = person_actions( self )
        self.potential_actions = []

        # update based on passed parameter
        super(person, self).__init__( keys )

    def meaning_of_life_shit( self ):
        self.goals.append( goal.personal() )

    def give_act( self, act ):
        self.potential_actions.append( act )

class party(base.base):
    "Represents a group of people, normally assigned a single task."
    def __init__( self, leader, **keys ):

        self.leader = leader
        
        # set initial values
        self.deviance = 0
        self.size = 0

        # update based on passed parameter
        super(person, self).__init__( keys )
        

    
