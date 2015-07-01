
from itertools import chain
from token import *

class RawIterator:
    def __init__( self, iterator, **kwds ):
        self.i = iterator
        for k, v in kwds.items():
            setattr( self, k, v )
        
        self.line = 0
        self.char = 0
        self.data = None

    @staticmethod
    def from_file( filename ):
        f = open( filename )
        if not f.is_open():
            raise IOError( "Could not open file." )

        return RawIterator( f.readlines(), filename = filename )

    @staticmethod
    def from_text( data ):
        return RawIterator( (l+'\n' for l in data.split('\n')) )
    
    max_lookahead = 3
    trigraphs = {
            "??=": '#',     "??/": '\\',    "??'": '^',
            "??(": '[',     "??)": ']',     "??!": '|',
            "??<": '{',     "??>": '}',     "??-": '~'
        }

    def _read_line( self ):
        self.data = self.i.next()
        if not len(self.data) or self.data[-1] != '\n':
            self.data += '\n'
                
        self.line += 1
        self.char = -1

    def next( self ):
        if not self.data:
            self._read_line()
            
        if self.data[:3] in self.trigraphs:
            c = self.trigraphs[ self.data[:3] ]
            self.data = self.data[3:]
            self.char += 3
            return c

        if len(self.data) == 2 and self.data == '\\\n':
            self._read_line()

        c = self.data[0]
        self.data = self.data[1:]
        self.char += 1
        return c

    def __iter__( self ):
        return self
        
