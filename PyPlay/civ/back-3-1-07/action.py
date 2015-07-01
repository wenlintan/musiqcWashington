import pygame
from pygame.locals import *

import goal, base

class evaluator(base.base):
    "Represents a statement to be evaluated based upon a dict passed later."
    def __init__(self, obj, expr = None, keys = None):
        self.obj = obj
        self.expr = expr
        self.keys = keys

        self.factor = 1.0
        self.constant = 0.0

    def evaluate(self, keys):
        obj = keys[ self.obj ]
        
        if expr is None:
            return obj

        if type(expr) == str:
            value = obj.attr[ self.expr ]
            return value * self.factor + self.constant

        for k,v in self.keys.items():
            if isinstance(v, evaluator):
                self.keys[k] = v(keys)

        return expr( obj, *args )
    __call__ = evaluate

    def __mul__(self, fac):
        self.factor *= fac
        return self

    def __div__(self, fac):
        self.factor /= float(fac)
        return self

    def __add__(self, fac):
        self.constant += fac
        return self

    def __sub__(self, fac):
        self.constant -= fac
        return self

    def __neg__(self):
        self.factor = -self.factor
        return self

class action(base.base):
    "Actions represent a solution to a goal."
    def __init__(self, decisions, elements, arguments, **keys):
        """Arguments: decisions is dictionary of decisions to be preprocessed
                      elements is an dictionary of callable items
                      arguments is an array of the same size as elements
                        each element is an array indicating the key
                        values given as arguments to that element
        """

        self.decidors = decisions
        self.elements = elements
        self.arguments = arguments


        if len(self.elements) != len(self.arguments):
            raise ValueError

        self.length = len( self.elements )
        super(action, self).__init__( keys )

    def __call__( self ):
        "Calling overloaded to call act method."
        return self.act()

    def decide( self ):
        "Make the preliminary independent decisions."
        self.decisions = {}
        for k,v in self.decidors.items():
            self.decisions[ k ] = v()

    def effects( self ):
        "Get the effects that finalizing this action would eventually have."
        for e in self.effects:
            e( self.decisions )
            e.obj.get_changes()

    def act( self ):
        "Default implementation just calls each element in any possible order."

        # build a single array containing all evaluation information
        element_items = self.elements.items()
        unevaluated = [ (element_items[i], self.arguments[i])
                        for i in range( self.length ) ]

        possible_arguments = self.decisions

        #loop until everything evaluated, checking for infinite condition
        last_len = 0
        while len(unevaluated) and len(unevaluated) != last_len:

            last_len = len(unevaluated)
            rebuilt_unevaluated = []
            
            for e in unevaluated:                
                element = e[0]
                arguments = e[1]
                
                can_evaluate = True
                built_arguments = []

                #determine if all necessary arguments have been computed
                #building them as possible
                for a in arguments:

                    try:
                        #attempt to find this argument
                        built_arguments.append( possible_arguments[ a ] )
                    except:
                        #impossible to evaluate this element at this time
                        can_evaluate = False
                    

                if can_evaluate:
                    #evaluate if possible
                    arguments[ element[0] ] = element[1]( *built_args )
                else:
                    #otherwise keep it in the unevaluated list
                    rebuilt_unevaluated.append( e )

            unevaluated = rebuilt_unevaluated



        

        
                    
