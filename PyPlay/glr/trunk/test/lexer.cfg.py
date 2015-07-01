
class Token:
	pass
If = Token

{%tokens

	[ \t\r]:		pass
	if:				return If
	else:			return Else
	elif:			return Elif
	
%}

{%productions
	if
%}