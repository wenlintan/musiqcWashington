
from itertools import chain, takewhile
from collections import defaultdict
import pdb

from lexer import *
from actions import *
	
class CFGTerminal:
	nullable = False
	terminal = True

	@staticmethod
	def create( *ids ):
		return map( CFGTerminal, ids )

	def __init__( self, identifier, glr_id = 0, data=None ):
		self.identifier = identifier
		self.glr_identifier = glr_id
		self.data = data
		if not self.data:
			self.data = self
		self.first = set( (self,) )
		
	def __repr__( self ):
		if self.data is not self:
			return "'" + self.identifier + "(" + str(self.data) + ")'"
		return "'" + self.identifier + "'"
	
	def with_data( self, data ):
		return CFGTerminal( self.identifier, self.glr_identifier, data )

	def data_wrapper( self, fn ):
		def wrapper( data, start, end ):
			return self.with_data( fn(data, start, end) )
		return wrapper

CFGTerminal.epsilon = CFGTerminal( "eps" )
CFGTerminal.epsilon.nullable = True
CFGTerminal.EOF = CFGTerminal( "$" )
	
class CFGNonterminal:
	nullable = False
	terminal = False

	@staticmethod
	def create( *ids ):
		return map( CFGNonterminal, ids )

	def __init__( self, identifier ):
		self.identifier = identifier
		self.productions = []
		self.first = set()
		
	def compute_first( self ):
		changed = False
		for production in self.productions: 
			for i in production:
				if i.first.difference( self.first ):
					self.first = self.first.union( i.first )
					changed = True
				if not i.nullable:
					break
			if not self.nullable and all( i.nullable for i in production ):
				self.nullable = True
				changed = True
		return changed
	
	def _compute_first( self, updated ):
		pass

	def production( self, reduce_action, *production ):
		if not production:
			self.nullable = True
		production = CFGProduction( self, reduce_action, *production )
		self.productions.append( production )
		return self
		
	def __repr__( self ):
		return self.identifier

class CFGStartNonterminal( CFGNonterminal ):
	def __init__( self, start ):
		super( self, CFGStartNonterminal ).__init__( "<start>" )
		self.start = start
		self.production( lambda i: i, start, CFGTerminal.EOF )

	def compute_first( self ):
		pass

class CFGProduction:
	def __init__( self, nonterminal, reduce_action, *production ):
		#if not production:
		#	production = ( CFGTerminal.epsilon, )
		self.production = production

		self.action = reduce_action
		self.nonterminal = nonterminal
		self.items = {}
		
	def __iter__( self ):
		return iter( self.production )
		
	def __getitem__( self, i ):
		return self.production[ i ]
		
	def __getslice( self, i, j ):
		return self.production[ i: j ]
		
	def __len__( self ):
		return len( self.production )
		
	def item( self, lookahead ):
		if lookahead in self.items:
			return self.items[ lookahead ]
		self.items[ lookahead ] = CFGItem( self, 0, lookahead )
		return self.items[ lookahead ]

	def __repr__( self ):
		prod = " ".join( str(i) for i in self.production )
		return "%s -> %s" % ( str(self.nonterminal), prod )
		
class CFGItem:
	def __init__( self, production, cursor, lookahead ):
		self.production = production
		self.cursor = cursor
		self.lookahead = lookahead
		
		self.advanced = None
		self.reduce = cursor == len( self.production )

		self.head = None
		if not self.reduce:
			self.head = self.production[ self.cursor ]
		self.lookahead_set = self._lookahead()

	def _lookahead( self ):
		if self.reduce or self.head.terminal:
			return set()
		rest = chain( self.production[self.cursor+1:], (self.lookahead,) )
		term, lookahead = rest.next(), set()
		while term.nullable:
			term, lookahead = rest.next(), lookahead.union( term.first )
		return lookahead.union( term.first )

	def lookahead_items( self ):
		if self.reduce or self.head.terminal:
			return []

		return ( p.item(la) 
			for p in self.head.productions 
			for la in self.lookahead_set)
		
	def closure( self, items = None ):
		if items is None:
			items = set( (self,) )

		new_items, items = list(items), set()
		while new_items:
			item = new_items.pop()
			if item not in items:
				items.add( item )
				new_items.extend( item.lookahead_items() )
		return items
		
	def advance( self ):
		if self.advanced is not None:
			return self.advanced
		c = self.cursor+1 
		self.advanced = CFGItem( self.production, c, self.lookahead )
		return self.advanced

	def __repr__( self ):
		preprod  = " ".join( str(i) for i in self.production[:self.cursor] )
		postprod = " ".join( str(i) for i in self.production[self.cursor:] )
		return "(%s -> %s.%s, %s)" % (
			str(self.production.nonterminal), 
			preprod, postprod, str(self.lookahead) )

