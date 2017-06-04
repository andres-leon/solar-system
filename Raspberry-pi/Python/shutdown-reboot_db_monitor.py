#!/usr/bin/env python2.7
#andres leon: this script starts on @reboot and  continually runs to check the db for status updates from the web interface
# then shuts down or reboots Pi based on status of the settings in the db
import sys
import time
import logging, json
import os
import MySQLdb
import subprocess
import linecache

#CURRENT_TIMESTAMP
logger = logging.getLogger('shutdown-reboot_db_monitor')
hdlr = logging.FileHandler('/home/pi/shutdown-reboot_db_monitor.log')
formatter = logging.Formatter("%(asctime)s     %(levelname)s     %(message)s")
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.WARNING)

db_shutdown = 0
db_reboot = 0
cmd_to_shutdown_or_reboot_sent = 0

def PrintException():
	exc_type, exc_obj, tb = sys.exc_info()
	f = tb.tb_frame
	lineno = tb.tb_lineno
	filename = f.f_code.co_filename
	linecache.checkcache(filename)
	line = linecache.getline(filename, lineno, f.f_globals)
	logger.error('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

def getSettingFromDB():
	global db_shutdown
	global db_reboot	
	try:
		db = MySQLdb.connect(host= "localhost", user="xx", passwd="yy", db="solardata")	
		cur = db.cursor()
		cur.execute("SELECT * FROM settings WHERE setting = 'reboot' or setting = 'shutdown'")
		for row in cur.fetchall():
			#print "'" + row[0] + "' : '" + row[1] + "'"
			if ( row[0] == "reboot" ):
				db_reboot = int(row[1])
			else:
				db_shutdown = int(row[1])
				
		db.close()
		
	except Exception, e:
		PrintException()

def UpdateDBSetting(setting, new_value ):
	try:
		db = MySQLdb.connect(host= "localhost", user="xx", passwd="yy", db="solardata")
		sqlcmd = "UPDATE settings set value = " + str(new_value) + ", datetimeupdated = NOW() WHERE setting = '" + setting + "'; ";
		cursor = db.cursor()
		cursor.execute(sqlcmd)
		# Commit your changes in the database
		db.commit()
		db.close()
	except Exception, e:
		PrintException()
		

def SendCmdToPi(cmd):
	if (cmd == 'reboot'): 
		os.system("sudo shutdown -r 1")
		print("rebooting")
	elif (cmd == 'shutdown'): 
		os.system("sudo shutdown -H 1")
		print("shutting down now")


#sleep for 20 seconds before loop begins to allow startup tasks to end.
time.sleep(20)

while True:
	try:
		while True:
			#1. get setting values from db
			#2. if either value is 1, then 
			#	update db so settings are 0
			#	send command
			if ( cmd_to_shutdown_or_reboot_sent == 0 ):
				print("getting data from db...")
				getSettingFromDB()
				print("got it. shutdown is " + str(db_shutdown) + " and reboot is " + str(db_reboot))
				
				if ( (db_shutdown == 1) ):
					print("shutdown requested!")
					UpdateDBSetting( 'shutdown', 0 )
					time.sleep(2)
					SendCmdToPi( 'shutdown' )
					print("shutdown command sent!")
					cmd_to_shutdown_or_reboot_sent = 1
					
				if ( (db_reboot  == 1) ):
					print("reboot requested!")
					UpdateDBSetting( 'reboot', 0 )
					time.sleep(2)
					SendCmdToPi( 'reboot' ) 
					print("reboot command sent!")
					cmd_to_shutdown_or_reboot_sent = 1				
				
				
			else:
				print("command to shutdown or reboot has been sent. Don't check DB anymore.")
			
			time.sleep(3)
			
	except Exception, e:
		PrintException()
	
	
	
		