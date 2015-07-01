VARIABLE = 0
CONSTANT = 1
OPERATOR = 2
FUNCTION = 3
TEXTTYPE = 4        #used as generic during parser
UNSPECIF = 5

class Atom:
    type = UNSPECIF
    def __init__(self, typ = UNSPECIF):
	self.type = typ

class Constant(Atom):
    def __init__(self, val):
	self.type = CONSTANT
	self.val = val

class Variable(Atom):
    def __init__(self, name, val):
	self.type = VARIABLE
	self.name = name
	self.val = val


class Operator(Atom):

    oparray = {'+':Operator.add, '-':Operator.subtract, '*':Operator.mult,
               '/':Operator.div, '^':Operator.power,    '=':Operator.equals }

    def __init__(self, opname):
	self.type = OPERATOR
	self.opname = opname

    def run(self, latom, ratom):
	try:
	    op = self.oparray[self.name]
	    return op(self, latom, ratom)
	except KeyError:
	    raise ValueError, "undefined operator"

    def __str__(self):
        return ' %s' % (self.opname)
		
    def add(l, r):
	return l.val + r.val

    def subtract(l, r):
	return l.val - r.val

    def mult(l, r):
	return l.val * r.val

    def div(l, r):
	return l.val / r.val

    def power(l, r):
	return pow(l.val,  r.val)

    def equals(l, r):
        l.value = r

class Function(Atom):
    funcarray = {}
    def __init__(self, name, *args):
        self.type = FUNCTION
        self.name = name
        self.arglist = args

    def run(self):
        try:
            func = funcarray[name]
            func(arglist)
        except KeyError:
            raise ValueError, "undefined function"

    def __str__(self):
        return ' %s(%s)' % (self.name, self.arglist)
        
    
class Expression(Atom):
    atoms = []
    order = '^*/+-='

    def __init__(self):
        self.type = EXPRESSION

    def add(self, atom):
	self.atoms.append(atom)

    def run(self):
	accumulator = []
	atomlist = self.atoms
	skip = False
	
	for atom in atomlist:
            if atom.type == FUNCTION or atom.type == EXPRESSION
                index = atomlist.index(atom)
                atomlist[index] = Constant(atom.run())
        
	for op in self.order:
	    for atom in atomlist:
                if skip:
                    skip = False
                    continue
                
		if atom.type == OPERATOR and atom.name == op:
                    index = atomlist.index(atom)
                    if index == 0:
                        res = atom.run(None, atomlist[index+1])
                    elif index == len(atomlist)-1:
                        res = atom.run(atomlist[index-1], None)
                    else:
                        res = atom.run(atomlist[index-1], atomlist[index+1])
                        
                    #remove last item, used in operator
		    accumulator = accumulator[:-1]
		    accumulator.append(Constant(res))
		    skip = True #skip next it was already used here
		else:
		    accumulator.append(atom)
			
		atomlist = accumulator

	if len(accumulator) > 1 or not accumulator[0].type ==CONSTANT:
            raise ValueError, "expression parse failed"

        return accumulator[0].val

    def __str__(self):
        return ' (%s)' % (self.atoms)

class Parser:
    def __init__(self):
        self.variables = {}
        self.lastexpression = None

    def __str__(self):
        if self.lastexpression is None:
            return ''
        return self.lastexpression.__str__()
    
    def parse(string):
        accum       = []
        typ         = UNSPECIF
        curexp      = [Expression()]
        possfunc    = None
        funclist    = []

        def isNumeric(char):
            return char in '0123456789'
        def typecheck(newtype):
            if not typ == newtype:
                self.build(typ, accum, curexp[len(curexp)-1])
                del accum[:]

        
        for char in string:
            if isNumeric(char) or char == '.':
                typecheck(CONSTANT)
                typ = CONSTANT
                accum.append(char)

            elif char in '=+-/*^':
                typecheck(OPERATOR)
                typ = OPERATOR

                accum.append(char)

            elif char == '(':
                if typ == TEXTTYPE:
                    possfunc = accum
                    del accum[:]
                else:
                    typecheck(EXPRESSION)

                curexp.append(Expression())

            elif char == ')':
                build(typ, accum, curexp[len(curexp)-1])
                curexp.pop(len(curexp)-1)
                if not possfunc is None:
                    typ = UNSPECIF
                    self.build(FUNCTION, accum, curexp[len(curexp)-1],
                               possfunc, funclist)
                else
                    typ = EXPRESSION

            elif char == ',':
                build(typ, accum, curexp[len(curexp)-1])
                funclist.append(curexp.pop(len(curexp)-1))
                curexp.append(Expression())

            else:
                typecheck(TEXTTYPE)
                typ = TEXTTYPE

                accum.append(char)
                
    def build(typ, buf, expr, func = None, funclist = None):
        if typ == CONSTANT:
            if '.' in buf:
                expr.add(Constant(float(str(buf))))
            else:
                expr.add(Constant(int(str(buf))))

        elif typ == VARIABLE:
            try:
                expr.add(self.variables[str(buf)])
            except KeyError:
                expr.add(Variable(str(buf), None))

        elif typ == OPERATOR:
            expr.add(Operator(str(buf)))

        
                        

                
