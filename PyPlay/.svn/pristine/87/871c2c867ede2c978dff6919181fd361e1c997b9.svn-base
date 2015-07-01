import sys, random


class evaluate_error(Exception):
    def __init__( self, desc ):
        self.desc = desc

class interpreter:

    ax = 0
    bx = 1
    cx = 2
    dx = 3
    
    num_registers = 4
    memory_space = 1000


    class instruction:
        ident = 0
        def __init__( self, rep, num_args, fn, full_rep = None ):
            
            self.ident = interpreter.instruction.ident
            self.rep = rep
            
            self.full_rep = full_rep
            self.num_args = num_args
            self.fn = fn

            interpreter.instruction.ident += 1

        def rep( self, *args ):
            if self.full_rep is None:
                return self.rep
            return self.full_rep % args

    class literal:
        def __init__( self, num ):
            self.num = num

        def get( self ):
            return self.num

        def set( self, val ):
            raise evaluate_error( "Can't assign to literal" )

        def __repr__( self ):
            return str(self.num)
        

    class register:
        registers = []
        
        def __init__( self, num ):
            self.num = num

        def get( self ):
            return interpreter.register.registers[ self.num  ]

        def set( self, val ):
            interpreter.register.registers[ self.num ] = val

        def __repr__( self ):
            return "reg%s(%s)" % (self.num, self.get())

    class pointer:
        data = []

        def __init__( self, num ):
            self.num = num

        def get( self ):
            return interpreter.pointer.data[ self.num ]

        def set( self, val ):
            interpreter.pointer.data[ self.num ] = val

        def __repr__( self ):
            return "ptr%s(%s)" % (self.num, self.get())
    
    def __init__( self ):

        ins = interpreter.instruction
        mov = ins( "mov", 2, self._mov )
        inc = ins( "inc", 1, self.umath_op( lambda x: x+1, "inc" ) )
        dec = ins( "dec", 1, self.umath_op( lambda x: x-1, "dec" ) )
        neg = ins( "neg", 1, self.umath_op( lambda x: -x, "neg" ) )
        add = ins( "add", 2, self.math_op( lambda x,y: x+y, "add" ) )
        sub = ins( "sub", 2, self.math_op( lambda x,y: x-y, "sub" ) )
        mul = ins( "mul", 2, self.math_op( lambda x,y: x*y, "mul" ) )
        div = ins( "div", 2, self.math_op( lambda x,y: x/y, "div" ) )
        jeq = ins( "jeq", 3, self.comp_op( lambda x,y: x==y, "jeq" ) )
        jne = ins( "jne", 3, self.comp_op( lambda x,y: x!=y, "jne" ) )
        jlt = ins( "jlt", 3, self.comp_op( lambda x,y: x<y, "jlt" ) )
        jgt = ins( "jgt", 3, self.comp_op( lambda x,y: x>y, "jgt" ) )
        ret = ins( "ret", 1, self._ret )
        

        self.raw_ins = [mov, inc, dec, add, sub, mul, div, jeq, jne, jlt, jgt, ret]

        #define two separate dictionaries for different mappings
        self.read_ins = dict( [(x.rep,x.ident) for x in self.raw_ins] )
        self.instructions = dict( [(x.ident,x) for x in self.raw_ins] )

        self.functions = []

    def evaluate( self, code, args, max_instructions = -1 ):

        # create our stack, empty
        self.stack = []

        # create registers and organize some references to them
        self.registers = [0] * interpreter.num_registers

        self.ax = interpreter.register( interpreter.ax )
        self.bx = interpreter.register( interpreter.bx )
        self.cx = interpreter.register( interpreter.cx )
        self.dx = interpreter.register( interpreter.dx )

        interpreter.register.registers = self.registers

        # create the data/executable memory and initialize
        self.data = [0] * interpreter.memory_space
        for i in range( len(code) ):
            self.data[i] = code[i]

            if type( code[i] ) is str:
                self.data[i] = self.read_ins[ code[i] ]

        start_args = len(code)
        for i in range( len(code), len(code)+len(args) ):
            self.data[i] = args[ i - len(code) ]

            if type( args[ i - len(code) ] ) is str:
                self.data[i] = self.read_ins[ args[ i - len(code) ] ]
                
        self.registers[ interpreter.ax ] = start_args
        interpreter.pointer.data = self.data

        self.ip = 0
        self.returned = False

        while not self.returned:

            opcode = self.getinc_ip()
            if opcode not in self.instructions.keys():
                raise evaluate_error( "Invalid opcode: %s" % opcode )
            
            instruct = self.instructions[ opcode ]
            
            for i in range( instruct.num_args ):
                self.push( self.getinc_ip() )

            instruct.fn()

        return self.registers[0]

    def inc_ip( self ):
        self.ip = (self.ip+1) % interpreter.memory_space

    def getinc_ip( self ):
        data = self.data[ self.ip ]
        self.inc_ip()
        return data

    def rand_instruction( self ):
        
        op = random.choice( self.raw_ins )
        
        ins = [op]
        for x in range( op.num_args ):
            args.extend( self.rand_argument() )
        return ins

    def rand_argument( self ):

        arg_type = random.random()
        if arg_type > 0.5:
            return [ random.randint( -2*interpreter.num_registers, -1 ) ]
        
        if arg_type > 0.2:
            return [ random.randint( 1, interpreter.memory_space ) ]

        return [ 0, random.randint( -1000, 1000 ) ]
            

    def push( self, elem ):
        if elem == 0:

            #is a literal
            elem = self.getinc_ip()
            self.stack.append( interpreter.literal(elem) )      

        else:

            #is a pointer to a memory location
            
            if elem > 0:
                #just a direct literal pointer( offset by one to avoid 0 )
                if elem > interpreter.memory_space:
                    raise evaluate_error( "Invalid memory pointer: %s" % elem )
                
                self.stack.append( interpreter.pointer(elem-1) )

            elif elem >= -interpreter.num_registers:
                #is the number of a register
                regnum = (-elem) - 1
                self.stack.append( interpreter.register(regnum) )

            elif elem >= -interpreter.num_registers * 2:
                #is a pointer to the address in a register
                regnum = (-elem) - interpreter.num_registers -1
                ptr = interpreter.pointer( self.registers[regnum] )
                self.stack.append( ptr )

            else:
                #nothing to do
                raise evaluate_error( "Invalid argument type: %s" % elem )



    def pop( self ):

        if not self.stack:
            raise evaluate_error( "Pop from empty stack" )

        return self.stack.pop()
        
        

    def _mov( self ):
        to = self.pop()
        from_val = self.pop()

        print "mov %s, %s;" % (to, from_val)

        to.set( from_val.get() )

    def umath_op( self, lam, name ):
        def fun():
            one = self.pop()

            print (name + " %s;") % (one)
            self.ax.set( lam( one.get() ) )
        return fun
    
    def math_op( self, lam, name ):
        def fun():
            two = self.pop()
            one = self.pop()

            print (name + " %s, %s;") % (one, two)
            self.ax.set( lam( one.get(), two.get() ) )
        return fun

    def comp_op( self, lam, name ):
        def fun():
            goto = self.pop()
            two = self.pop()
            one = self.pop()

            print (name + " %s, %s, %s;") % (one, two, goto)
            if lam( one.get(), two.get() ):
                self.ip = goto.get()
        return fun

    def _ret( self ):
        ret_code = self.pop()

        print "ret %s;" % ret_code
        
        self.ax.set( ret_code.get() )
        self.returned = True
        

        
