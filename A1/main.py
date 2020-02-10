import argparse
import re
import socket
class Packet(object):
	def __init__(self,server,name):
		self.server = server.split()

parser = argparse.ArgumentParser(description='DNS client')
parser.add_argument('-t', type=int, default=5,help='time out of retransmit')
parser.add_argument('-r', type=int, default=3,help='max-retries')
parser.add_argument('-p', type=int, default=53,help='UDP port number of the DNS server')
parser.add_argument('-mx', action = 'store_true',help='send a mail server query')
parser.add_argument('-ns', action = 'store_true',help='send a name server query')
parser.add_argument('server')
parser.add_argument('name')
args = parser.parse_args()

if args.mx and args.ns:
	print('ERROR    invalid argument:could send mail server and name server at the same time')
	exit()

if not re.match(r'^@\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$',args.server):
	print('ERROR	invalid argument:format of server address is wrong')
	exit()


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
