
import pdb
from itertools import chain

from glr import CFGParser, CFGNonterminal, CFGTerminal
from actions import *
from lexer import CFGLexer, CFGToken

class Token(object):
	def __init__( self, data, start, end ):
		self.data, self.start, self.end = data, start, end

	def __str__( self ):
		return "(" + self.__class__.__name__ + ", " + repr(self.data) + ")"

	def __repr__( self ):
		return str( self )

	def __eq__( self, rhs ):
		return isinstance( rhs, self.__class__ ) and self.data == rhs.data

	def __ne__( self, rhs ):
		return not self == rhs 

	def python( self ):
		return ( self.python_token, self.data, self.start, self.end )

	def output( self, indents, previous = None ):
		white_space = ''
		if isinstance( previous, (Newline, Indent, Dedent) ):
			white_space = indents[-1]
		return white_space + self.data, indents, self

class RealToken( Token ):
	def output( self, indents, previous = None ):
		white_space = ''
		if isinstance( previous, Newline ):
			white_space = indents[-1]
			if previous.paren:
				white_space += '\t'
		if isinstance( previous, (Indent, Dedent) ):
			white_space = indents[-1]
		elif isinstance( previous, (Identifier, Number) ):
			white_space = ' '
		elif isinstance( previous, Operator ) and previous.data == ',':
			white_space = ' '
		return white_space + self.data, indents, self

class Identifier( RealToken ):
	python_token = 1
	def __init__( self, data, start = (1,0), end = (1,0) ):
		super( Identifier, self ).__init__( data, start, end )
		self.ident = data
	
class Number( RealToken ):
	python_token = 2
	def __init__( self, data, start = (1,0), end = (1,0) ):
		super( Number, self ).__init__( data, start, end )
		self.value = float(data)

class Literal( RealToken ):
	python_token = 3
	def __init__( self, data, start = (1,0), end = (1,0) ):
		super( Literal, self ).__init__( data, start, end )
		self.value = data[1:-1]

class Newline( Token ):
	python_token = 4
	@staticmethod
	def empty( data, start, end ):
		return Newline( data, start, end, True )

	def __init__( self, data, start = (1,0), end = (1,0), 
			empty = False, paren = False ):
		super( Newline, self ).__init__( data, start, end )
		self.empty, self.paren = empty, paren
		if empty or paren:
			self.python_token = 54

class Indent( Token ):
	python_token = 5
	tab_width = 4
	def __init__( self, data = '\t', start = (1,0), end = (1,0) ):
		super( Indent, self ).__init__( data, start, end )

	def indent_length( self, data = None ):
		l = 0
		if data is None: data = self.data
		for ch in data:
			if ch == ' ':		l += 1
			elif ch == '\t':	l = (l/self.tab_width+1) * self.tab_width
		return l

	def output( self, indents, previous = None ):
		data = self.data
		while self.indent_length( data ) <= self.indent_length( indents[-1] ):
			data = '\t' + data
		indents.append( data )
		return '', indents, self

	def __eq__( self, rhs ):
		return isinstance( rhs, self.__class__ )

class Dedent( Token ):
	python_token = 6
	def __init__( self, data = '', start = (1,0), end = (1,0) ):
		super( Dedent, self ).__init__( data, start, end )
	
	def output( self, indents, previous = None ):
		indents.pop()
		return '', indents, self

	def __eq__( self, rhs ):
		return isinstance( rhs, self.__class__ )

class Operator( Token ):
	python_token = 51
	def __init__( self, data, start = (1,0), end = (1,0) ):
		super( Operator, self ).__init__( data, start, end )
		self.op = data

class Comment( Token ):
	python_token = 53
	def __init__( self, data, start = (1,0), end = (1,0) ):
		super( Comment, self ).__init__( data, start, end )

class EOF( Token ):
	python_token = 0
	def __init__( self, data, start = (1,0), end = (1,0) ):
		super( EOF, self ).__init__( data, start, end )

