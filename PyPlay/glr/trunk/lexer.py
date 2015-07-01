
from itertools import takewhile, chain
from collections import defaultdict
import pdb

class _NamedEmptyObject:
	def __init__( self, name ):
		self.name = name
	def __str__( self ):
		return ""
	def __repr__( self ):
		return self.name

class CFGDFAState:
	epsilon = _NamedEmptyObject( "eps" )
	bol = _NamedEmptyObject( "bol" )
	eol = _NamedEmptyObject( "eol" )
	eof = _NamedEmptyObject( "eof" )

	accepts = False
	guid = 0
	
	def __init__( self ):
		self.edges = {}
		self.false_edge = defaultdict( lambda: False )
		self.guid = CFGDFAState.guid
		CFGDFAState.guid += 1
		
	def __repr__( self ):
		edges = ', '.join([ 
			"{0}: {1}".format( repr(ch), edge.guid ) 
			for ch, edge in self.edges.items() 
			])
		return "CFGDFAState({0}({1}), {{{2}}})".format( 
			self.guid,  self.accepts, edges )
		
	def __lt__( self, rhs ):
		return self.guid < rhs.guid
		
class CFGNFAState:
	epsilon = CFGDFAState.epsilon
	bol = CFGDFAState.bol
	eol = CFGDFAState.eol
	eof = CFGDFAState.eof

	accepts = False
	guid = 0
	
	def __init__( self ):
		self.edges = defaultdict(set)
		self.guid = CFGNFAState.guid
		CFGNFAState.guid += 1
		
	def step( self, ch, state_set ):
		for s in self.edges[ch]:
			state_set.add( s )
			
	def epsilon_closure( self, state_set = None ):
		if state_set is None:
			state_set = set((self,))
		
		l = lambda x: x not in state_set
		for s in filter( l, self.edges[ self.epsilon ] ):
			state_set.add( s )	
			s.epsilon_closure( state_set )
		return state_set
		
	def no_real_edges( self ):
		_ = self.edges[ self.epsilon ]
		return len( self.edges.keys() ) > 1

	def __repr__( self ):
		edges = ', '.join([ 
			"{0}: ({1})".format( repr(ch), 
				', '.join( '{0}'.format(d.guid) for d in edge ) ) 
			for ch, edge in self.edges.items()
			])
		return "CFGNFAState({0}, {{{1}}})".format( self.guid, edges )
		
class CFGLexerSyntaxError( Exception ):
	def __init__( self, msg ):
		self.msg = msg
		
class CFGToken:
	NoToken = object()

	@staticmethod
	def tokens_from_dict( d ):
		return [ CFGToken( expr, tok ) for expr, tok in d.items() ]

	@staticmethod
	def signal_token( token, gen = False ):
		return CFGToken( "", token, gen )

	def __init__( self, expr, token, token_gen = False ):
		self.expr = expr
		if not hasattr( token, "__call__" ):
			token = self._generate_callback( token )
		if token_gen:
			self.token = self._wrap_gen_token( token )
		else:
			self.token = self._wrap_token( token )

	def set_priority( self, priority ):
		self.priority = priority

	def __lt__( self, rhs ):
		return self.priority < rhs.priority

	def __call__( self, parsed, start, end ):
		return self.token( parsed, start, end )
	
	def _generate_callback( self, token ):
		def cb( data, start, end ):
			return token
		return cb

	def _wrap_gen_token( self, tok ):
		def cb( parsed, start, end ):
			result = tok( parsed, start, end )
			for r in result:
				if r is not self.NoToken:
					yield r
		return cb

	def _wrap_token( self, tok ):
		def cb( parsed, start, end ):
			result = tok( parsed, start, end )
			if result is not self.NoToken:
				yield result
		return cb

