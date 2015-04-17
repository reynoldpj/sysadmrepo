#!/usr/bin/python
# It doesn't require authentication details to connect to shinken. But instead
# it connects to shinken livestatus port 50000 and queries using SQL like livestatus query language
# 

import socket
import sys, re, os, time
import os.path

#Shinken server 
SERVER = "shinken.jackal.com"

#############################################################
def getlist(getstri): 
     '''
	Get lists of all alerts ( WARN, CRITICAL, UNKNOWN )
	The list can viewed from, Shinken >> Current Status >> Problems >> Services (Unhandled)
     '''
     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
     s.connect((SERVER, 50000))
     s.send(getstri)
     s.shutdown(socket.SHUT_WR)
     data = ''
     while True:
	val = s.recv(8192)
 	if not val: break	
	data = data + val
     s.close()
     return data

#############################################################
def checkExists(host, service, service_status, sinfo):
	'''
	   Checks whether a regex entry already exists in patterns.regex file 
	'''

	REGEX_FILE= 'patterns.regex'

	if not os.path.isfile(REGEX_FILE):
		os.system('touch %s' % REGEX_FILE)

	if not os.path.isdir('sysdoc'):
		os.system('mkdir sysdoc')

	# Open regex file in rw mode
	regexfile = open(REGEX_FILE,'r+')

	searchString = host+" "+service+" "+service_status+" "+sinfo
	checkcomm1="grep "+"\"^#"+host+" "+service+" "+service_status+" : sysdoc/\" "+REGEX_FILE+" >/dev/null 2>&1"
	matchFlag = False
	url = ''
	
	# Set file pointer to beginning
	regexfile.seek(0)

	# Search for matching pattern in regex file
	for line in regexfile:
		m2 = re.search(r'^(?!#)(.*)\s:\s(.*)',line)
		
		if m2:
			pattern = m2.group(1)
			url = m2.group(2)
			
			sepattern = re.compile(pattern)
			m3 = sepattern.search(searchString)

			if m3:
				matchFlag = True
				break
		else:
			print "[INFO]NO MATCH\n[INFO]M2 is NONE"

	# Print message if no match is found for searchstring
	if not matchFlag:
		# Seek towards the end of regex file and write down the pattern (if its not present)
		retval=os.system(checkcomm1)
		
		if retval != 0:
			regexfile.seek(0,2)
			time.sleep(0.09)
			url="sysdoc/"+str(time.time())+".txt"
			regexfile.write(host+" "+service+" "+service_status+" : "+url+"\n")
			os.system('touch '+url) # Create file

	# close file
	regexfile.close()

	return matchFlag, url
	
	


#############################################################
def main():

	queryp1 = "GET services\n"
	queryp2 = "Columns: host_display_name state display_name plugin_output\n"
	queryp3 = "Filter: state = 1\nFilter: state = 2\nFilter: state = 3\nOr: 3\n"
	queryp4 = "Filter: notifications_enabled != 0"

	query = "%s%s%s%s" % (queryp1, queryp2, queryp3, queryp4)	

	data	= 	getlist(query)
	list1	=	data.split('\n')

	if len(list1) == 0 :
		print "0 ALERTS/WARNINGS !!!"
		sys.exit(0)

	try:
		list1.remove('')
	except ValueError,e:
		print "[EXCEPTION CAUGHT] ValueError: %s" % e.message
		print e

	# For storing columns
	tuple1=[]
	j = 0

	for i in list1:		
		try:
			l2 = i.split(';')

			host = l2[0]
		
			if int(l2[1]) == 1:
				service_status    = 'WARN'
			elif int(l2[1]) == 2:
				service_status    = 'CRITICAL'
			elif int(l2[1]) == 3:
				service_status    = 'UNKNOWN'

			#service name
			service = l2[2]
			#status info
			sinfo	     = l2[3]		

			matchFlag, url	=	checkExists(host, service, service_status, sinfo)

			# Save all entries in lists and tuples
			listAll = (host,service,service_status,sinfo,matchFlag,url)
			tuple1.insert(j,listAll) 

			j = j + 1

		except Exception,e:
			print "[EXCEPTION] Iteration value (i) : %s " % i	
			print e




	# First print all elements where matchFlag=False <=> No sysdoc entry before
	for i in range(len(list1)):
		if not tuple1[i][4]:
			print "------------------------------------------------"
			print "Host: %s\nService: %s"%(tuple1[i][0],tuple1[i][1])
			print "Service Status: %s\nStatus info: %s"%(tuple1[i][2],tuple1[i][3])
			print "KB URL: %s"%(tuple1[i][5])
			print "[NOTICE] KB Entry is newly created and empty."
			print "[NOTICE] Add relevant entry in %s"%(tuple1[i][5])
			print "------------------------------------------------"
		
	# 
	for i in range(len(list1)):
		if tuple1[i][4]:
			print "------------------------------------------------"
			print "Host: %s\nService: %s"%(tuple1[i][0],tuple1[i][1])
			print "Service Status: %s\nStatus info: %s"%(tuple1[i][2],tuple1[i][3])
			print "KB URL: %s"%(tuple1[i][5])
			print "------------------------------------------------"	

	del list1
	del tuple1


#############################################################

if __name__ == "__main__":
	try:
		main()
	except Exception,e:
		print "[EXCEPTION CAUGHT] Inside main() : %s" % e.message
		print e
