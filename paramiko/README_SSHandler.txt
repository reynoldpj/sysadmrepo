README
=========

This class is a wrapper around python "paramiko" class.

Usage of SSHandler class:



$ python
Python 2.7.3 (default, Jan  2 2013, 13:56:14) 
[GCC 4.7.2] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import SSHandler
>>> 
>>> 
>>> sshcon = SSHandler.SSHandler(servername='logs.jackal.com', user='root', password='')
>>> sshcon.executecmd('uptime')
>>> sshcon.getExitcode()
0
>>> sshcon.getStdout()
u' 15:01:09 up 231 days,  6:00, 19 users,  load average: 5.70, 5.24, 4.68\n'
>>> 
>>> sshcon.executecmd('goby')
>>> sshcon.getExitcode()
127
>>> sshcon.getExitcode()
127
>>> sshcon.getStderr()
u'bash: goby: command not found\n'
>>> 
>>> 
>>> sshcon.disconnect()
>>> 

