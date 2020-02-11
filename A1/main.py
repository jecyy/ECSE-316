import argparse
import re
import socket
class Packet(object):
	def __init__(self,name,type):
		self.name = bytes(self.formName(name.split('.')))
		self.type = bytes([self.typeTransform(type)])
	def formName(self,names):
		formatName = []
		for n in names:
			formatName.append(len(n))
			for c in n:
				formatName.append(ord(c))
		return formatName
	def typeTransform(self,type):
		typemap = {'A':1,'NS':2,'MX':15}
		return typemap[type]
	def generateData(self):
		return b'\x82\x7a\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00'+self.name+b'\x00\x00'+self.type+b'\x00\x01'
class PacketParser(object):
	def __init__(self,response,data):
		self.IDVerification = response[:2] == data[:2]
		self.TTL = response[len(data)+8:len(data)+10]
		self.autority = 'auth' if response[2] & 4 else 'non-auth'
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
type = 'NS' if args.ns else 'MX' if args.mx else 'A'
packet = Packet(args.name,type)
print('DNS sending request for:',args.name)
print('Server:',args.server[1:])
print('Request type:',type)
data = packet.generateData()
print(data)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto(data,(args.server[1:],args.p))
response,serverAddr = s.recvfrom(1024)
print(response)
if serverAddr != (args.server[1:],args.p):
	print('ERROR	unexpect response:response from wrong server')
	exit()