#!/usr/bin/env python

import re
import os
import sys

try:
    import paramiko
except ImportError, e:
    print "Please install the Debian package python-paramiko"
    sys.exit(1)

###########################
# Classes

class SSHandler():
    """A custom wrapper class for paramiko"""
    def __init__(self, servername,user='root',password=''):
        """Accepts servername,user and password"""
        self.servername = servername
        self.user    = user
        self.password    = password        
        self.retval    = None
        self.ssh    = None
        self.output    = ''
        self.outerr    = ''

        self.connect()

    def connect(self):
        """Called right after the class object is instantiated"""
        if isinstance(self.ssh, paramiko.SSHClient):
            raise SSHandlerConnectError("Disconnect before trying again")

        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(hostname=self.servername,username=self.user,password=self.password)
        except Exception,e:
            raise SSHandlerConnectError("Failed to SSH to server %s" % self.servername)

    def disconnect(self):
        """Closes ssh connection to server"""
        if isinstance(self.ssh, paramiko.SSHClient):
            self.ssh.close()
        else:
            raise SSHandlerConnectError("Not connected")

    def executecmd(self, command):
        """Receives the command string to be executed on server and saves the 
           values of exitcode, output and stderr to be queried later using 
           getExitcode(), getStdout(), getStderr() functions """
        if not isinstance(self.ssh, paramiko.SSHClient):
            raise SSHandlerConnectError("Try connecting to server first using connect()")

        checkretval = "echo $?"
        stin,stout,ster = self.ssh.exec_command("%s ; %s" % (command, checkretval))
        
        output = stout.readlines()
        outerr = ster.readlines()

        try:
            if len(output)>0:
                self.retval = int(output.pop(len(output)-1).strip())
        except IndexError,e:
            print "Unable to get exit code of command %s" % command
            print "Details: %s" % e.__str__()
            print "Output: %s" % ''.join(output)
        
        self.output = ''.join(output)
        self.outerr = ''.join(outerr)

        try:        
            stin.close()
            stout.close()
            ster.close()
        except Exception,e:
            print "Exception occured while closing streams: %s" % e.__str__()
        


    def getExitcode(self):
        """returns the exit code
           Call this function after executecmd() to get the exit value"""
        return self.retval


    def getStdout(self):
        """Call this function after executecmd() to get the stdout"""
        return self.output

    def getStderr(self):
        """Call this function after executecmd() to get the stderr"""
        return self.outerr        




class SSHandlerConnectError(Exception):
    """Raised when ssh connection failure to server"""
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return repr(self.value)        