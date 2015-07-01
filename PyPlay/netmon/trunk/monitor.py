#!/usr/bin/python
import select
from socket import *

import json, re, time
from datetime import datetime
import urlparse, urllib, urllib2

from subprocess import *
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


class JSONAPIRequestHandler( BaseHTTPRequestHandler ):
	def _send_headers( self, content_type, length ):
		self.send_response( 200 )
		self.send_header("Content-Type", content_type)
		self.send_header("Content-Length", length )
		self.send_header("Access-Control-Allow-Origin", "*")
		self.end_headers()
		
	def _recent( self, last = 0 ):
		result = self.server.recent( 0, last )
		self._send_headers( "application/json", len(result) )
		self.wfile.write( result )
		
	send_files = { 
		"/": "text/html",
		"/index.html": "text/html", 
		"/style.css": "text/css", 
		"/graph.js": "text/javascript",
		"/monitor.js": "text/javascript",
		"/jquery-1.7.1.min.js": "text/javascript"
		}

	def _send_file( self, fname ):
		ctype = self.send_files[ fname ]
		if fname == '/':
			fname = "/index.html"
		fname = "/home/wrightj/Desktop/SVN/NetMon/trunk" + fname

		f = file(fname, 'r')
		d = ''.join( f.readlines() )
		f.close()
		
		self._send_headers( ctype, len(d) )
		self.wfile.write( d )

	def do_GET( self ):
		parse = urlparse.urlparse(self.path)
		params = None
		
		if parse.query:
			i = urlparse.parse_qs( parse.query ).items()
			params = dict([ (k, v[0]) for k, v in i ])
		print self.path, params
			
		if parse.path in ('/recent', '/recent/'):
			self._recent( int(params["l"]) if params else None )
			
		if parse.path in self.send_files:
			self._send_file( parse.path )

	def do_POST( self ):
		params = None
		if int(self.headers["Content-Length"]) != 0:
			params = self.rfile.read( int(self.headers["Content-Length"]) )
			params = urlparse.parse_qs( params )
			params = dict([(k,int(v[0])) for k, v in params.items()])
		
		if self.path in ('/recent', '/recent/'):
			self._recent( params["l"] if params else None )
		
		else:
			self.send_response( 404 )
			
class Client:
	traffic_data_limit = 100
	def __init__( self, name ):
		self.name = name
		self.awake = False
		self.upload = []
		self.download = []

	def update( self, traffic ):
		self.awake = True
		attrs = ["name", "ip", "mac"]
		for a in attrs:
			setattr( self, a, traffic[a] )

		self.upload.append( traffic['outgoing'] )
		self.download.append( traffic['incoming'] )
		if len( self.upload ) > self.traffic_data_limit:
			self.upload.pop(0)
			self.download.pop(0)

	def json_data( self ):
		e = {"type": "client", "name": self.name, "ip": self.ip, "mac": self.mac, "awake": self.awake}
		if self.download:
			e[ "download" ] = self.download
			e[ "upload" ] = self.upload
		return ( json.dumps( e ), )

