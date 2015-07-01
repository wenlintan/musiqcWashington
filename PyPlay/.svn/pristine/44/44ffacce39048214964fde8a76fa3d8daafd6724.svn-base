#!/usr/bin/env python

import argparse, re
from collections import defaultdict

class DataFile:
	def __init__( self, filename, scale = 1.0, emap = None ):
		self.comments, self.dt = [], 0.
		self.potentials = self._load_file( filename, scale, emap )
	
	@staticmethod
	def build_electrode_map( data ):
		emap, place = defaultdict( lambda: 0 ), 0
		for item in data.split(','):
			if item[0] == '_':		
				place += 1
			elif item[0].isdigit():	
				emap[ place ] = int( item )
				place += 1
			elif item[0] == '[':
				begin, end = item[1:-1].split('-')
				for i in range( int(begin), int(end) ):
					emap[ place ] = i
					place += 1
			else:
				print "Failed to parse electrode_map, ignoring."
				return None
		return emap
	
	def add_compensation( self, filename, scale = 1.0, emap = None ):
		p = self._load_file( filename, scale, emap )
		self.potentials = self._add_potentials( self.potentials, p )

	def _add_potentials( self, t1, t2 ):
		pot = []
		for t1line, t2line in zip( t1, t2 ):
			data = defaultdict( lambda: 0. )
			for i, d in t1line:
				data[ i ] += d
			for i, d in t2line:
				data[ i ] += d
			pot.append( list( data.items() ) )
		return pot
						
	def _load_file( self, filename, scale, emap ):
		col_offset = None
		if emap is None:
			emap = dict( (i,i) for i in range(100) )
		pot = []

		with open( filename ) as f:
			for line in f:
				if line.startswith('#') : 	self.comments.append( line.replace('#','').strip() )
				if line.startswith('dt=') : self.dt = float(line[3:])
				if line.startswith('e0') : 	col_offset = 0
				if line.startswith('e1') : 	col_offset = 1
				if line[0].isdigit() or line[0] in '+-':
					# check we know how the columns match up to the electrodes
					if col_offset is None and emap is None:
						print( 'Warning : electrode header info not found. Assuming starts with electrode number 1' )
						col_offset = 1
					elif emap is not None:
						col_offset = 0

					# split up the rows by tab or comma and make into list of floats
					rawdata = [float(i) for i in re.split('\t| |\n|,', line) if i != '']

					potential_row = [(emap[i + col_offset], scale*d) for i, d in enumerate(rawdata) if emap[i+col_offset]]
					pot.append( potential_row )
			
		return pot

	def write( self, filename, num_electrodes = None ):
		if num_electrodes is None:
			num_electrodes = max( l[0] for l in self.potentials[0] )
			
		with open( filename, 'w' ) as f:
			for c in self.comments:
				f.write( '#' + c + '\n' )
			
			f.write( 'dt=' + str(self.dt) + '\n' )
			for i in range( num_electrodes ):
				f.write( 'e' + str(i+1) + '\t' )
			f.write( '\n' )
		
			for line in self.potentials:
				data = [0. for i in range(num_electrodes)]
				for i, d in line:
					data[ i-1 ] = d
				f.write( '\t'.join( [str(d) for d in data] ) )
				f.write( '\n' )							
	
if __name__ == "__main__":

	parser = argparse.ArgumentParser(description = 'Adds compensation or other fields to trapping potential')
	parser.add_argument('trap_potential',
						help="""Specify the filename of the file that gives the basic trapping potential."""
						)

	parser.add_argument('output_file',
						help="""Specify filename for output."""
						)

	parser.add_argument('-s', '--scale', default=1.0,
						help="""Specify scale for trap_potential."""
						)

	parser.add_argument('--compensation', nargs='+', action='append', metavar=('filename', 'scale', 'electrode_map'),
						help="""Add a compensation file to base trap potential."""
						)

	parser.add_argument('--electrode_map', default=None,
						help="""Specify the mapping between input columns and trap electrodes (1 based).
								Usage: --electrode_map _,[21-30],31,32,[33-40]"""
						)
						
	parser.add_argument('-n', '--nelectrodes',
						help="""Specify number of electrodes to be writtten in output file.
								Otherwise this number is assumed from the highest electrode number."""
						)

	args = vars(parser.parse_args())
	

	emap = None
	if args['electrode_map']:
		emap = DataFile.build_electrode_map( args['electrode_map'] )
			
	df = DataFile( args['trap_potential'], float(args['scale']), emap )
	if args['compensation']:
		for item in args['compensation']:
			scale, item_emap = 1.0, emap
			if len(item) > 1:	scale = float(item[1])
			if len(item) > 2:	item_emap = DataFile.build_electrode_emap(item[2])
			df.add_compensation( item[0], scale, item_emap )

	nelectrodes = None
	if 'nelectrodes' in args:
		nelectrodes = int( args['nelectrodes'] )
	df.write( args['output_file'], nelectrodes )

	




