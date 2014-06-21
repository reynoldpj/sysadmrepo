#!/usr/bin/python
'''
Tool to find out top 10 email users whose emails are in postfix deferred queue
'''

import commands, re, sys

(exitstatus, outtext) = commands.getstatusoutput('find /var/spool/postfix/deferred -type f')

if exitstatus != 0:
    raise SystemExit('Unable to execute cmd "find /var/spool/postfix/deferred -type f"')

emaildict = {}

for fname in outtext.split('\n'):
    fp = open(fname, 'rb')
    head = fp.read(512) 
    m1 = re.search(r'.*sasl_username=(.*?@.*?)[A-Z].*', head)
    if m1:
        email = m1.group(1)
    else:
        email = 'MAILER-DAEMON'
    if emaildict.has_key(email):
        emaildict[email] += 1  
    else:
        emaildict[email] = 1   
    fp.close()

emaillist = sorted(emaildict.items(), key=lambda x: x[1], reverse=True)
for i in range(0,10):
    print emaillist[i]
