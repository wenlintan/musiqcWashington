
import os, time, threading

class FileDataLogger:
	def __init__( self, filename, maxsize = None, graphname = None, plotinterval = 60 ):
		self.save_file = filename
		self.max_size = maxsize

		self.graph_file = graphname
		self.plot = plotinterval

		self._load_data()
		self.save = open( self.save_file, "a" )

	def handle_data( self, data ):
		self.data.append( data )
		self.ndata += 1

		str_data = self._str_from_data( data )
		self.save.write( str_data )
			
		if self.max_size is not None and self.ndata > self.max_size:
			self._shrink_data()
			
		if self.ndata - self.last_plot > self.plot and self.graph_name is not None:
			self.save.flush()
			graph.make_plot( cutoff = 5000, show_plot = False, save = self.graph_name )
			self.last_plot = self.ndata
		
	def _load_data( self ):
		self.data = []
		self.ndata = self.last_plot = 0		

		if os.path.exists( self.save_file ):
			self.save = open( self.save_file, "r" )
			for l in self.save.readlines():
				if not l.strip():
					continue
				self.data.append( self._data_from_str(l) )
			self.save.close()
		self.last_plot = self.ndata = len( self.data )

	def _str_from_data( self, d ):
		str_data = "\t\t".join([ "\t".join([ str(k) for k in ch ]) for ch in d ])
		return str_data + '\n'

	def _data_from_str( self, s ):
		data = [ int(i.strip()) for i in s.split() ]
		data = [(data[i], data[i+1], data[i+2]) for i in range(0, len(data), 3)]
		return data

	def _shrink_data( self ):
		self.save.close()
	
		self.data = self.data[-self.max_size/2:]
		self.save = open( self.save_file, "w" )
		for d in self.data:
			self.save.write( self._str_from_data( d ) )
		self.save.close()
	
		self.save = open( self.save_file, "a" )
		self.ndata = self.last_plot = len(self.data)


class FileParameterClient( threading.Thread ):
	def __init__( self, filename ):
		threading.Thread.__init__( self )
		self.filename = filename
		self.old_mtime, self.newvals = 0, None
		if os.path.exists( self.filename ):
			self.old_mtime = os.stat( self.filename ).st_mtime
			
		self.running = True

	def _check( self ):
		if not os.path.exists( self.filename ):
			return

		if os.stat( self.filename ).st_mtime - self.old_mtime < 10:
			return

		try:
			self.old_mtime = os.stat( self.filename ).st_mtime
			f = open( self.filename, "r")
			pgain, pshift, igain, ishift = [str(f.readline()[:-1]) for i in range(4)]
			f.close()

			print("New values:", pgain, pshift, igain, ishift)
			params = urllib.urlencode({"pg":pgain, "ps":pshift, "ig":igain, "is":ishift})
			urllib2.urlopen( 'http://localhost:8321/parameters', params )
		except urllib2.URLError:
			print("Failed to send parameters.", response)
		except ValueError, e:
			print("Bad data in value file.")
		except Exception, e:
			print e

	def run( self ):
		while self.running:
			self._check()
			time.sleep(1)
		print "Done."

	def stop( self ):
		self.running = False
		self.join()
