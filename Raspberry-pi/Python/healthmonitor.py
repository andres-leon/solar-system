#!/usr/bin/env python2.7
#andres leon: this script runs from cron every x amount of minutes and checks
# if new data has been entered into the stats table. if a period of time has
# passed with no new data in, it will reboot the system.

import sys
import time
import logging, json
import os
import MySQLdb
import subprocess
import linecache
import datetime
import time
from dateutil.parser import parse

logger = logging.getLogger('healthmonitor')
hdlr = logging.FileHandler('/home/pi/healthmonitor.log')
formatter = logging.Formatter("%(asctime)s     %(levelname)s     %(message)s")
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.WARNING)


def PrintException():
	exc_type, exc_obj, tb = sys.exc_info()
	f = tb.tb_frame
	lineno = tb.tb_lineno
	filename = f.f_code.co_filename
	linecache.checkcache(filename)
	line = linecache.getline(filename, lineno, f.f_globals)
	logger.error('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

def SendCmdToPi(cmd):
	if (cmd == 'reboot'): 
		os.system("sudo reboot")
		print("rebooting")
	elif (cmd == 'shutdown'): 
		os.system("sudo halt")
		print("shutting down now")

	
def GetLastEntryFromDB():
	try:
		db = MySQLdb.connect(host= "localhost", user="xx", passwd="yy", db="solardata")	
		cur = db.cursor()
		cur.execute("SELECT datetimestamp from stats order by datetimestamp desc limit 1")
		row = cur.fetchone()
		
		return row[0]
		
		db.close()
		
	except Exception, e:
		print("error. check log. " + str(e))
		PrintException()
		return 0


try:
	print("starting healthmonitor")
	now = datetime.datetime.now()
	print ("current date time is " + str(now) )
	lastentrydate = GetLastEntryFromDB()
	print ("last entry was " + str(lastentrydate))
	
	#convert to unix time
	now_ts = time.mktime( now.timetuple() )
	lastentrydate_ts = time.mktime( lastentrydate.timetuple() )
	
	timediff = int( now_ts - lastentrydate_ts ) / 60
	
	#lastentrydate = parse( lastDBentry )
	#print ("last entry TO DATE was " + str(lastentrydate))
	print ("difference in minutes: " + str( timediff ) )
		
	if ( timediff > 5 ):	#at least 5 minutes have passed since last data in.
		print ("WARNING! No new data entered in the last 5 minutes. Rebooting.")
		logger.error("No new data entered in the last 5 minutes. Rebooting.")
		SendCmdToPi('reboot')
	else:
		#logger.error("ok! data is resent. we're good.")
		print ("ok! data is resent. we're good.")
		
except Exception, e:
	print("error. check log. " + str(e))
	PrintException()
	
	
	
	