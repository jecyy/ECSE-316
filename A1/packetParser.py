class PacketParser(object):
	def __init__(self,response,data):
		self.IDVerification = response[:2] == data[:2]
		self.numAu = self.calNum(response[8:10])
		self.numAdd = self.calNum(response[10:12])
		#self.TTL = self.calTTL(response[len(data)+6:len(data)+10])
		self.authority = 'auth' if response[2] & 4 else 'non-auth'
		#self.RDLENGTH = self.calNum(response[len(data)+10:len(data)+12])
		self.numOfAns = self.calNum(response[6:8])
		self.Ans = []
		self.Add = []
		self.appendAnswer(response,data)
	def calTTL(self,TTLbytes):
		sum = 0
		expIndex = 3
		for b in TTLbytes:
			sum = sum + b^(expIndex*2)
			expIndex = expIndex - 1
		return sum
	def calNum(self,RDLENGTHbytes):
		#print(RDLENGTHbytes[0]*(16^2)+RDLENGTHbytes[1])
		return RDLENGTHbytes[0]*(16^2)+RDLENGTHbytes[1]
	def calType(self, n):
		typemap = {1:'A' ,2:'NS',15:'MX', 5:'CNAME'}
		return typemap[n]
	def calAddress(self,IPbytes):
		IPList = []
		for i in IPbytes:
			IPList.append(str(i))
		ipAddress = '.'.join(IPList)
		return ipAddress
	def parseName(self,b):
		qname = ''
		for i in b:
			if i in range(48,58) or i in range(65,91) or i in range(97,123):
				qname = qname + chr(i)
			else:
				qname = qname + '.'
		return qname
	def appendAnswer(self,response,data):
		if self.numOfAns + self.numAdd == 0:
			print('no valid answer')
			exit()
		i = len(data)
		scanner = 0
		def parseAnswer(answers,i):
			answer = {}
			b = []
			if response[i] & 192:
				scanner = self.calNum(response[i:i+2])-192*(16^(2))
				print(scanner)
				while response[scanner] & 192:
					scanner = self.calNum(response[scanner:scanner+2])-192*(16^(2))
				i = i + 2
				while response[scanner] != 0:
					b.append(response[scanner])
					scanner = scanner + 1
			else:
				scanner = i
				while response[scanner] != 0:
					b.append(response[scanner])
					scanner = scanner + 1
				i = scanner + 1
			answer['qname'] = self.parseName(b[1:])
			answer['type'] = self.calType(response[i+1])
			i = i+4
			answer['TTL'] = self.calTTL(response[i:i+4])
			i = i+4
			answer['RDLENGTH'] = self.calNum(response[i:i+2])
			i = i + 2
			if answer['type'] == 'A' and answer['RDLENGTH'] == 4:
				answer['ipAddress'] = self.calAddress(response[i:i+4])
				i = i+4
				answers.append(answer)
			elif answer['type'] == 'NS':
				b = []
				if response[i] & 192:
					scanner = calNum(response[i:i+2])-192*(16^(2))
					while response[scanner] & 192:
						scanner = calNum(response[scanner:scanner+2])-192*(16^(2))
					i = i + 2
					while response[scanner] != 0:
						b.append(response[scanner])
						scanner = scanner + 1
				else:
					scanner = i
					while response[scanner] != 0:
						b.append(response[scanner])
						scanner = scanner + 1
					i = scanner + 1
				answer['serverName'] = self.parseName(b[1:])
				answers.append(answer)
			elif answer['type'] == 'CNAME':
				b = []
				if response[i] & 192:
					scanner = self.calNum(response[i:i+2])-192*(16^(2))
					while response[scanner] & 192:
						scanner = self.calNum(response[scanner:scanner+2])-192*(16^(2))
					i = i + 2
					while response[scanner] != 0:
						b.append(response[scanner])
						scanner = scanner + 1
				else:
					scanner = i
					while response[scanner] != 0:
						b.append(response[scanner])
						scanner = scanner + 1
					i = scanner + 1
				answer['alias'] = self.parseName(b[1:])
				answers.append(answer)
			elif answer['type'] == 'MX':
				answer['preference'] = self.calNum(response[i:i+2])
				i = i+2
				b = []
				if response[i] & 192:
					scanner = self.calNum(response[i:i+2])-192*(16^(2))
					while response[scanner] & 192:
						scanner = self.calNum(response[scanner:scanner+2])-192*(16^(2))
					i = i + 2
					while response[scanner] != 0:
						b.append(response[scanner])
						scanner = scanner + 1
				else:
					scanner = i
					while response[scanner] != 0:
						b.append(response[scanner])
						scanner = scanner + 1
					i = scanner + 1
				answer['exchange'] = self.parseName(b[1:])
				answers.append(answer)
			else:
				print('ERROR	unexpect response:could not parse the response')
				exit()
			return i
		for r in range(self.numOfAns):
			i = parseAnswer(self.Ans,i)
			#print(i)
		for r in range(self.numAu):
			if response[i] & 192:
				i = i + 2
			else:
				scanner = i
				while response[scanner] != 0:
					scanner = scanner + 1
				i = scanner + 1
			i = i+8
			num = self.calNum(response[i:i+2])
			i = i+ num + 2
		for r in range(self.numAdd):
			i = parseAnswer(self.Add,i)
			#print(i)
		if i != len(response):
			print('ERROR	unexpect response:could not parse the response')
			exit()