#!/usr/bin/env python2.7
#andres leon: this script runs on @reboot and checks the db for status updates from the web interface
# then updates the arduino to turn the inverter on or off.
import sys
import RPi.GPIO as GPIO
import time
import logging, json
import os
import MySQLdb
import serial
import subprocess


logger = logging.getLogger('fancontroller')
hdlr = logging.FileHandler('/home/pi/inverter_db_monitor.log')
formatter = logging.Formatter("%(asctime)s     %(levelname)s     %(message)s")
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.WARNING)

inverter_relay = 1;

def PrintException():
	exc_type, exc_obj, tb = sys.exc_info()
	f = tb.tb_frame
	lineno = tb.tb_lineno
	filename = f.f_code.co_filename
	linecache.checkcache(filename)
	line = linecache.getline(filename, lineno, f.f_globals)
	logger.error('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

def getRelaySettingFromDB():
	returnval = "o"
	try:
		db = MySQLdb.connect(host= "localhost", user="xx", passwd="yy", db="solardata")	
		cur = db.cursor()
		cur.execute("SELECT setting, value FROM settings WHERE setting LIKE 'inverter%'")
		for row in cur.fetchall():
			#print "'" + row[0] + "' : '" + row[1] + "'"
			if ( row[0] == "inverter_relay" ):
				if ( int(row[1]) == 1 ):
					returnval = "c"
				else:
					returnval = "o"

		db.close()
		return returnval
		
	except Exception, e:
		PrintException()

def UpdateDBFromSetting( newSetting ):
	try:
		db = MySQLdb.connect(host= "localhost", user="xx", passwd="yy", db="solardata")
		sqlcmd = "UPDATE settings set value = " + newSetting + " WHERE setting = 'inverter_relay'; ";
		cursor = db.cursor()
		cursor.execute(sqlcmd)
		# Commit your changes in the database
		db.commit()
		db.close()
	except Exception, e:
		PrintException()
		

def getSetCurrRelayStatus( cmd ):
	returnval = ""
	try:
		command = "python /home/pi/inverter_relay_control01.py " + str(cmd)
		process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
		process.wait()
		#print process.returncode
		returnval = process.stdout.read(1)
		returnval = returnval.strip()
		return returnval
		
	except Exception, e:
		PrintException()
		return returnval
		
		
#sleep for 20 seconds before loop begins to allow startup tasks to end.
time.sleep(20)

while True:
	try:
		while True:
			dbRelaySetting = getRelaySettingFromDB()
			print("dbRelaySetting = " + dbRelaySetting)
			currRelayStatus = getSetCurrRelayStatus("q")
			print("currRelayStatus = " + currRelayStatus)
		
			if ( dbRelaySetting != currRelayStatus ):
				getSetCurrRelayStatus(dbRelaySetting)
				print("inverter setting updated.")
				
			time.sleep(3)
		
	except Exception, e:
		PrintException()
	
	
	
		