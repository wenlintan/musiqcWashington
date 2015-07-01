
class base(object):
    def __init__( self, keys = None ):
        "Perform standard initiation on simulation objects."

        #initialize any specified parameters if they exist in the simulation
        if keys is not None:
            for k in keys.keys():
                if k in self.__dict__:
                    self.__dict__[k] = keys[k]

        #create the attr dictionary to easily refer to any necessary attributes
        self.attr = {}
        for k,v in self.__dict__.items():
            self.recurse_attr( k, v )

    def reparse( self ):
        for k,v in self.__dict__.items():
            self.recurse_attr( k, v )

    def recurse_attr( self, k, v ):
        if k == "attr":
            #uhh, okay computer
            return
        
        try:
            #allow derived classes to opt out of member listing
            if not v.recurse_attributes:
                return
        except AttributeError:
            #if recurse_attributes isn't defined continue
            pass
        
        try:
            for k2, v2 in v.__dict__.items():
                self.recurse_attr( k + "." + k2, v2 )
        except AttributeError:
            self.attr[ k ] = v
            
    def get_attr_by_type( self, typ ):
        return [ i for i in self.attr.values() if type(i) == typ ]
