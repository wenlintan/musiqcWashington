

class MainEventHandler:
	def __init__( self ):
		self.handlers = []

	def push( self, handler ):
		self.handlers.insert( 0, handler )

	def pop( self ):
		self.handlers.pop(0)

	def handle_event( self, event ):
		for h in self.handlers:
			if h.handle_event( event ):
				return

