
class Token(object):
    def __init__( self, start, end ):
        self.start, self.end = start, end

    def __eq__( self, rhs ):
        return self.start == rhs.start and self.end == rhs.end

class Newline(Token):
    def __init__( self, start, end ):
        super(Newline, self).__init__(start, end)

class Whitespace(Token):
    def __init__( self, start, end ):
        super(Whitespace, self).__init__(start, end)

class PPNumber(Token):
    def __init__( self, start, end, data ):
        super(PPNumber, self).__init__(start, end)
        self.data = data    

class PPHeaderName(Token):
    def __init__( self, start, end, data ):
        super(PPHeaderName, self).__init__(start, end)
        self.data = data

class PPOpOrPunc(Token):
    def __init__( self, start, end, data ):
        super(PPOpOrPunc, self).__init__(start, end)
        self.data = data

class Identifier(Token):
    def __init__( self, start, end, data ):
        super(Identifier, self).__init__(start, end)
        self.data = data

class Keyword(Identifier):
    pass

class Literal(Token):
    pass

class IntegerLiteral(Literal):
    DECIMAL = 10
    OCTAL = 8
    HEXADECIMAL = 16

    prefix_map = {
            "": DECIMAL,
            "0": OCTAL,
            "0x": HEXADECIMAL,
            "0X": HEXADECIMAL
        }

    UNSIGNED = 1
    LONG = 2
    LONGLONG = 4
    
    def __init__( self, start, end, prefix, data, suffix, ud_suffix ):
        super(IntegerLiteral, self).__init__(start, end)
        self.base = self.prefix_map[ prefix ]
        self.data = data

        self.type = 0
        if 'u' in suffix:
            self.type |= UNSIGNED

        if 'll' in suffix or 'LL' in suffix:
            self.type |= self.LONGLONG

        elif 'l' in suffix or 'L' in suffix:
            self.type |= self.LONG

        self.ud_suffix = ud_suffix

    def value( self ):
        return int( self.data, self.base )
        
class FloatingLiteral(Literal):
    FLOAT = 0
    DOUBLE = 1
    LONGDOUBLE = 2

    suffix_map = {
            "": FLOAT,
            'd': DOUBLE,
            'D': DOUBLE,
            'l': LONGDOUBLE,
            'L': LONGDOUBLE
        }
    
    def __init__( self, start, end, frac, exp, suffix, ud_suffix ):
        super(FloatingLiteral, self).__init__(start, end)
        self.data = frac
        self.exp = exp
        
        self.type = self.suffix_map[ self.suffix ]
        self.ud_suffix = ud_suffix

    def value( self ):
        return float( self.data ) * 10**int( self.exp )

    def integral( self ):
        return int( self.data.split('.')[0] )

class CharLiteral(Literal):
    def __init__( self, start, end, prefix, data, ud_suffix ):
        super(CharLiteral, self).__init__(start, end)

    def value( self ):
        return ord( data[0] )

class StringLiteral(Literal):
    def __init__( self, start, end, prefix, data, ud_suffix ):
        super(StringLiteral, self).__init__(start, end)

        
