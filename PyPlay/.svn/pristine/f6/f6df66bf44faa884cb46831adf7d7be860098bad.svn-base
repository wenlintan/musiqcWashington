
from itertools import product

class Node:
	nvalues = 2
	def __init__( self, name, time, prev, parents, prob ):
		self.name = name
		self.time = time

		if prev is not None:
			prev.next = self
		self.prev = prev

		self.parents = list( parents )
		for p in self.parents:
			p.children.append( self )

		self.children = []
		self.prob = prob

	def clone( self ):
		return Node( self.name, self.time+1, 
			self, self.parents, self.prob )

	def advance( self ):
		self.parents = [ p.next for p in self.parents ]
		self.children = [ c.next for c in self.children ]

class ArgumentNode( Node ):
	def __init__( self, name, time, nargs, prev, parents, prob, *args ):
		super( ArgumentNode, self ).__init__()
		self.nargs = nargs
		self.args = args

	def __call__( self, *args ):
		if len( args ) != self.nargs:
			raise ValueError( "Incorrect number of arguments." )
		return ArgumentNode( self.name, self.time, self.nargs, self.prev,
			self.parents( args ), self.prob, *args )

class TemporalModel:
	def __init__( self, initial, state, evidence ):
		self.initial = initial
		self.steps = [(initial, None), ( state, evidence )]

	def _prob( self, node ):
		index, multiplier = node.value, node.nvalues
		for p in node.parents:
			index += multiplier * p.value
			multiplier *= p.nvalues
		return node.prob[ index ]

	def explain_Viterbi( self, initial, evalues ):
		prob = initial
		for (i, step_evalues) in enumerate( evalues ):
			state, evidence = self.steps[ -1 ]
			for s in state:
				s.parent_assn = {}

			for (e, v) in zip( evidence, step_evalues ):
				e.value = v

			new_prob = {}
			for xtp1 in product( *(range(n.nvalues) for n in state) ):
				for (s, v) in zip( state, xtp1 ):
					s.value = v

				mult = lambda x, y: x*y
				p_e_x = reduce( mult, (self._prob(e) for e in evidence) )
				print "pex", p_e_x, xtp1, [p.value for p in evidence[0].parents]

				pmax = 0.
				prev_state = self.steps[ -2 ][0]
				for xt in product( *(range(n.nvalues) for n in evidence) ):
					for (s, v) in zip( prev_state, xt ):
						s.value = v

					p_x_x = reduce( mult, (self._prob(s) for s in state) )
					p = p_x_x * prob[ xt ]
					print "pxt", prob[ xt ]
					print "pxx", p_x_x, xt, [p1.value for p1 in state[0].parents]
					if p > pmax:
						pmax = p
						for s, new, par in zip( state, xtp1, xt ):
							s.parent_assn[ new ] = par

				new_prob[ xtp1 ] = p_e_x * pmax
				print xtp1, p_e_x * pmax
			prob = new_prob

			new_state, new_evidence = [], []
			for s in state:
				new_state.append( s.clone() )
			for e in evidence:
				new_evidence.append( e.clone() )
			for s in new_state:
				s.advance()
			for e in new_evidence:
				e.advance()
			self.steps.append( (new_state, new_evidence) )

	def step( self, evidence ):
		pass

if __name__ == "__main__":
	rain0 = Node( "Rain0", 0, None, tuple(), None )
	rain = Node( "Rain", 1, rain0, (rain0,), (0.7, 0.3, 0.3, 0.7) )
	umbrella = Node( "Umbrella", 1, None, (rain,), (0.8, 0.2, 0.1, 0.9) )
	tm = TemporalModel( (rain0,), (rain,), (umbrella,) )

	tm.explain_Viterbi( { (0,): 0.5, (1,): 0.5 }, 
		[(1,), (1,), (0,), (1,), (1,)] )

	
