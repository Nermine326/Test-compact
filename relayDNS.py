
# MySQL
config_dbhost = "localhost"
config_dbuser = "root2"
config_dbpasswd = ""
config_dbname = "DNSdata"
config_dbtable = "dnscache"

# Relay DNS
config_dnsrelay = ['1.1.1.1']
config_dnstimeout = 3
# Server DNS
config_dnsport = 53
config_delayerror = 1


#=============================
# SQL
#=============================


import sys, subprocess
import socket
import dns.resolver
from dns.exception import DNSException
import time
import MySQLdb

class DNSClient:
	def __init__(self, nameservers, timeout):
		self.res = dns.resolver.Resolver()
		self.res.nameservers = nameservers
		self.res.timeout = timeout

	def dnsResolve(self, domain):
		res = 0
		try:
			answer = self.res.query(domain, "A")
			res = "%s" % answer[0]
		except dns.resolver.NoAnswer:
			print "Error: No AAAA record for", dnss.domain," ", data
		except dns.resolver.NXDOMAIN:
			print "Error: The name ", dnss.domain, " does not exist"
		except DNSException:
			print 'Error: DNS Exception: ', dnss.domain
		return res

class DNSServer:
	def __init__(self, port, delayerror):
		self.udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		try:
			self.udps.bind(('',port))
		except:
			print "Error: Port ",port," already used (wait ",delayerror," seconds before close)"
			time.sleep(delayerror)
			sys.exit(0)

	def recieveQuery(self):
		return self.udps.recvfrom(1024)

	def sendQuery(self, answer, addr):
		self.udps.sendto(answer, addr)

	def close(self):
		self.udps.close()
		print 'Close'

class DNSQuery:
	def __init__(self, data):
		try:
			self.data=data
			self.domain=''
			#tipo : Opcode query type =  [ standard (0) | inverse (1) | server status (2) ]
			tipo = (ord(data[2]) >> 3) & 15	 # Opcode bits
			if tipo == 0:					 # Standard query
				ini=12
				lon=ord(data[ini])
				while lon != 0:
					self.domain+=data[ini+1:ini+lon+1]+'.'
					ini+=lon+1
					lon=ord(data[ini])
		except:
			return ""

	def dnsAnswer(self, ip):
		packet=''
		if self.domain and len(self.domain) > 0:
			packet+=self.data[:2] + "\x81\x80"
			packet+=self.data[4:6] + self.data[4:6] + '\x00\x00\x00\x00'	 # Questions and Answers Counts
			packet+=self.data[12:]											 # Original Domain Name Question
			packet+='\xc0\x0c'												 # Pointer to domain name
			packet+='\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04'				 # Response type, ttl and resource data length -> 4 bytes
			try:
				packet+=str.join('',map(lambda x: chr(int(x)), ip.split('.'))) 	 # 4bytes of IP
			except:
				return ""
		return packet

class SQLConnexion:
	def __init__(self, dbhost, dbuser, dbpasswd, dbname, dbtable):
		try:
			self.db = MySQLdb.connect(host=dbhost, user=dbuser, passwd=dbpasswd, db=dbname)
			self.cur = self.db.cursor()
			self.tablecache = dbtable    
		except:
			print "Error connexion database MySQL"
			time.sleep(5)
			sys.exit(0)

	def close(self):
		self.cur.close()
		self.db.close()

	def sqlquery(self, query):
		try:
			self.cur.execute(query)
		except MySQLdb.Error, e:
			print "Error %d: %s" % (e.args[0], e.args[1])
			print "Query SQL \n %s" % query
			self.db.rollback()
			time.sleep(5)

	def sqlgetdomain(self, domain):
		res = 0
		self.sqlquery("SELECT * FROM `"+self.tablecache+"` WHERE `domain` = '"+domain[:-1]+"';")
		resultcount = int(self.cur.rowcount)
		if resultcount > 0:
			q = self.cur.fetchall()
			ip = q[0][1]
			banned = q[0][2]
			if banned == 1:
				res = "127.0.0.1"
			else:
				res = ip
		return res

	def sqlsetdomain(self, domain, ip):
	   self.sqlquery("INSERT INTO `"+self.tablecache+"` (`domain` ,`ip` ,`banned`) VALUES ('"+domain[:-1]+"', '"+ip+"', '0');")
	   self.db.commit()

if __name__ == '__main__':
	print 'Started'
	db = SQLConnexion(config_dbhost, config_dbuser, config_dbpasswd, config_dbname, config_dbtable) # SQL Connexion
	dnsc = DNSClient(config_dnsrelay, config_dnstimeout) # DNS Client
	udps = DNSServer(config_dnsport, config_delayerror) # DNS Server
	try:
		while 1:
			data, addr = udps.recieveQuery() # recieve UDP data (usually on port 53)
			dnss = DNSQuery(data) # Parse DNS query
			if ".in-addr.arpa." in dnss.domain:
				ip = dnss.domain.split(".") 
				answer = ip[3]+"."+ip[2]+"."+ip[1]+"."+ip[0]
			else:
				answer = db.sqlgetdomain(dnss.domain) # Check if domain exists in database
			if answer != 0: # if domain exists
				udps.sendQuery(dnss.dnsAnswer(answer), addr) # Send IP to the user
			else: # if it's a new domain
				print "New domain:"
				answer = dnsc.dnsResolve(dnss.domain) # Ask the Primary DNS server
				if answer != 0:
					udps.sendQuery(dnss.dnsAnswer(answer), addr) # Send IP to the user
					db.sqlsetdomain(dnss.domain, answer) # Add IP in database
				else:
					db.sqlsetdomain(dnss.domain, "127.0.0.1") # Add IP in database
			# Display log
			heure = time.strftime('%d.%m.%y %H:%M',time.localtime())
			print '[%s] %s %s <- %s' % (heure, addr, answer, dnss.domain)
	except KeyboardInterrupt:
		udps.close()
