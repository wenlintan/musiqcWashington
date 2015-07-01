import pygame
from pygame.locals import *

import pickle, random

import faction, action, decision

class genetic:
    def __init__( self, factions ):
        self.factions = factions
        self.scores =  [0] * len( factions )

        self.mutation = 0.05
        self.selection_size = 0.125
        self.length_change = 0.05

        for fac in self.factions:

            size = 2 + (random.random() < (self.length_change*2)) * (random.random() * 4 - 2)
            for i in range( size ):
                fac.actions.append( self.random_action( fac, 2 ) )


    def random_decision( self, fac, force_list = None ):
        "Creates a decision based on a random list in faction."
        #decide which list to make decision from
        decide_list = force_list
        if force_list is None:
            decide_list = fac.get_attr_by_type( list )
            decide_list = self.rand_element( decide_list )

        attr_list = decide_list[0].attr
        attr = self.rand_element( attr_list.keys() )

        #value that we should search for the closest to
        value_random = random.random()
        if   value_random < 0.333: value = decision.minimum
        elif value_random < 0.666: value = decision.maximum
        else:                      value = self.rand_int(-100, 100)

        weight = random.random() * 3.0

        #possible add decisions on another factor from same list
        dec = decision.decision( decide_list, attr, value, weight )
        if random.random() < self.length_change: dec = dec + random_decision( decide_list )
        
        return dec

    def random_act( self, possible, types ):
        """Select a random action from a list of possible and the types
            available for use as parameters."""

        def get_by_type( lst, typ ):
            return [ x for x in lst if x.__class__ == typ ]

        #select a random possible action
        action = self.rand_element( possible.keys() )

        #select caller number from this action's caller type
        act = action[0]
        caller_type = possible[ action ]
        caller = self.rand_element( get_by_type( types, caller_type ) )
        caller = types.index( caller )

        #select random object with right argument type
        args = []
        for arg in action[2]:
            newarg = self.rand_element( get_by_type( types, arg ) )
            args.append( types.index( newarg ) )

        #add the return type for this action to the possible types list
        if action[1] is not None:
            types.append( action[1].__class__ )
            

        return act, [ caller ].extend( args )


    def random_action( self, fac, size ):        
        decidors = list()
        decidors_size = 2 + (random.random() < (self.length_change*2)) * (random.random() * 4 - 2)
        for j in range( decidors_size ):
            decidors.append( self.random_decision( fac ) )

        decisions = dict( [ (i, decidors[i]) for i in range( decidors ) ] )

        action_types = [ fac.__class__ ]
        action_dict = dict([ (f, fac.__class__) for f in fac.possible_actions ])
        
        for e in decidors:
            alist = dict([ (a, e.obj_type.__class__)
                           for a in e.obj_type.possible_actions ])
                      
            action_dict.update( alist )
            action_types.append( e.obj_type.__class__ )

        actions = list(); args = list()
        size = size + (random.random() < (self.length_change*2)) * int(random.random() * 4 - 2)
        size = min( size, 1 )

        for j in range( size ):
            try:
                act, arg = self.random_action( action_dict, action_types )
                actions.append( act )
                args.append( arg )
            except:
                break
            
        act_index = decidors_size
        actions = dict([ (i+act_index, actions[i])
                         for i in range( len(actions) ) ])
                         
        return action.action( decisions, actions, args )

        
        
        
        

    def random_ideal_values( self, fac, current ):
        for k in current.keys():
            current[k] = self.rand_int( -100, 100 )
            
    def randomize( self ):
        for fac in self.factions:
                
            for k in fac.ideal_values.keys():
                fac.ideal_values[k] = random.random() * 200.0 - 100

    def generation( self ):
        self.score()

        size = len( self.factions )
        select = int( len( self.factions ) * self.selection_size )

        sort = [ (self.score[x],x) for x in range( size ) ].sort()
        
        selected = [ self.faction[ sort[x][1] ] for x in range( select ) ]
        scores = [ sort[x][0] for x in range( select ) ]

        sum_scores = sum( scores )
        scores = [ x / sum_scores for x in scores ]

        self.factions = []
        for x in range( size ):
            rand1 = random.random()
            rand2 = random.random()



    def score( self ):
        self.scores = [ fac.population + fac.military
                        for fac in self.factions ]

    def breed( self, fac1, fac2 ):

        #start with first factions values as defaults
        f = faction.faction( **fac1.__dict__ )

        for k in fac.ideal_values.keys():
            if random.random > 0.5:
                fac.ideal_values[k] = fac2.ideal_values[k]

    def mutate( self, fac ):

        for k in fac.ideal_values.keys():
            if random.random > (1-self.mutation):
                fac.ideal_values[k] = random.random() * 200.0 - 100

    def rand_int( self, mini=0, maxi=100 ):
        return int( random.random() * (maxi-mini) + mini )

    def rand_element( self, arr ):
        if len( arr ) == 0:
            raise ValueError
        
        index = int( (random.random()) * len(arr) )
        return arr[ index ]

    def rand_int_if( self, orig, if_number, mini=0, maxi=100 ):
        if random.random() > if_number:
            return orig

        return self.rand_int( mini, maxi )

    def rand_element_if( self, orig, if_number, arr ):
        if len( arr ) == 0:
            raise ValueError
        
        if random.random() > if_number:
            return orig

        return self.rand_element( arr )

    def switch_if( self, orig, if_number, new ):
        if random.random() > if_number:
            return orig

        return new

    def save( self ):
        f = file( ".\info.txt", "w" )
        pickle.dump( self.factions, f )
        f.close()

    def load( self ):
        f = file( ".\info.txt", "r" )
        self.factions = pickle.load( f )
        f.close()