class PPLexer:
    def __init__( self, raw_iter ):
        self.f = raw_iter
        self.char = self.f.next()

    digraphs = {
            "<%": '{',      "%>": '}',
            "<:": '[',      ":>": ']',
            "%:": '#',      "%:%:": '##',
            "and": '&&',   "and_eq": '&=',
            "bitor": '|',  "or_eq": '|=',
            "or": '||',     "xor_eq": '^=',
            "xor": '^',     "not": '!',
            "compl": '~',   "not_eq": '!=',
            "bitand": '&'
        }

    pp_op_or_puncs = [
            '{', '}', '[', ']', '#', '##', '(', ')',
            '<:', ':>', '<%', '%>', '%:', '%:%:', ';', ':', '...',
            'new', 'delete', '?', '::', '.', '.*',
            '+', '-', '*', '/', '%', '^', '&', '|', '~',
            '!', '=', '<', '>', '+=', '-=', '*=', '/=', '%=',
            '^=', '&=', '|=', '<<', '>>', '<<=', '>>=', '==', '!=',
            '<=', '>=', '&&', '||', '++', '--', ',', '->*', '->',
            'and', 'and_eq', 'bitand', 'bitor', 'compl', 'not', 'not_eq',
            'or', 'or_eq', 'xor', 'xor_eq'
        ]

    max_pp_op_len = max(len(p) for p in pp_op_or_puncs)
    pp_op_or_punc_inc = [
            [list(p[:l]) for p in pp_op_or_puncs]
            for l in range( max_pp_op_len + 1 )     #Add to trivially terminate
        ]
    starts_pp_op_or_punc = lambda s, c: c in s.pp_op_or_punc_inc[ len(c) ]
    pp_op_or_punc = lambda s, c: "".join(c) in s.pp_op_or_puncs

    digits = '0123456789'
    digit = lambda s, c: c in s.digits

    octal_digits = '01234567'
    octal_digit = lambda s, c: c in s.octal_digits
        
    hexadecimal_digits = '0123456789abcdefABCDEF'
    hexadecimal_digit = lambda s, c: c in s.hexadecimal_digits
        
    nondigits = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'
    nondigit = lambda s, c: c in s.nondigits

    identifier_nondigit = lambda s, c: s.nondigit(c)

    whitespace = lambda s, c: c in " \v\n\t"
    
    
    def next( self ):
        c = self.char
        self.tok_start = self.f.line, self.f.char

        if self.whitespace(c):
            self.char = self.f.next()
            if c == '\n':
                tok_end = self.f.line, self.f.char
                return Newline( self.tok_start, tok_end )

            while self.whitespace(self.char) and self.char != '\n':
                self.char = self.f.next()

            tok_end = self.f.line, self.f.char
            return Whitespace( self.tok_start, tok_end )

        la = [c, self.f.next()]
        if la == ['/', '/']:
            return self.parse_line_comment()

        if la == ['/', '*']:
            return self.parse_block_comment()

        if self.digit(c) or (c == '.' and self.digit(la[1])):
            return self.parse_pp_number( *la )

        if c == '\'' or (c in 'uUL' and la[1] == '\''):
            return self.parse_char_literal( *la )

        if c == '"' or (c in 'uULR' and la[1] == '"'):
            return self.parse_string_literal( *la )

        if la == ['u', '8'] or (c in 'uUL' and la[1] == 'R'):
            la.append( self.f.next() )
            if la[-1] == 'R':
                la.append( self.f.next() )
            if la[-1] == '"':
                return self.parse_string_literal( *la )

        # Parse identifier checks whether it parses an
        # identifier "digraph" and correctly returns this as an op
        if self.identifier_nondigit(c):
            return self.parse_identifier( *la )
            
        if self.starts_pp_op_or_punc([c]):
            return self.parse_pp_op_or_punc( *la )        

        self.char = self.f.next()
        raise ValueError("Could not parse data '%s' into PPToken." % la)

    def __iter__( self ):
        return self

    def _parse_until( self, stop, i, c = None ):
        data = []
        if c is None:
            c = i.next()
        
        while not stop(data, c):
            data.append(c)
            c = i.next()
        return "".join(data), c, i

    def _parse_while( self, cont, i ):
        stop = lambda d, c: not cont(d, c)
        return self._parse_until( stop, i )

    def parse_header_name( self, *lookahead ):
        i = chain( lookahead, self.f )
        enc = i.next()
        if enc not in '<"':
            raise ValueError("Failed to parse header name.")

        stop = lambda d, c: c in ['\n', enc]
        data, c, i = self._parse_until( stop, i )
        if data[-1] == '\n':
            raise ValueError("Failed to parse header name.")

        # Read past closing " or >
        self.char = i.next()
        tok_end = self.f.line, self.f.char
        return PPHeaderName( self.tok_start, tok_end, data )

    def parse_pp_number( self, *lookahead ):
        def stop( data, c ):
            if self.digit(c) or self.identifier_nondigit(c) or c=='.':
                return False
            return not (data and data[-1] in "eE" and c in "+-")

        i = chain( lookahead, self.f )
        data, c, i = self._parse_until( stop, i )

        self.char = c
        tok_end = self.f.line, self.f.char
        return PPNumber( self.tok_start, tok_end, data )

    def _parse_integer( self ):
        accept = '0123456789'
        start = 0

        if len(self.data) > 2 and self.data[:2] in ('0x', '0X'):
            accept = '0123456789abcdefABCDEF'
            start = 2
            
        elif len(self.data) > 1 and self.data[0] == '0':
            accept = '01234567'
            start = 1

        end = start
        while end < len(self.data) and self.data[end] in accept:
            end += 1

        p, d, s = data[:start], data[start:end], data[end:]
        return IntegerLiteral( self.start, self.end, p, d, s ) 

    def _parse_floating( self ):
        stop = lambda d, c: not self.digit(c)
        i = chain( (g for g in data), '\n' )
        frac, c, i = self._parse_until( stop, i )
        if c == '.':
            f2, c, i = self._parse_until( stop, i )
            frac = frac + '.' + f2

        if frac == '.':
            raise ValueError( "Failed to parse floating literal." )

        exp = ""
        if c in 'eE':
            sign = i.next()
            if sign in '+-':
                exp, sign = sign, None
                
            e2, c, i = self_parse_until( stop, i, sign )
            exp = exp + e2

        suffix = ""
        if c in 'flFL':
            suffix, c = c, i.next()

        ud_suffix = str( list(i)[:-1] )
        return FloatingLiteral( frac, exp, suffix, ud_suffix )

    def parse_identifier( self, *lookahead ):
        stop = lambda d,c: not self.digit(c) and not self.identifier_nondigit(c)
        i = chain( lookahead, self.f )
        data, c, i = self._parse_until( stop, i )

        self.char = c
        tok_end = self.f.line, self.f.char

        if data in self.pp_op_or_puncs:
            return self.parse_pp_op_or_punc( *data )
        return Identifier( self.tok_start, tok_end, data )

    def parse_char_literal( self, *lookahead ):
        i = chain( lookahead, self.f )
        ch, enc = i.next(), None
        if ch in "uUL":
            enc = ch
            i.next()

        def stop( data, c ):
            if c not in "'\n":
                return False
            return not (data and data[-1] == '\\' and c == '\'')

        data, c, i = self._parse_until( stop, i )
        self.char = i.next()        # Skip past closing '

        # Parse user defined suffix if it exists
        ud_suffix = None
        if self.identifier_nondigit(self.char):
            ident = self.parse_identifier()
            ud_suffix = ident.data
            
        tok_end = self.f.line, self.f.char
        return CharLiteral( self.tok_start, tok_end, enc, data, ud_suffix )        

    def parse_string_literal( self, *lookahead ):
        i = chain( lookahead, self.f )
        
        ch, enc = i.next(), None
        if ch in "uUL":
            enc = ch
            ch = i.next()

        if ch == '8':
            if enc != 'u':
                raise ValueError("Unknown string prefix.")
            enc = 'u8'
            ch = i.next()
        
        if ch == 'R':
            # FIXME: Parse raw string
            self.char = i.next()

        elif ch == '"':
            def stop( data, c ):
                if c not in "\"\n":
                    return False
                return not (data and data[-1] == '\\' and c == '\"')

            data, c, i = self._parse_until( stop, i )
            self.char = i.next()        # Skip past closing "
            
        else:
            raise ValueError("Failed to parse string.")

        # Parse user defined suffix if it exists
        ud_suffix = None
        if self.identifier_nondigit(self.char):
            ident = self.parse_identifier()
            ud_suffix = ident.data
            
        tok_end = self.f.line, self.f.char
        return StringLiteral( self.tok_start, tok_end, enc, data, ud_suffix )

    def parse_pp_op_or_punc( self, *lookahead ):
        stop = lambda d, c: not self.starts_pp_op_or_punc(list(chain(d,c)))
        i = chain( lookahead, self.f )
        data, c, i = self._parse_until( stop, i )

        self.char = c
        tok_end = self.f.line, self.f.char

        if data in self.digraphs:
            data = self.digraphs[ data ]
        return PPOpOrPunc( self.tok_start, tok_end, data )

    def parse_line_comment( self, *lookahead ):
        stop = lambda d, c: c == '\n'
        i = chain( lookahead, self.f )
        data, c, i = self._parse_until( stop, i )
        
        self.char = '\n'
        tok_end = self.f.line, self.f.char
        return Whitespace( self.tok_start, tok_end )

    def parse_block_comment( self, *lookahead ):
        def stop( data, c ):
            return not (data and data[-1] == '*' and c == '/')
        i = chain( lookahead, self.f )
        data, c, i = self._parse_until( stop, i )
        
        self.char = i.next()
        tok_end = self.f.line, self.f.char
        return Whitespace( self.tok_start, tok_end )
        
