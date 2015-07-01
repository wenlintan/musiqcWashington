
class Integer:
	def __init__( self, data ):
		self.data = data
		self.value = int(data)
		
class Real:
	def __init__( self, data ):
		self.data = data
		self.value = float(data)
		
class Operator:
	def __new__( cls, data ):
		return self.operators[ data ]
Operator.plus = Operator['+'] = object()
Operator.minus = Operator['-'] = object()
Operator.mul = Operator['*'] = object()
Operator.div = Operator['/'] = object()

{% tokens
	+: Operator
	-: Operator
	*: Operator
	/: Operator
	
	[1-9][0-9]*:	Integer
	[1-9][0-9]*.[0-9]*[eE][+-]?[0-9]*:	Real
%}

{% productions
	E	->	F
	F	->	F Operator.mul T
	F	->	F Operator.div T
	
	T	->	T Operator.plus N
	T	->	T Operator.minus N
	
	N	-> Operator.minus N
	N	-> Integer
	N	-> Real
%}