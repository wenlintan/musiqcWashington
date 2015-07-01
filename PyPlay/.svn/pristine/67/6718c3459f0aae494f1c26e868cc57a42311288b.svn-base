
class Token:
	type = None
	
class
{% tokens

identifier = [a-zA-Z_][a-zA-Z0-9_]*
literal = '[!'\n]*'

%}

{% productions

sections -> sections section
sections ->

section -> '{%' 'options' options '%}'
section -> '{%' 'tokens' tokens '%}'
section -> '{%' 'productions' productions '%}'

options -> options option
options ->
option -> identifier '=' value

tokens -> tokens token
tokens ->
token -> identifier '=' 

productions -> productions production
productions ->
production -> identifier '->' values

values -> values value
values ->
value -> identifier
value -> literal

%}