class Code:
	def __init__( self, tokens = None ):
		self.tokens = tokens
		if self.tokens is None:
			self.tokens = []

	def append( self, line ):
		self.tokens.extend( line )
		return self

	def add_block( self, indent, code, dedent ):
		self.tokens.append( indent )
		self.tokens.extend( code.tokens )
		self.tokens.append( dedent )
		return self

class Regex:
	def __init__( self, regex, name, code ):
		self.regex, self.name, self.code = regex, name, code

class TokenSection:
	@staticmethod
	def create( start, ident, regexes, end ):
		return TokenSection( regexes )

	def __init__( self, regexes ):
		self.regexes = regexes

	def build( self ):
		if not self.regexes:
			return

		term = CFGTerminal
		self.terminals = [ r.name.data for r in self.regexes if r.name.data ]
		self.terminals = dict( (t, term(t)) for t in self.terminals )

		tokens = [ 
			CFGToken( r.regex.value, r.name.data )
			for r in self.regexes
			]

		self.lexer = CFGLexer( tokens )
		return self.terminals.values()

	def lexer_tokens( self ):
		yield "\tdef _wrap( self, fn ):\n"
		yield "\t\tdef cb( p, s, e ):\n"
		yield "\t\t\ttok = fn(p, s, e)\n"
		yield "\t\t\tif tok is not self.NoToken:\n"
		yield "\t\t\t\tyield tok\n"
		yield "\t\treturn cb\n\t\n"

		yield "\tdef _build_lexer( self ):\n"

		guid_map = {}
		states = self.lexer.states
		for i, s in enumerate(states):
			guid_map[ s.guid ] = i

		yield "\t\tself.states = [CFGDFAState() for i in range({0})]\n" \
			.format( len(states) )
		yield "\t\tself.base_state = self.states[{0}]\n" \
			.format( guid_map[ self.lexer.base_state.guid ] )
		yield '\t\t\n'

		yield "\t\tself.error_token = self._wrap("
		yield "lambda p, s, e:self.NoToken )\n"
		yield "\t\tself.eof_token = self._wrap("
		yield "lambda p, s, e:self.NoToken)\n"
		yield "\t\tself.NoToken = object()\n"
		yield "\t\t\n"

		yield "\t\tbol = CFGDFAState.bol\n"
		yield "\t\teol = CFGDFAState.eol\n"
		yield "\t\t\n"

		yield "\t\tself.terminals = (\n"
		ts = self.terminals.keys()
		t = ( ', '.join( t for t in ts[i:i+4] )
				for i in range( 0, len(self.terminals), 4 ) )
		t = ', \n'.join( t )
		yield "\t\t\t{0}\n\t\t) = CFGTerminal.create(\n".format( t )
		t = ( ', '.join( '"{0}"'.format( t ) 
				for t in ts[i:i+4] )
				for i in range( 0, len(self.terminals), 4 ) )
		t = ', \n'.join( t )
		yield "{0} )\n".format( t )
		yield "\t\t\n"

		for t in self.terminals.values():
			yield "\t\t{0}.glr_identifier = {1}\n" \
					.format( t.identifier, t.glr_identifier )
		yield "\t\t\n"

		for i, s in enumerate(states):
			if s.accepts:
				tname = s.token( '', None, None ).next()
				yield "\t\tself.states[{0}].accepts = True\n".format( i )
				if tname:
					yield "\t\ttoken = self._wrap("
					yield "{0}.data_wrapper(self._token_{0}))\n" \
							.format( tname ) 
				else:
					yield "\t\ttoken = self._wrap("
					yield "lambda p, s, e: self.NoToken)\n"
				yield "\t\tself.states[{0}].token = token\n".format( i )
			for ch, other in s.edges.items():
				oi = guid_map[ other.guid ]
				yield "\t\tself.states[{0}].edges[{1}] = self.states[{2}]\n" \
						.format( i, repr(ch), guid_map[ other.guid ] )
			for ch, val in s.false_edge.items():
				yield "\t\tself.states[{0}].false_edge[{1}] = {2}\n" \
						.format( i, repr(ch), val )
			yield '\t\t\n'

		for r in self.regexes:
			if not r.name.data:
				continue
			yield "\tdef _token_{0}( self, parsed, start, end ):\n" \
					.format( r.name.data )
			indent, previous = ['\t\t'], Newline('\n')
			for t in r.code.tokens:
				data, indent, previous = t.output( indent, previous )
				yield data
			if r.code.tokens:
				yield "\n"
			else:
				yield "\t\treturn None\n"
			yield "\t\n"
		