class CFGState:
	def __init__( self, identifier, items ):
		self.identifier = identifier
		self.items = items
		self.edges = {}
		
	def __repr__( self ):
		return repr( self.items )
		
class CFGParser:
	def __init__( self, start, terminals, nonterminals, goal_action = None ):
		self.terminals = list(terminals)
		self.nonterminals = list(nonterminals)
		
		self.start = CFGNonterminal( "<start>" )
		if goal_action is None:
			goal_action = lambda x: x
		self.start.production( goal_action, start, CFGTerminal.EOF )
		
		self.nonterminals.append( self.start )
		self.terminals.append( CFGTerminal.EOF )

		for i, v in enumerate( chain( self.terminals, self.nonterminals ) ):
			v.glr_identifier = i
		
		# Compute first sets
		while any( nt.compute_first() for nt in self.nonterminals ):
			pass

		self._build_table()
			
	def _build_table( self ):
		ident = 0
		states = {}
		
		start_item = self.start.productions[0].item( CFGTerminal.EOF )
		start_items = tuple( start_item.closure() )
		self.base_state = CFGState( ident, start_items )
		new_states = { start_items: self.base_state }
		
		while new_states:
			items, state = new_states.popitem()
			states[ items ] = state
			
			nexts = set( i.head for i in items if not i.reduce )
			for n in nexts:
				next = (i.advance().closure() for i in items if i.head is n)
				next = tuple( reduce( set.union, next, set() ) )
				if next in states:
					state.edges[ n ] = states[ next ]
				elif next in new_states:
					state.edges[ n ] = new_states[ next ]
				else:
					ident += 1
					new_state = CFGState( ident, next )
					state.edges[ n ] = new_state
					new_states[ next ] = new_state

		l = len(self.terminals) + len(self.nonterminals)
		self.table = [[None]*l for s in states]
		for s in states.values():
			for edge, dest in s.edges.items():
				ident = edge.glr_identifier
				if edge is CFGTerminal.EOF:
					act = CFGAction.Accept
				elif edge in self.terminals:
					act = CFGShiftAction( dest.identifier )
				else:
					act = CFGGotoAction( dest.identifier )
				self.table[ s.identifier ][ ident ] = act
			for i in filter( lambda i: i.reduce, s.items ):
				ident = i.lookahead.glr_identifier
				act = CFGReduceAction( i.production.nonterminal,
					len(i.production), i.production.action )
				self.table[ s.identifier ][ ident ] = act

	def _parse( self, lexer ):
		stack, output = [0], []
		lookahead, reduced = lexer.next(), None

		while lookahead is not CFGTerminal.EOF:
			action = self.table[ stack[-1] ][ lookahead.glr_identifier ]
			reduced = action( stack, output, lookahead )
			while reduced is not None:
				action = self.table[ stack[-1] ][ reduced.glr_identifier ]
				action( stack, output, reduced )
				action = self.table[ stack[-1] ][ lookahead.glr_identifier ]
				reduced = action( stack, output, lookahead )
			lookahead = lexer.next()

		action = self.table[ stack[-1] ][ lookahead.glr_identifier ]
		reduced = action( stack, output, lookahead )
		while reduced is not None:
			action = self.table[ stack[-1] ][ reduced.glr_identifier ]
			action( stack, output, reduced )
			action = self.table[ stack[-1] ][ lookahead.glr_identifier ]
			reduced = action( stack, output, lookahead )
		if action is not CFGAction.Accept:
			raise CFGUnexpectedEOFException()
		return output
		
	def parse( self, lexer ):
		try:
			lexer = chain( lexer, (CFGTerminal.EOF,) )
			return self._parse( lexer ).pop()
		except CFGUnexpectedEOFException:
			print("Unexpected EOF.")
		except CFGBadReduceException:
			print("Bad reduce.")
		except CFGUnexpectedTerminalException:
			print("Unexpected terminal.")

	def parse_items( self, *items ):
		return self.parse( iter(items) )


