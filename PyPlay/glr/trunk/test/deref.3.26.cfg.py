
{% options
	start = S'
	parser = GLR
%}

{% tokens
	S', S, E, V, 'x', '*', '=', $
%}

{% productions
	S'	-> S $
	
	S	-> V '=' E
	S	-> E
	
	E 	-> V
	
	V	-> 'x'
	V	-> '*' E
%}