class Product:
	def __init__( self, ident, name ):
		self.ident, self.name = ident, name

class Production:
	@staticmethod
	def create( nonterm, produces, products, code ):
		return Production( nonterm, products, code )

	def __init__( self, nonterm, products, code ):
		self.nonterm, self.code = nonterm, code
		self.products = list( Product( i, n ) for i, n in products )

		for i, p in enumerate(self.products):
			if not p.name.data:
				p.name = Identifier( '_' * (i+1) )

class ProductionSection:
	@staticmethod
	def create( start, ident, productions, end ):
		return ProductionSection( productions )

	def __init__( self, productions ):
		self.productions = productions

	def build( self, terminals ):
		if not self.productions:
			return

		nonterm = CFGNonterminal
		self.nonterminals = set( p.nonterm.data for p in self.productions )
		self.nonterminals = dict( (p, nonterm(p)) for p in self.nonterminals )
		
		allthethings = self.nonterminals.copy()
		allthethings.update( dict( (t.identifier, t) for t in terminals ) )

		for p in self.productions:
			res = "_".join( i.ident.data for i in p.products )
			p.name = "_reduce_{0}_to_{1}".format( p.nonterm.data, res )
			nonterm = self.nonterminals[ p.nonterm.data ]
			products = tuple( allthethings[ i.ident.data ] for i in p.products )
			nonterm.production( p.name, *products )

		goal = self.nonterminals[ self.productions[0].nonterm.data ]
		self.terminals = terminals
		self.nonterminals = self.nonterminals.values()
		self.parser = CFGParser( goal, self.terminals, self.nonterminals,
				goal_action = "identity")

	def parser_tokens( self ):
		yield "\tdef _build_parser( self ):\n"
		yield "\t\tself.table = [[None]*{0}]*{1}\n".format(
			len( self.parser.table[0] ), len( self.parser.table ) )
		yield "\t\ta = CFGAction.Accept\n"
		yield "\t\tg = CFGGotoAction\n"
		yield "\t\ts = CFGShiftAction\n"
		yield "\t\tr = CFGReduceAction\n"
		yield "\t\tself.identity = lambda x:x\n"
		yield "\t\tCFGTerminal.EOF = CFGTerminal('$')\n"
		yield "\t\tCFGTerminal.EOF.glr_identifier = {0}\n" \
				.format( CFGTerminal.EOF.glr_identifier )

		yield "\t\tself.nonterminals = (\n"
		ts = self.nonterminals
		s = self.parser.start
		s.identifier = "start"
		ts.append( s )
		t = ( ', '.join( t.identifier for t in ts[i:i+4] )
				for i in range( 0, len(self.nonterminals), 4 ) )
		t = ', \n'.join( t )
		yield "\t\t\t{0}\n\t\t) = CFGNonterminal.create(\n".format( t )
		t = ( ', '.join( '"{0}"'.format( t.identifier ) 
				for t in ts[i:i+4] )
				for i in range( 0, len(self.nonterminals), 4 ) )
		t = ', \n'.join( t )
		yield "{0} )\n".format( t )
		yield "\t\t\n"
		
		for t in self.nonterminals:
			yield "\t\t{0}.glr_identifier = {1}\n" \
					.format( t.identifier, t.glr_identifier )
		yield "\t\t\n"

		goto = lambda s: "g( {0} )".format( s.state )
		shift = lambda s: "s( {0} )".format( s.state )
		red = lambda s: "r( {0}, {1}, self.{2} )" \
				.format( s.nonterminal.identifier, s.nargs, s.fn )

		typemap = {
			CFGGotoAction: goto,
			CFGShiftAction: shift,
			CFGReduceAction: red,
			CFGAction: lambda s: "a"
			}

		for (i, line) in enumerate(self.parser.table):

			yield "\t\tself.table[{0}] = [\n\t\t\t".format( i )
			for (j, e) in enumerate(line):
				if e.__class__ not in typemap:
					yield "None"
				else:
					yield typemap[ e.__class__ ]( e )
				if j+1 != len(line):	yield ","
				if j < len(self.parser.terminals):
					yield "\t# {0}".format( 
							self.parser.terminals[j].identifier )
				else:
					l = len(self.parser.terminals)
					nt = self.parser.nonterminals[j-l]
					yield "\t# {0}".format( nt )
				yield "\n\t\t\t"
			yield "]\n\t\t\n"

		yield "\t\n"
		for p in self.productions:
			yield "\tdef {0}( self, ".format( p.name )
			yield ", ".join( i.name.data for i in p.products )
			yield "):\n"
			indent, previous = ['\t\t'], Newline('\n')
			for t in p.code.tokens:
				data, indent, previous = t.output( indent, previous )
				yield data
			if p.code.tokens:
				yield "\n"
			else:
				yield "\t\treturn None\n"
			yield "\t\n"


