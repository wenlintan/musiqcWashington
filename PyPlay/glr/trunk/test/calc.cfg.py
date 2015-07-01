
class Real:
	def __init__( self, data ):
		self.data = data
		self.value = float(data)

{% tokens
	"[ \t\n][ \t\n]*"

	"\+" (%plus%)
	"-" (%minus%)
	"\*" (%mul%)
	"/" (%div%)

	"([0-9][0-9]*(\.[0-9]*)?|\.[0-9][0-9]*)([eE][+\-]?[0-9][0-9]*)?"(%real%):
		return Real( parsed )
%}

{% productions
	E	->	T(%term%):					return term

	T	->	T(%lhs%) plus F(%rhs%): 	return Real( lhs.value + rhs.value )
	T	->	T(%lhs%) minus F(%rhs%): 	return Real( lhs.value - rhs.value )
	T	->	F(%factor%):				return factor

	F	->	F(%lhs%) mul N(%rhs%): 		return Real( lhs.value * rhs.value )
	F	->	F(%lhs%) div N(%rhs%): 		return Real( lhs.value / rhs.value )
	F	->	N(%number%):				return number
	
	N	-> minus N(%num%): 				return Real( -num.value )
	N	-> real(%real%):				return real
%}

if __name__ == "__main__":
	p = Parser()
	print p.tokenize_and_parse( "6+5" ).value
	print p.tokenize_and_parse( "3*4+1" ).value
	print p.tokenize_and_parse( "3+4*1" ).value
	print p.tokenize_and_parse( "3*4*-5*1+3+4+1*0" ).value
	print p.tokenize_and_parse( "6+-5" ).value

