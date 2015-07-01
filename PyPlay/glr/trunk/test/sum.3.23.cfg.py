
{% options
	start = E
	parser = GLR
%}

{% tokens
	E, T, x, '+'
%}

{% productions	
	E 	-> T + E
		-> T
	
	T	-> x
%}
