import pygame
from pygame.locals import *

import base, resource

class area(base.base):
    "Represents an area of land with set resource potentials."
    def __init__( self, pos, size, **keys ):

        # set initial values
        self.pos = pos
        self.size = size
        self.area = size[0] * size[1]
        
        self.potential = resource.resource()
        self.used = resource.resource()

        # per faction factors [0,100]
        self.faction_control = [0] * global_info.num_factions
        self.faction_importance = [0] * global_info.num_factions

        #distance to faction territory
        self.faction_distance = [0] * global_info.num_factions

        # update based on passed parameter
        super(area, self).__init__( keys )

    def description( self ):
        return "Food: %d(%d), Wood: %d(%d), Gold: %d(%d), Stone: %d(%d)" % (
                    self.used.food, self.potential.food,
                    self.used.wood, self.potential.wood,
                    self.used.gold, self.potential.good,
                    self.used.stone, self.potential.stone )

        
