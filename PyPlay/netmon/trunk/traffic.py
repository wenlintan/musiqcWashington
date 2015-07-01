#!/usr/bin/python

from socket import *
from subprocess import *
from datetime import datetime
from time import sleep

def read_arp_cache():
	with file( "/proc/net/arp" ) as f:
		i = iter( f )
		i.next()
		for line in i:
			ip, hw, flags, mac, mask, device = line.split()
			if device != "br0":
				continue
			fmt = "dig +short -x {0}"
			proc = Popen( fmt.format( ip ), stdout=PIPE, shell=True )
			data, _ = proc.communicate()
			data = data.strip()
			if not data:
				data = mac
			yield ip, (data, mac)

arps = {}
s = socket(AF_INET, SOCK_DGRAM)

# Flush out old data, these may fail
call( "iptables -D forward-traffic -j forward-client-traffic", shell = True )
call( "iptables -F forward-client-traffic", shell = True )
call( "iptables -X forward-client-traffic", shell = True )

# Write new traffic monitoring data
check_call( "iptables -N forward-client-traffic", shell = True )
check_call( "iptables -A forward-client-traffic -j RETURN", shell = True )
check_call( "iptables -I forward-traffic -j forward-client-traffic", shell = True )

last_time = datetime.now()
while True:
	new_arps = dict(read_arp_cache())
	if arps != new_arps:		
		for ip in new_arps.keys():
			if ip in arps.keys():
				continue
			check_call( "iptables -I forward-client-traffic -s {0} -j RETURN".format(ip), shell = True )
			check_call( "iptables -I forward-client-traffic -d {0} -j RETURN".format(ip), shell = True )

		for ip in arps.keys():
			if ip in new_arps.keys():
				continue
			check_call( "iptables -D forward-client-traffic -s {0} -j RETURN".format(ip), shell = True )
			check_call( "iptables -D forward-client-traffic -d {0} -j RETURN".format(ip), shell = True )

		arps = new_arps

	incoming, outgoing = {}, {}
	def parse( data ):
		for line in data.splitlines()[2:-1]:	# Skip unrelated lines
			pkts, bytes, target, proto, opt, i, o, src, dest = line.split()
			if i == "eth1":
				incoming[ "Total" ] = bytes
			elif src in arps:
				outgoing[ arps[src][0] ] = bytes
			elif o == "eth1":
				outgoing[ "Total" ] = bytes
			elif dest in arps:
				incoming[ arps[dest][0] ] = bytes

	t = datetime.now()
	dt = t - last_time
	diff = dt.seconds + dt.microseconds / 1e6
	last_time = t

	proc = Popen( "iptables -vnxZ -L forward-client-traffic", 
			stdout=PIPE, shell=True )
	data, err = proc.communicate()
	parse( data )

	proc = Popen( "iptables -vnxZ -L forward-traffic", stdout=PIPE, shell=True )
	data, err = proc.communicate()
	parse( data )

	data = []
	for k in arps.keys():
		d, m = arps[k]
		fmt = '{{"name": "{0}", "ip": "{1}", "mac": "{2}", "incoming": {3}, "outgoing": {4}}}'
		data.append( fmt.format( d, k, m, incoming[d], outgoing[d] ) )
	data.append( '{{"incoming": {0}, "outgoing": {1}, "dt": {2}}}'.format( incoming["Total"], outgoing["Total"], diff ) )
	data = '[{0}]'.format( ", ".join( data ) )
	s.sendto( data, ("127.0.0.1", 515) )
	
	print data
	sleep(5)



