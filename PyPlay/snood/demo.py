

class Animal:
    def talk( self ):
        print "Animal Noise."

class Cat( Animal ):
    def __init__( self, name ):
        self.name = name
        
    def talk( self ):
        print "Meow", self.name
        self.cat = True
        
        return self.name

c = Cat( "Whiskers" )
c.talk()

a = Animal()
a.talk()