class CFGLexer:
	NoToken = _NamedEmptyObject("NoToken")
	def __init__( self, tokens, error_token = None, eof_token = None ):
		self.error_token, self.eof_token = error_token, eof_token
		self.error_token = CFGToken.signal_token( self.error_token )
		if self.eof_token:
			self.eof_token = CFGToken.signal_token( self.eof_token )


		if isinstance( tokens, dict ):
			tokens = CFGToken.tokens_from_dict( tokens )

		self.states = []
		for i, tok in enumerate(tokens):
			tok.set_priority( i )
			base, end = self._parse_regular_expr( tok.expr, tok )
			self.states.append( base )

		self.base_state = CFGNFAState()
		for state in self.states:
			self.base_state.edges[ state.epsilon ].add( state )
		self._convert_to_dfa()

	def _wrap_data( self, it, pos = (1, 0) ):
		line, col = pos
		yield CFGDFAState.bol, line, col
		for ch in it:
			if ch == '\n':
				yield CFGDFAState.eol, line, col
				yield '\n', line, col
				yield CFGDFAState.bol, line+1, 0
				line, col = line+1, 0
			else:
				yield ch, line, col
				col += 1
		yield CFGDFAState.eol, line, col
		yield CFGDFAState.eof, line, col

	def match( self, data ):
		it = iter(data)
		chars = self._wrap_data( it )
		ch, line, col = chars.next()
		try:
			state, parsed = self.base_state, ""
			while True:
				parsed += str(ch)
				state = state.edges[ ch ]
				ch, line, col = chars.next()
		except KeyError:
			if ch is not CFGNFAState.eof:
				return None
		if state.accepts:
			for r in state.token( parsed, (1,0), (line, col) ):
				return r
		return None

	def tokenize( self, data ):
		for i in self._tokenize( data ):
			for t in i:
				yield t

	def _tokenize( self, data ):
		it = self._wrap_data( iter(data) ) 
		chars, error = it, ""
		while True:
			try:
				last_accept, state, parsed = None, self.base_state, ""
				ch, line, col = chars.next()
				stack, stack_len = [], 0
				start = line, col
				while True:
					parsed += str(ch)
					stack.append( (ch, line, col) )

					if not state.false_edge[ ch ]:
						stack_len = len(stack)

					state = state.edges[ ch ]
					ch, line, col = chars.next()
					if state.accepts:
						last_accept, last_parsed = state, parsed
						end = line, col
						last_stack = stack_len
			except KeyError: 
				if stack[0][0] is CFGDFAState.eof:
					if error:
						yield self.error_token( error, error_start, start )
					if self.eof_token:
						yield self.eof_token( '', start, start )
					return
				if last_accept is not None:
					if error: 
						yield self.error_token( error, error_start, start )
						error = ""
					yield last_accept.token( last_parsed, start, end )
					# Add unparsed data back into stream
					chars = chain( stack[ last_stack: ], it )
				else:
					if not error and str( stack[0][0] ):
						error_start = start
					error += str( stack[0][0] )
					chars = chain( stack[1:], it ) 

	def _convert_to_dfa( self ):
		dfa_map = {}
		dfa_base = CFGDFAState()
		closure = self.base_state.epsilon_closure()
		if any( s.accepts for s in closure ):
			raise CFGLexerSyntaxError( "Base state accepts." )

		new_states = { frozenset(closure): dfa_base }
		self.base_state = dfa_base
		
		while new_states:
			states, dfa_state = new_states.popitem()
			dfa_map[ states ] = dfa_state
			
			edges = [set(s.edges.keys()) for s in states ]
			all_edges = set()
			for e in edges:
				all_edges = all_edges.union( e )
				
			all_edges.discard( CFGNFAState.epsilon )
			for ch in all_edges:
				temp_states = set()
				for s in states:
					s.step( ch, temp_states )
					
				eps_states = set()
				for s in temp_states:
					eps_states.add( s )
					s.epsilon_closure( eps_states )
				if not eps_states:
					continue
					
				eps_states = frozenset( eps_states )
				if eps_states in dfa_map:
					dfa_state.edges[ ch ] = dfa_map[ eps_states ]
				elif eps_states in new_states:
					dfa_state.edges[ ch ] = new_states[ eps_states ]
					
				else:
					new_dfa = CFGDFAState()
					tokens = sorted( s.token for s in eps_states if s.accepts )
					if tokens:
						new_dfa.accepts, new_dfa.token = True, tokens[0]
						
					dfa_state.edges[ ch ] = new_dfa
					new_states[ eps_states ] = new_dfa
	
		self.states = dfa_map.values()
		for state in self.states:
			if CFGNFAState.bol not in state.edges:
				state.edges[ CFGNFAState.bol ] = state
				state.false_edge[ CFGNFAState.bol ] = True
			if CFGNFAState.eol not in state.edges:
				state.edges[ CFGNFAState.eol ] = state
				state.false_edge[ CFGNFAState.eol ] = True
			elif state.accepts and '\n' not in state.edges:
				raise CFGLexerSyntaxError( "No \\n after $." )

	def _parse_regular_expr( self, expr, token=None, state=None, depth=0 ):
		i = iter( expr )
		base_state, prev_state, options = state, None, []
		if state is None:
			base_state = state = CFGNFAState()
		
		try:
			ch = i.next()
			while True:
				if ch == '.':		
					prev_state, state = state, self._parse_dot( state )
				elif ch == '[':	
					prev_state, state = state, self._parse_class( state, i )
				elif ch == '(':		
					# Recurse to parse subgroup
					base, end = self._parse_regular_expr( 
						i, state=state, depth=depth+1 )
					prev_state, state = state, end
				elif ch == ')':
					# Break loop without making state accept
					if not depth:
						raise CFGLexerSyntaxError( ") without matching (." )
					break
				elif ch == '|':
					# Make new isolated state and store this location
					# to be connected correctly later
					state, prev_state = CFGNFAState(), state
					options.append( (state, prev_state) )
					prev_state = None
				elif ch == '*':	
					# Add epsilon edges to form a loop
					prev_state.edges[ state.epsilon ].add( state )
					state.edges[ state.epsilon ].add( prev_state )
					# Add extra state connected to epsilon to prevent
					# unwanted looping
					state, prev_state = CFGNFAState(), state
					prev_state.edges[ state.epsilon ].add( state )
				elif ch == '?':		
					prev_state.edges[ state.epsilon ].add( state )
				else:
					if ch in "^$":
						ch = [CFGNFAState.bol, CFGNFAState.eol][ ch == '$' ]
					if ch == '\\':
						ch = self._escape( i.next() )
					new_state = CFGNFAState()
					state.edges[ch].add( new_state )
					prev_state, state = state, new_state
				ch = i.next()
		except StopIteration:
			if depth:
				raise CFGLexerSyntaxError( "Unclosed (." )
			state.accepts = True
			state.token = token
		while options:
			opt, opt_prev = options.pop()
			base_state.edges[ state.epsilon ].add( opt )
			opt_prev.edges[ state.epsilon ].add( state )
		return base_state, state
		
	escape_map = {"n":"\n", "r":"\r", "t":"\t", "v":"\v"}
	def _escape( self, ch ):
		if ch in self.escape_map:
			return self.escape_map[ ch ]
		return ch

	dot_accepts = [ chr(i) for i in range(256) if chr(i) not in "\n" ]
	def _parse_dot( self, state ):
		new_state = CFGNFAState()
		for ch in self.dot_accepts:
			state.edges[ ch ].add( new_state )
		return new_state

	def _parse_class( self, state, i ):
		new_state = CFGNFAState()
		l = lambda ch: ch != ']'
		last, edges, invert = None, [], False
		
		for ch in takewhile(l, i):
			if ch == '^' and last is None:
				invert = True
			elif ch == '-' and last is not None:
				try:
					next = i.next()
					for j in range( ord(last), ord(next)+1 ):
						edges.append( chr(j) )
				except StopIteration:
					raise CFGLexerSyntaxError( "Bad char class" )
			elif ch == '\\':
				try:
					last = self._escape( i.next() )
					edges.append( last )
				except StopIteration:
					raise CFGLexerSyntaxError( "Bad char class" )
			else:
				last = ch
				edges.append( last )
				
		if invert:
			allchr = set( chr(i) for i in range(256) ) 
			edges = list( allchr.difference( set(edges) ) )
		for ch in edges:
			state.edges[ ch ].add( new_state )
		return new_state

