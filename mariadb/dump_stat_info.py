#!/usr/bin/python

import MySQLdb
import json
from ConfigParser import ConfigParser

LIMIT = 7
user_and_client_stat_columns = ('TOTAL_CONNECTIONS', 'CONCURRENT_CONNECTIONS', 'CONNECTED_TIME', 'BUSY_TIME', 'CPU_TIME', 'BYTES_RECEIVED', 'BYTES_SENT', 'BINLOG_BYTES_WRITTEN', 'ROWS_READ', 'ROWS_SENT', 'ROWS_DELETED', 'ROWS_INSERTED', 'ROWS_UPDATED', 'SELECT_COMMANDS', 'UPDATE_COMMANDS', 'OTHER_COMMANDS', 'COMMIT_TRANSACTIONS', 'ROLLBACK_TRANSACTIONS', 'DENIED_CONNECTIONS', 'LOST_CONNECTIONS', 'ACCESS_DENIED', 'EMPTY_QUERIES')

# data holding dicts
data_user_stat = {}
data_client_stat = {}
data_index_stat = {}
data_table_stat = {}

try:

    # Configuration parsers
    cfg  = ConfigParser()
    cfg.read('/root/.my.cnf')

    # Connect to mysql db and get cursor info
    db  =   MySQLdb.connect(host = cfg.get(section='client',option='host'), db = 'INFORMATION_SCHEMA', user = cfg.get(section='client',option='user'), passwd = cfg.get(section='client',option ='password'))
    cur = db.cursor()

    #gather USER_STATISTICS and CLIENT_STATISTICS info
    for col in user_and_client_stat_columns:
        cur.execute("SELECT USER,%s FROM USER_STATISTICS ORDER BY %s DESC LIMIT %d" % (col, col, LIMIT))
        data_user_stat[col] = cur.fetchall()
        cur.execute("SELECT CLIENT,%s FROM CLIENT_STATISTICS ORDER BY %s DESC LIMIT %d" % (col, col, LIMIT))
        data_client_stat[col] = cur.fetchall()

    # gather INDEX_STATISTICS
    cur.execute("select TABLE_SCHEMA, TABLE_NAME, INDEX_NAME, ROWS_READ from INDEX_STATISTICS order by ROWS_READ desc limit %d" % LIMIT)
    data_index_stat['ROWS_READ'] = cur.fetchall()

    # gather TABLE_STATISTICS
    cur.execute("select TABLE_SCHEMA,TABLE_NAME,ROWS_CHANGED from TABLE_STATISTICS order by ROWS_CHANGED desc limit %d" % LIMIT)
    data_table_stat['ROWS_CHANGED'] = cur.fetchall()

    cur.execute("select TABLE_SCHEMA,TABLE_NAME,ROWS_READ from TABLE_STATISTICS order by ROWS_READ desc limit %d" % LIMIT)
    data_table_stat['ROWS_READ'] = cur.fetchall()

    cur.execute("select TABLE_SCHEMA,TABLE_NAME,ROWS_CHANGED_X_INDEXES from TABLE_STATISTICS order by ROWS_CHANGED_X_INDEXES desc limit %d" % LIMIT)
    data_table_stat['ROWS_CHANGED_X_INDEXES'] = cur.fetchall()

    cur.execute("select TABLE_SCHEMA,TABLE_NAME,ROWS_READ from TABLE_STATISTICS where TABLE_NAME like '%s' order by ROWS_READ desc limit %d" % ("%comments%",LIMIT))
    data_table_stat['ROWS_READ_comments'] = cur.fetchall()

    cur.execute("select TABLE_SCHEMA,TABLE_NAME,ROWS_CHANGED from TABLE_STATISTICS where TABLE_NAME REGEXP 'gast|guest|gasten|gjeste|gbook|gaest' order by ROWS_CHANGED desc limit %d" % LIMIT)
    data_table_stat['ROWS_CHANGED_guestbook'] = cur.fetchall()

    querystring = {'ROWS_CHANGED_comments':'%comments%' , 'ROWS_CHANGED_phpbbuser': 'phpbb%user%', 'ROWS_CHANGED_phpbbloginattempt':'phpbb%login%attempt%','ROWS_CHANGED_phpbbpost': 'phpbb%post%', 'ROWS_CHANGED_wpcomments': '%wp%comments%', 'ROWS_CHANGED_wpposts':'%wp%posts%', 'ROWS_CHANGED_wpusers': '%wp%users%','ROWS_CHANGED_users': 'users%', 'ROWS_CHANGED_session':'%session%', 'ROWS_CHANGED_friend': '%friend%' }


    for key in querystring.keys():
        cur.execute("select TABLE_SCHEMA,TABLE_NAME,ROWS_CHANGED from TABLE_STATISTICS where TABLE_NAME like '%s' order by ROWS_CHANGED desc limit %d" % (querystring[key], LIMIT))
        data_table_stat[key] = cur.fetchall()    
    
    print json.dumps({'USER_STATISTICS':  data_user_stat, 'CLIENT_STATISTICS': data_client_stat, 'INDEX_STATISTICS': data_index_stat ,'TABLE_STATISTICS': data_table_stat})

except Exception,e:
    print e.message

finally:
    #close db connection
    cur.close()
    db.close()
