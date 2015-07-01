
import re, sys

class Tokenizer:
	def __init__( self, split ):
		self.splitter = split

	def split( self, text ):
		self.text = text
		print text
		self.words = re.split( self.splitter, text )
		self.n = len( set(self.words) )

if __name__ == "__main__":
	if len( sys.argv ) < 2:
		sys.exit(0)

	t = Tokenizer( r"[^a-zA-Z0-9]+" )
	f = file( sys.argv[1] )
	t.split( '\n'.join( f.readlines() ) )
	print set(t.words)
	print t.n

