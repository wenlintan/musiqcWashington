import pygame
from pygame.locals import *

import base

class goal(base.base):
    "A goal defines an ideal state for some object."
    def __init__(self, obj, **keys):

        self.obj = obj
        
        # set initial values
        self.importance = 0
        self.reward = {}

        # update based on passed parameter
        super(goal, self).__init__( keys )


class movement(goal):
    def __init__(self, obj, pos, **keys):
        self.goal = pos

        super(movement_goal, self).__init__( obj, keys )

class resource(goal):
    def __init__(self, obj, resource, value, **keys):
        self.resource = resource
        self.value = value

        super(resource_goal, self).__init__( obj, keys )

class personal(goal):
    def __init__(self, obj, attr, value, **keys):
        self.attr = attr
        self.value = value

        self.reward = {}

        super(personal_goal, self).__init__( obj, keys )

    def is_satisfied(self, reward = None):
        if reward is None:
            reward = self.reward

        if reward[attr] > self.value:
            return True

        return False

