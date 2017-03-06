#Project 2 Routing Table
#Name: Kaivan Shah
#EID: kks942

from socket	import socket
from socket	import AF_INET
from socket	import SOCK_STREAM
from sys import argv
from sys import exit
from ipaddress import IPv4Network
from ipaddress import IPv4Address

DEF_NETMASK = IPv4Network("0.0.0.0/0")
DEF_AS = 'A'
DEF_COST = 100

listOfAS = {}

class AddressNotFound (Exception) :
	pass

class AutonomousSystem :
	def __init__(system, as_name) :
		system.as_name = as_name
		system.address = {}

	def update_as(system, netmask, netcost) :
		system.address[netmask] = netcost

	def query_as(system, as_add) :
		best_n = DEF_NETMASK
		best_cost = DEF_COST
		
		for n in system.address :
			if as_add in n :
				c = system.address[n]
				if c < best_cost :
					best_n = n
					best_cost = c
		
		if best_n != DEF_NETMASK :
			return best_n, best_cost
		raise AddressNotFound

def update_AS (line) :
	lines = line.split(' ')
	listOfAS[lines[0]].update_as(IPv4Network(lines[1]), int(lines[2]))

def query_AS (addr) :
	ip = IPv4Address(addr)
	AS_name = DEF_AS
	net_mask = DEF_NETMASK
	net_cost = DEF_COST
	query = addr

	for ASName in listOfAS :
		try :
			curr_mask, curr_cost = listOfAS[ASName].query_as(ip)
			if curr_cost < net_cost or (curr_cost == net_cost and curr_mask.prefixlen > net_mask.prefixlen) :
				net_cost = curr_cost
				AS_name = ASName
				net_mask = curr_mask

		except AddressNotFound :
			pass
	query +=" " + AS_name
	query +=" " + str(net_cost)
	return query

#Here we listen client and accept the connection. Then,
def listen_client() :
	loop = True
	while loop:
		request = ""
		info = {}
		split_lines = ""
		response = ""

		client_socket, addr = server_socket.accept()
		# 1. We get the request through the wire
		request = client_socket.recv(8192)
		request = bytes.decode(request)
		print(request)

		# 2. parse the request
		split_lines = request.splitlines()
		length = len(split_lines)

		assert length >= 3
		assert split_lines[length - 1] == "END"
		#store the command
		info[0] = split_lines[0]
		#store the body
		info[1] = [split_lines[i] for i in range(1, length - 1)]
		assert len(info[1]) == length - 2
		assert len(info[1]) > 0

		# 3. get a response
		if info[0] == "UPDATE" :
			response = response + "ACK" + "\r\n"
			assert len(info[1]) > 0
			for line in info[1] :
				update_AS(line)
		else :
			response = response + "RESULT" + "\r\n"
			assert len(info[1]) == 1
			response = response + query_AS(info[1][0]) + "\r\n"
		response = response + "END" + "\r\n"
		print(response)

		# 4. Send encoded response
		client_socket.send(response.encode())
		client_socket.close()

#server
server_name = "localhost"
print("The server",server_name,"is ready...")

if len(argv) != 2 :
	print("Enter the port number")
	exit()
server_port = int(argv[1])
server_socket = socket(AF_INET, SOCK_STREAM)

for n in range(ord('A'), ord('I')) :
	listOfAS[chr(n)] = AutonomousSystem(chr(n))

server_socket.bind(('', server_port))
server_socket.listen(1)
listen_client()