class File:
	def __init__( self, code ):
		self.items = [ code ]

	def append( self, section, code ):
		self.items.extend( (section, code) )
		return self

class CFGFileParser:
	def __init__( self ):
		self._build_parser()
		self.lexer = CFGLexer( self.tokens, 
			eof_token = self.eof.data_wrapper(EOF) )
		self.parser = CFGParser( 
			self.goal, self.terminals, self.nonterminals )
		self.reset()

	def _build_parser( self ):
		self.terminals = ( start_section, end_section,
			tokens_id, productions_id,
			start_name, end_name, produces, colon,
			newline, indent, dedent, operator, comment, identifier,
			literal, number, eof ) = (
			CFGTerminal.create( "start_section", "end_section",
					"tokens_id", "productions_id",
					"start_name", "end_name", "produces", 
					"colon", "newline", "indent", "dedent",
					"operator", "comment", "identifier", "literal", "number",
					"eof" ) )
		for t in self.terminals:
			setattr( self, t.identifier, t )

		make_tuple = lambda *args: tuple(args)

		self.tokens = []
		self.tokens.append(CFGToken(r"{%", start_section))
		self.tokens.append(CFGToken(r"%}", end_section))
		self.tokens.append(CFGToken(r"tokens", 
			tokens_id.data_wrapper(Identifier)))
		self.tokens.append(CFGToken(r"productions", 
			productions_id.data_wrapper(Identifier)))

		self.tokens.append(CFGToken(r"\(%", start_name))
		self.tokens.append(CFGToken(r"%\)", end_name))
		self.tokens.append(CFGToken(r"->", produces))
		self.tokens.append(CFGToken(r":", 
			colon.data_wrapper(Operator)))

		operators = [
			",", ";", "@", 
			"+", "-", "\\*", "/", "//", "!", "\\|", "&",
			"<<", ">>", "<", ">", "=", "\\.",
			"%", "`", "~", "\\^"
			]
		for o in operators:
			self.tokens.append(CFGToken(o, operator.data_wrapper(Operator)))

		assign_operators = [
			"+=", "-=", "\\*=", "/=", "//=",
			"!=", "\\|=", "&=", "<=", ">=", "==", "%=",
			"<<=", ">>=" ]
		for o in assign_operators:
			self.tokens.append(CFGToken(o, operator.data_wrapper(Operator)))
		
		paren_operators = [ "\(", "\[", "{", "\)", "\]", "}" ]
		for p in paren_operators[:3]:
			self.tokens.append(CFGToken(p, self._paren_open))
		for p in paren_operators[3:]:
			self.tokens.append(CFGToken(p, self._paren_close))

		self.tokens.append(CFGToken(r"[a-zA-Z_][a-zA-Z0-9_]*",
			identifier.data_wrapper( Identifier )))
		self.tokens.append(CFGToken(
			r"([0-9][0-9]*(\.[0-9]*)?|\.[0-9][0-9]*)([eE][+-]?[0-9][0-9]*)?",
			number.data_wrapper( Number )))
		
		self.tokens.append(CFGToken(r'"([^\\"\n]*(\\.)?)*"', 
			literal.data_wrapper( Literal )))
		self.tokens.append(CFGToken(r"'([^\\'\n]*(\\.)?)*'", 
			literal.data_wrapper( Literal )))

		self.tokens.append(CFGToken(r'r"([^"\n]*(\\")?)*"', 
			literal.data_wrapper( Literal )))
		self.tokens.append(CFGToken(r"r'([^'\n]*(\\')?)*'", 
			literal.data_wrapper( Literal )))
		
		self.tokens.append(CFGToken(
			r'"""([^"]*("|"")?)*"""', 
			literal.data_wrapper( Literal )))
		self.tokens.append(CFGToken(
			r"'''([^']*('|'')?)*'''", 
			literal.data_wrapper( Literal )))
	
		self.tokens.append(CFGToken(r"^[ \t]*\n", self._newline_handler(True))) 
		self.tokens.append(CFGToken(r"^[ \t]*", self._indent_handler, True))
		self.tokens.append(CFGToken(r"\n", self._newline_handler(False)))
		
		self.tokens.append(CFGToken(r"[ \t\r]", CFGToken.NoToken))
		self.tokens.append(CFGToken(r"\\\n^", CFGToken.NoToken))

		self.tokens.append(CFGToken(r"^[ \t]*#[^\n]*\n",
			self._comment_line_handler, True))
		self.tokens.append(CFGToken(r"#[^\n]*", 
			comment.data_wrapper( Comment )))

		self.nonterminals = ( goal, cfg_file, section, 
			code, code_line, code_lines, code_bits,
			naming, regexes, products, productions,
			regex, production ) = ( 
			CFGNonterminal.create(
				"goal", "cfg_file", "section", 
				"code", "code_line", "code_lines", "code_bits",
				"naming", "regexes", "products", "productions",
				"regex", "production"
				) )
		for t in self.nonterminals:
			setattr( self, t.identifier, t )

		make_list = lambda *args: list(args)
		def append( l, i ): l.append(i); return l
		def append_tuple( l, *a ): l.append( tuple(a) ); return l

		first = lambda a, *args: a
		second = lambda a, b, *args: b
		third = lambda a, b, c, *args: c
		fourth = lambda a, b, c, d, *args: d

		goal.production( first, cfg_file, eof )
		cfg_file.production( File.append, cfg_file, section, code_lines )
		cfg_file.production( File, code_lines )

		code_toks = [ operator, identifier, number, literal, colon,
			tokens_id, productions_id ]
		for t in code_toks:
			code_bits.production( append, code_bits, t )
			code_bits.production( make_list, t )

		code_line.production( append, code_bits, newline )
		code_line.production( lambda i: [], newline )

		code_lines.production( Code.append, code_lines, code_line )
		code_lines.production( Code.add_block, 
			code_lines, indent, code_lines, dedent )
		code_lines.production( lambda: Code() )

		code.production( lambda _, c, __: Code(c), colon, code_bits, newline )
		code.production( fourth, colon, newline, indent, code_lines, dedent )
		code.production( lambda n: Code(), newline )

		section.production( TokenSection.create, 
			start_section, tokens_id, regexes, end_section )
		section.production( ProductionSection.create, 
			start_section, productions_id, productions, end_section )

		naming.production( second, start_name, identifier, end_name )
		naming.production( lambda: Identifier("", None, None) )

		regex.production( Regex, literal, naming, code )
		regexes.production( append, regexes, regex )
		for white in [ newline, indent, dedent ]:
			regexes.production( first, regexes, white )
		regexes.production( lambda: [] )

		products.production( append_tuple, products, identifier, naming )
		products.production( lambda: [] )

		production.production( Production.create, 
			identifier, produces, products, code )
		productions.production( append, productions, production )
		for white in [ newline, indent, dedent ]:
			productions.production( first, productions, white )
		productions.production( lambda: [] )

	def _paren_open( self, parsed, start, end ):
		self.paren_level += 1
		data = Operator(parsed, start, end)
		return self.operator.with_data(data)

	def _paren_close( self, parsed, start, end ):
		self.paren_level -= 1
		data = Operator(parsed, start, end)
		return self.operator.with_data(data)

	def _indent_handler( self, parsed, start, end ):
		indent = 0
		for ch in parsed:
			if ch == ' ':		indent += 1
			elif ch == '\t':	indent = (indent/4 +1) * 4

		line, col = start
		if self.paren_level == 0:
			if indent > self.indent_levels[-1]:
				self.indent_levels.append( indent )
				data = Indent( parsed, start, end )
				yield self.indent.with_data( data )
			while indent < self.indent_levels[-1]:
				self.indent_levels.pop()
				data = Dedent( '', end, end )
				yield self.dedent.with_data( data )
	
	def _newline_handler( self, empty ):
		def cb( parsed, start, end ):
			line, col = start
			for ch in parsed[:-1]:
				col += 1
			paren = self.paren_level != 0
			data = Newline( '\n', (line, col), (line, col+1), empty, paren )
			return self.newline.with_data( data )
		return cb

	def _comment_line_handler( self, parsed, start, end ):
		line, col = start
		index = parsed.index( '#' )
		line, col = line, col+index
		end = (line, col+len(parsed[index:-1]))
		data = Comment( parsed[index:-1], (line, col), end )
		yield self.comment.with_data( data )

		line, col = end
		data = Newline( '\n', end, (line, col+1), True )
		yield self.newline.with_data( data )
	
	def reset( self ):
		self.paren_level = 0
		self.indent_levels = [0]

	def tokenize( self, data, reset = True ):
		if reset:
			self.reset()
		for tok in self.lexer.tokenize( data ):
			yield tok

	def tokenize_nt( self, data, reset = True ):
		for t in self.tokenize( data, reset ):
			yield t.data

	def python_tokenize( self, data, reset = True ):
		for t in self.tokenize( data, reset ):
			yield t.data.python()

	def _ifind( self, it, val ):
		v = it.next()
		while val != v:
			v = it.next()
		return v, it

	def _indent_level( self, it, include_below = False ):
		depth = 0
		while depth >= 0:
			t = it.next()
			if t == Indent():	depth += 1
			elif t == Dedent():	depth -= 1
			if include_below or depth == 0:
				yield t

	def _get_file_tokens( self, filename ):
		f = file( filename, 'r' )
		return self.tokenize_nt( chain.from_iterable( f ) )

	def _get_class_tokens( self, filename, clsname, include_header = False ):
		tokens = self._get_file_tokens( filename )
		n = Identifier('')
		while n != Identifier( clsname ):
			cls, tokens = self._ifind( tokens, Identifier('class') )
			n = tokens.next()

		if include_header:
			yield cls
			yield n
		while n != Indent():
			n = tokens.next()
			if include_header:
				yield n

		for t in self._indent_level( tokens, True ):
			yield t

	def _get_fn_tokens( self, filename, clsname, fnname, 
			args = False, header = False ):
		tokens = self._get_class_tokens( filename, clsname )
		n = Identifier( '' )
		while n != Identifier( fnname ):
			d, tokens = self._ifind( tokens, Identifier( 'def' ) )
			n = tokens.next()

		if header:
			yield d
			yield n
		while n != Indent():
			n = tokens.next()
			if args:
				yield n

		for t in self._indent_level( tokens, True ):
			yield t

	def _intro( self ):
		yield "\n\n" + "#"*70 + '\n'
		yield "# Begin automatically generated code\n"
		yield "#"*70 + '\n'
		yield "from collections import defaultdict\n"
		yield "from itertools import chain\n"

	def _parser_header( self ):
		yield "class Parser:\n"
		yield "\tdef __init__( self ):\n"
		yield "\t\tself._build_lexer()\n"
		yield "\t\tself._build_parser()\n"
		yield "\t\n"
		yield "\tdef tokenize_and_parse( self, input ):\n"
		yield "\t\treturn self.parse( self.tokenize( input ) )\n"
		yield "\t\n"

	def _fn_header( self, name ):
		yield "\tdef {0}".format( name )

	def _extro( self ):
		yield "#"*70 + '\n'
		yield "# End automatically generated code\n"
		yield "#"*70 + '\n\n\n'

	def parse( self, filename ):
		cfi = chain.from_iterable

		f = file( filename, 'r' )
		tokens = self.tokenize( cfi( f ) )
		cfg_file = self.parser.parse( tokens )
		f.close()

		tokens, prods = None, None
		for i in cfg_file.items:
			if isinstance( i, TokenSection ):		tokens = i
			if isinstance( i, ProductionSection ):	prods = i

		if tokens is None or prods is None:
			return

		terminals = tokens.build()
		prods.build( terminals )

		out = chain( 
			(t for t in cfg_file.items[0].tokens),
			self.tokenize_nt( cfi(self._intro()) ),
			self._get_file_tokens( 'actions.py' ),
			self._get_class_tokens( 'glr.py', 'CFGNonterminal', True ),
			self._get_class_tokens( 'glr.py', 'CFGTerminal', True ),
			self._get_class_tokens( 'lexer.py', '_NamedEmptyObject', True ),
			self._get_class_tokens( 'lexer.py', 'CFGDFAState', True ),
			self.tokenize_nt( cfi(self._parser_header()), False ),
			self.tokenize_nt( cfi(self._fn_header( "parse" )), False ),
			self._get_fn_tokens( 'glr.py', 'CFGParser', 'parse', 
				args = True ),
			self.tokenize_nt( cfi(self._fn_header( "_parse" )), False ),
			self._get_fn_tokens( 'glr.py', 'CFGParser', '_parse', 
				args = True ),
			self.tokenize_nt( cfi(self._fn_header( "tokenize" )), False ),
			self._get_fn_tokens( 'lexer.py', 'CFGLexer', 'tokenize', 
				args = True ),
			self.tokenize_nt( cfi(self._fn_header( "_tokenize" )), False ),
			self._get_fn_tokens( 'lexer.py', 'CFGLexer', '_tokenize', 
				args = True ),
			self.tokenize_nt( cfi(self._fn_header( "_wrap_data" )), False ),
			self._get_fn_tokens( 'lexer.py', 'CFGLexer', '_wrap_data', 
				args = True ),
			self.tokenize_nt( cfi(tokens.lexer_tokens()), False ),
			self.tokenize_nt( cfi(prods.parser_tokens()), False ),
			self.tokenize_nt( cfi(self._extro()), False ),
			(t for t in cfg_file.items[-1].tokens)
			)

		indents, previous = [''], None
		f = file( 'output.py', 'w' )
		for t in out:
			data, indents, previous = t.output( indents, previous )
			f.write( data )

		return cfg_file

	def output( self ):
		pass

if __name__ == "__main__":
	parser = CFGFileParser( )
	cfg_file = parser.parse( 'test/calc.cfg.py' ) 
	#pdb.set_trace()

