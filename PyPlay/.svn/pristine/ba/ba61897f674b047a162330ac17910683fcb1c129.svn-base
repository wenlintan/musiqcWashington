
from simulation import *

class Term( object ):
	def __le__( self, rhs ):
		return self | -rhs

	def __neg__( self ):
		return Negate( self )

	def __or__( self, rhs ):
		if rhs.__class__ == Disjunction:
			return rhs | self
		return Disjunction( self, rhs )

	def __and__( self, rhs ):
		if rhs.__class__ == Conjunction:
			return rhs & self
		return Conjunction( self, rhs )

	def substitute( self, subst ):
		return self
	
class Operator( Term ):
	def __init__( self, name, op, *args ):
		super( Operator, self ).__init__()
		self.name = name
		self.op = op
		self.args = list(args)

	def evaluate( self, *args ):
		self.op( args )

	def __call__( self, *args ):
		return Operator( self.name, self.op, *args )

	def unify( self, rhs ):
		if self.__class__ != rhs.__class__:
			return None
		
		subst = {}
		for a, ra in zip( self.args, rhs.args ):
			s = a.unify( ra )
			if s is None: return None
			subst.update( s )
		return subst

class Negate( Operator ):
	def __init__( self, arg ):
		super( Negate, self ).__init__( '-', lambda x: not x[0], arg )

	def __neg__( self ):
		return self.args[0]

	def __repr__( self ):
		return '-%s' % repr(self.args[0])

class Conjunction( Operator ):
	def __init__( self, *args ):
		super( Conjunction, self ).__init__( '&', all, *args )

	def __neg__( self ):
		l = [ -a for a in self.args ]
		return Disjunction( *l )

	def __and__( self, rhs ):
		self.args.append( rhs )
		return self

	def __repr__( self ):
		return ' & '.join( repr(a) for a in self.args )

class Disjunction( Operator ):
	def __init__( self, *args ):
		super( Disjunction, self ).__init__( '|', any, *args )

	def __neg__( self ):
		l = [ -a for a in self.args ]
		return Conjunction( *l )

	def __or__( self, rhs ):
		self.args.append( rhs )
		return self

	def __repr__( self ):
		return ' | '.join( repr(a) for a in self.args )

class Predicate( Term ):
	def __init__( self, name, *args ):
		super( Predicate, self ).__init__()
		self.name = name
		self.args = list(args)

	def __call__( self, *args ):
		return Predicate( self.name, *args )

	def __repr__( self ):
		return '%s( %s )' % ( self.name, ', '.join( self.args ) )

	def substitute( self, subst ):
		mapped = ( subst[a] if a in subst else a for a in self.args )
		return Predicate( self.name, *mapped )

	def unify( self, rhs ):
		if rhs.__class__ != Predicate or self.name != rhs.name:
			return None

		subst = {}
		for a, ra in zip( self.args, rhs.args ):
			if a != ra:
				subst[ a ] = ra
		return subst

class Knowledge( Entity ):
	def __init__( self ):
		super( Knowledge, self ).__init__()
		self.database = []

	def _is_horn_clause( self, p ):
		if p.__class__ == Negate or p.__class__ == Conjunction:
			return False
		elif p.__class__ == Disjunction:
			nneg = len( [a for a in p.args if a.__class__ == Negate] )
			if nneg != len( p.args ) - 1:
				return False
		return True

	def tell( self, term ):
		if not self._is_horn_clause( term ):
			return

		if term in self.database:
			return

		self.database.append( term )
		for p in self.database:
			negs = [ a.args[0] for a in p.args if a.__class__ == Negate ]
			conc = [ a for a in p.args if a.__class__ != Negate ][0]
			for i, n in enumerate( negs ):
				s = n.unify( term )
				if s is not None:
					prems = negs[:i]
					prems.extend( negs[i+1:] )
					self._find_and_infer( prems, conc, s )
				
	def _find_and_infer( self, premises, conc, subst ):
		if not premises:
			self.learn( conc.substitute( subst ) )
		else:
			for p in self.database:
				s = premises[0].substitute( subst ).unify( p )
				if s is not None:
					s.update( subst )
					self._find_and_infer( premises[1:], conc, s )

	def __repr__( self ):
		return '\n'.join( repr(d) for d in self.database )

if __name__ == "__main__":
	k = Knowledge()
	parent = Predicate( 'Parent' )
	male = Predicate( 'Male' )
	father = Predicate( 'Father' )

	k.tell( parent( 'Tom', 'John' ) )
	k.tell( father( 'x', 'y') <= parent( 'x', 'y' ) & male( 'y' ) )
	k.tell( male( 'John' ) )

	print( '\n'.join( repr(d) for d in k.database ) )


