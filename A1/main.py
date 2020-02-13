import argparse
import re
import socket
from packetParser import PacketParser
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
s.settimeout(args.t)
s.sendto(data,(args.server[1:],args.p))
response = b''
serverAddr = ()
numOfTries = 0

while response == b'' or response is None:
	try:
		response,serverAddr = s.recvfrom(1024)
	except socket.timeout as e:
		if numOfTries < args.t:
			print('not receiving,resend the message')
			s.sendto(data,(args.server[1:],args.p))
			numOfTries = numOfTries + 1
		else:
			print('ERROR	message transfer:the number of resend the message has been used up')
			exit()
print(response)
if serverAddr != (args.server[1:],args.p):
	print('ERROR	unexpect response:response from wrong server')
	exit()
if response[3] & 1:
	print('ERROR	Format error: the name server was unable to interpret the query')
	exit()
elif response[3] & 2:
	print('ERROR	Server failure: the name server was unable to process this query due to a problem with the name server')
	exit()
elif response[3] & 3:
	print('ERROR	Name error: meaningful only for responses from an authoritative name server, this code signifies that the domain name referenced in the query does not exist')
	exit()
elif response[3] & 4:
	print('ERROR	Not implemented: the name server does not support the requested kind of query')
	exit()
elif response[3] & 5:
	print('ERROR	Refused: the name server refuses to perform the requested operation for policy reasons')
	exit()
parsedResponse = PacketParser(response,data)
for i in parsedResponse.Ans:
	if i['type'] == 'A':
		print('IP	',i['ipAddress'],'	', i['TTL'],'	',parsedResponse.authority)
	elif i['type'] == 'MX':
		print('MX	',i['exchange'],'	',i['preference'],'	',i['TTL'],'	',parsedResponse.authority)
	elif i['type'] == 'NS':
		print('NS	',i['serverName'],'	',i['TTL'],'	',parsedResponse.authority)
	elif i['type'] == 'CNAME':
		print('CNAME	',i['alias'],'	',i['TTL'],'	',parsedResponse.authority)
for i in parsedResponse.Add:
	if i['type'] == 'A':
		print('IP	',i['ipAddress'],'	', i['TTL'],'	',parsedResponse.authority)
	elif i['type'] == 'MX':
		print('MX	',i['exchange'],'	',i['preference'],'	',i['TTL'],'	',parsedResponse.authority)
	elif i['type'] == 'NS':
		print('NS	',i['serverName'],'	',i['TTL'],'	',parsedResponse.authority)
	elif i['type'] == 'CNAME':
		print('CNAME	',i['alias'],'	',i['TTL'],'	',parsedResponse.authority)