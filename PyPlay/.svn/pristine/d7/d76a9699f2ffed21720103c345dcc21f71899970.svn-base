
class CFGBadReduceException( Exception ):
	pass
class CFGUnexpectedEOFException( Exception ):
	pass
class CFGUnexpectedTerminalException( Exception ):
	pass

class CFGAction(object):
	def __call__( self, stack, output, lookahead ):
		pass
CFGAction.Accept = CFGAction()

class CFGUnexpectedAction:
	def __call__( self, stack, output, lookahead ):
		raise CFGUnexpectedTerminalException()

class CFGGotoAction:
	def __init__( self, state ):
		self.state = state

	def __call__( self, stack, output, lookahead ):
		stack.append( self.state )

class CFGShiftAction:
	def __init__( self, state ):
		self.state = state

	def __call__( self, stack, output, lookahead ):
		stack.append( self.state )
		output.append( lookahead.data )

class CFGReduceAction:
	def __init__( self, nonterm, nargs, fn ):
		self.nonterminal = nonterm
		self.nargs = nargs
		self.fn = fn

	def __call__( self, stack, output, lookahead ):
		if len(stack) < self.nargs:
			raise CFGBadReduceException()
		
		args = []
		for i in range( self.nargs ):
			args.append( output.pop() )
			stack.pop()
		args.reverse()
		output.append( self.fn( *args ) )
		return self.nonterminal
