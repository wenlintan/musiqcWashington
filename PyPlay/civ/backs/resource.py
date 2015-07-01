import base

class resource(base.base):
    "Represents all the resources used in the simulation"
    
    def __init__( self, **keys ):

        # set initial values
        self.food = 0
        self.wood = 0
        self.gold = 0
        self.stone = 0

        # update based on passed parameter
        super(resource, self).__init__( keys )

    def __add__( self, other ):
        return resource( food = self.food + other.food,
                         wood = self.wood + other.wood,
                         gold = self.gold + other.gold,
                         stone = self.stone + other.stone )

    def __sub__( self, other ):
        return resource( food = self.food - other.food,
                         wood = self.wood - other.wood,
                         gold = self.gold - other.gold,
                         stone = self.stone - other.stone )

    def __mul__( self, factor ):
        return resource( food = self.food * factor,
                         wood = self.wood * factor,
                         gold = self.gold * factor,
                         stone = self.stone * factor )

    def __repr__( self ):
        return "resource( food=%d, wood=%d, gold=%d, stone=%d )" % (
                        self.food, self.wood, self.gold, self.stone )

    def mag( self ):
        return self.food + self.wood + self.gold + self.stone

    def reset( self ):
        self.food = 0
        self.wood = 0
        self.gold = 0
        self.stone = 0

    def rectify( self ):
        """Rectifies resources to integer values."""
        self.food = int(self.food)
        self.wood = int(self.wood)
        self.gold = int(self.gold)
        self.stone = int(self.stone)

        
    
    def calculate_needs( self, population, military, expansion ):
        "Calculate the needs to maintain these values"
        self.food = population
        self.gold = military * 3 + expansion * 2
        self.wood = expansion * 3
        self.stone = expansion
        