class JSONAPIServer( HTTPServer ):
	event_limit = 500
	def __init__( self, addr, handler ):
		HTTPServer.__init__( self, addr, handler )
		self.events = [""] * self.event_limit
		self.event_pos = 0

		self.traffic_time = datetime.now()
		self.clients = {}

	def _add_event( self, event ):
		self.events[ self.event_pos ] = event
		self.event_pos += 1
		self.event_pos %= self.event_limit

	def full_update( self ):
		events = []
		for c in self.clients.values():
			events.extend( c.json_data() )
		events.append( '{{"l": {0}}}'.format( self.event_pos ) )
		return "[{0}]".format( ', '.join( events ) )

	def recent( self, filter, index ):
		if index is None:
			return self.full_update()
		elif index > self.event_limit:
			events = self.events[ index: ]
			events.append( '{"l": 0}' )
		else:
			events = self.events[ index: self.event_pos ]
			events.append( '{{"l": {0}}}'.format( self.event_pos ) )
		return "[{0}]".format( ', '.join( events ) )		
		
	def handle_traffic( self, traffic_data ):
		data = json.loads( traffic_data )
		s = set( d['name'] for d in data if 'name' in d )
		for n, c in self.clients.items():
			if n in s:
				continue
			c.awake = False
			e = {'name': n, 'ip': c.ip, 'mac': c.mac, 'awake': False}
			e['type'] = 'client'
			self._add_event( json.dumps(e) )

		save_data = {'type': 'bandwidth'}
		save_data[ 'client_ul' ] = {}
		save_data[ 'client_dl' ] = {}

		for i, d in enumerate(data):
			if not 'name' in d:
				dt = d[ 'dt' ]
				save_data[ 'ul' ] = d['outgoing'] / dt
				save_data[ 'dl' ] = d['incoming'] / dt
				del data[i]
				break
				
		for d in data:
			ul, dl = d['outgoing'] / dt, d['incoming'] / dt
			name = d['name']
			if name not in self.clients:
				self.clients[ name ] = Client( name )
				e = {'name': name, 'ip': d['ip'], 'mac': d['mac']}
				e['awake'] = True
				e['type'] = 'client'
				self._add_event( json.dumps(e) )

			self.clients[ name ].update( d )
			save_data[ 'client_ul' ][ name ] = ul
			save_data[ 'client_dl' ][ name ] = dl

		self._add_event( json.dumps(save_data) )

	param_map = {"SRC": "src", "DST": "dest", "PROTO": "proto",
		"SPT": "sport", "DPT": "dport"}

	def handle_connection( self, conn ):
		# Router kernel: [271438.431756] [UFW NEW] 
		#  IN= OUT=eth1 PHYSIN=wlan0 SRC=192.168.1.101 DST=76.74.254.123 
		#  LEN=64 TOS=0x00 PREC=0x00 TTL=63 ID=18017 DF PROTO=TCP SPT=64244 
		#  DPT=80 WINDOW=65535 RES=0x00 SYN URGP=0
		print conn
		dpattern = r"<\d*> *(?P<mon>\w*) +(?P<day>\d*) +(?P<t>\d+:\d+:\d+) +(?P<r>.*)"
		r = re.match( dpattern, conn )
		mon, day, t, conn = map( r.group, ["mon", "day", "t", "r"] )

		utc = 0
		mons = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
		mon = mons.index( mon ) + 1
		if mon != 0:
			day = int(day)
			year = datetime.now().year
			hour, minu, sec = [ int(a) for a in t.split(':') ]
			utc = int( time.mktime( (year, mon, day, hour, minu, sec, -1, -1, -1) ) )

		index = conn.find( ':' )
		if conn[ : index ].strip() != "Router kernel":
			return

		rest = conn[ index+1: ]
		pattern = r"\[(?P<t>\d*\.\d*)\] +\[(?P<m>[\w\s]*)\] +(?P<r>.*)"
		r = re.match( pattern, rest.strip() )
		t, message = r.group( 't' ), r.group( 'm' )

		rest = {}
		rest[ 'utc' ] = utc
		for d in r.group( 'r' ).split():
			l = d.split( '=' )
			if len( l ) == 2:
				name, value = l
			else:
				name, value = l[0], True
			if name in self.param_map:
				rest[ self.param_map[name] ] = value
		if message == "UFW BLOCK":
			rest[ 'type' ] = "Blocked"
		elif message == "UFW NEW":
			if rest[ 'src' ][ : 10 ] == "192.168.1.":
				rest[ 'type' ] = "Outgoing"
			else:
				rest[ 'type' ] = "Incoming"

		for n in ["src", "dest"]:
			if n in rest:
				ip = rest[n]
				fmt = "dig +short -x {0}"
				proc = Popen( fmt.format( ip ), stdout=PIPE, shell=True )
				data, _ = proc.communicate()
				if data.strip():
					rest[ n ] = data.strip()
	
		self._add_event( json.dumps( rest ) )


server = JSONAPIServer(('', 8321), JSONAPIRequestHandler)

ufw_sock = socket(AF_INET, SOCK_DGRAM)
ufw_sock.bind(('127.0.0.1', 514))
ufw_sock.setblocking(0)

traffic_sock = socket(AF_INET, SOCK_DGRAM)
traffic_sock.bind(('127.0.0.1', 515))
traffic_sock.setblocking(0)

while True:
	active, _, __ = select.select([ufw_sock, traffic_sock, server], [], [])
	if ufw_sock in active:
		server.handle_connection( ufw_sock.recv(4096) )
	if traffic_sock in active:
		server.handle_traffic( traffic_sock.recv(4096) )
	if server in active:
		server.handle_request()


