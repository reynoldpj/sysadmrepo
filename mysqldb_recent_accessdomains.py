#!/usr/bin/env python

import commands
import sqlite3
import re

from datetime import datetime
from argparse import ArgumentParser

class ManageSqlite(object):
    def __init__(self, sqlitefilename):
        self.sqlitefilename = sqlitefilename
        
        self.conn = sqlite3.connect(self.sqlitefilename, timeout=86400, detect_types=sqlite3.PARSE_DECLTYPES, isolation_level=None, check_same_thread=False) 
        self.cur  = self.conn.cursor()
        
        self.cur.executescript("""
            create table if not exists recentaccessdatabases(
                starttime timestamp,
                domain varchar,
                tablename varchar,
                size bigint,
                mysqlserver varchar
            );
            
            create index if not exists starttime_index on recentaccessdatabases (starttime);
            create index if not exists domain_index on recentaccessdatabases (domain);
            create index if not exists tablename_index on recentaccessdatabases (tablename);
            
            create table if not exists statusinfo(
                starttime timestamp,
                endtime   timestamp,
                mysqlserver varchar,
                status varchar                
            );      
            
            create index if not exists status_starttime_index on statusinfo (starttime);
            create index if not exists status_endtime_index on statusinfo (endtime);
            create index if not exists status_index on statusinfo (status);
            
        """)
        
    def insertValue(self, datetime1, domain, table, size, mysqlserver):
        self.cur.execute('insert into recentaccessdatabases values(?,?,?,?,?)', (datetime1, domain, table, size, mysqlserver))    
        
    
    def updateStatus(self, starttime, statusmsg, mysqlserver, endtime=None):
        if starttime and endtime is None:
            self.cur.execute('insert into statusinfo(starttime,status,mysqlserver) values(?,?,?)',\
                             (starttime, statusmsg, mysqlserver))
        elif endtime and starttime:
            self.cur.execute('update statusinfo set endtime=?,status=? where status=? and mysqlserver=? and starttime=?',\
                             (endtime, statusmsg, "STARTED", mysqlserver, starttime))
    
    def getDetails(self, sqlquery):
        '''
        accepts an sql query which will be run against the database table and the 
        results are returned as a json object
        '''        
        pass 
    
    

class GatherInfo(ManageSqlite):
    '''
    init function
    '''
    def __init__(self, lastNmin, sqliteFname, mysqlserver):
        super(GatherInfo, self).__init__(sqliteFname)
        
        self.mysqlserver = mysqlserver
        self.min = lastNmin
        self.command = "find /customers/[0-9a-f]/[0-9a-f]/[0-9a-f]/ -type f \
                        -name '*[.ibd|.MYD]' -amin -%d -exec du -s {} \;" % self.min
        
        
    def findRecentaccessedTables(self):
        self.starttime = datetime.now()
        
        self.updateStatus(starttime=self.starttime, statusmsg="STARTED", mysqlserver=self.mysqlserver) 
        
        (exitstatus, outtext) = commands.getstatusoutput(self.command)
        
        self.endtime   = datetime.now()
        
        if exitstatus == 0 and len(outtext) > 0:
            list1 = outtext.split('\n')
            
            while True:
                try:
                    m1 = re.search(r'([0-9]+)\t\/customers.*\/(.*?)\/mysql\.mysql\/(.*?)\.[MYD|ibd]', list1.pop())
                    
                    sizeinkb = m1.group(1)
                    domain   = m1.group(2)
                    tablename = m1.group(3)        
                    
                    self.insertValue(self.starttime, domain, tablename, sizeinkb, self.mysqlserver)                            
                except IndexError:
                    break
                
            self.updateStatus(statusmsg="COMPLETED", mysqlserver=self.mysqlserver, endtime=self.endtime, starttime=self.starttime)
        else:
            self.updateStatus(statusmsg="FAILED", mysqlserver=self.mysqlserver, endtime=self.endtime, starttime=self.starttime)          
        
        
        
        
if __name__ == "__main__":
    parser = ArgumentParser(prog="findrecentaccessedDatabases", usage="%(prog)s [options]", \
                            description="Program used to find database files which were accessed in the last N minutes and insert the db name, table name and its size to a sqlite table along with the timestamp", \
                            version="1.0")
    
    parser.add_argument("--lastNmin", type=int, default=60,\
                        help="Find db files which were accessed last N min ago. Specifies the last 'N' minute")
    parser.add_argument("--sqlitefile", type=str, required=True,help="sqlite file where result are stored")
    parser.add_argument("--mysqlservername", type=str, required=True, help="mysql server name")
    
    args = parser.parse_args()
    
    gInfo = GatherInfo(lastNmin=args.lastNmin, sqliteFname=args.sqlitefile, mysqlserver=args.mysqlservername)
    gInfo.findRecentaccessedTables()
