#!/usr/bin/env python2.7
#this script is meant to calibrate the current sensor's zero point
#by shutting off power to the inverter, then taking several measurements
#from the sensor, getting the average, and then applying this average
#as the new zero point. 

import os, logging, sys
import subprocess
import json
import serial
import time
import MySQLdb
import time
import linecache


logger = logging.getLogger('current_sensor_calibrate')
hdlr = logging.FileHandler('/home/pi/current_sensor_calibrate.log')
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

def getRelaySettingFromDB():
	try:
		db = MySQLdb.connect(host= "localhost", user="root", passwd="root", db="solardata")	
		cur = db.cursor()
		cur.execute("SELECT setting, value FROM settings WHERE setting LIKE 'inverter%'")
		for row in cur.fetchall():
			if ( row[0] == "inverter_relay" ):
				return int(row[1])

		db.close()
		
	except Exception, e:
		PrintException()
		return 0

def UpdateDBFromSetting( newSetting ):
	try:
		db = MySQLdb.connect(host= "localhost", user="root", passwd="root", db="solardata")
		sqlcmd = "UPDATE settings set value = " + str( newSetting ) + " WHERE setting = 'inverter_relay'; ";
		cursor = db.cursor()
		cursor.execute(sqlcmd)
		# Commit your changes in the database
		db.commit()
		db.close()
		
	except Exception, e:
		PrintException()

def SensorReading():
	raw = 0.0
	zero_point = 0.0
	current = 0.0
	avgSamples = 0.0
	try:
		ser = serial.Serial('/dev/ttyUSB2', 115200)
		for x in range(1,3):
			jsondata =  str(ser.readline().strip()) #clear buffer of bad data
			
		jsondata = ""
		loopcount = 1
		while (loopcount <= 10):
			print ("start loopcount " + str(loopcount))
			jsondata =  str(ser.readline().strip())
			try:
				data = json.loads(jsondata)
			except:
				if (loopcount > 1):
					loopcount -= 1	#go back once to get a new reading			
					print("error reading from sensor... loopcount= " + str(loopcount))
					
			avgSamples += data["avgSamples"]
			loopcount += 1			
			
			
		avgSamples = ( avgSamples / 10.0 )
		ser.close()
		
		return avgSamples
			
	except Exception, e:
		PrintException()
		return 0.0

try:
			
	#1. get curernt status of inverter relay
	print("Acquiring inverter status...")
	prev_inverter_relay_status = getRelaySettingFromDB()
	
	print("current inverter status is " + str(prev_inverter_relay_status))
	
	if (prev_inverter_relay_status):
		#2. turn off relay
		print("Turning off inverter.")
		UpdateDBFromSetting(0)
		print("Command sent. Waiting 15 secs. to apply...")
		time.sleep(15) #give it 10 seconds for database to update, polling tool to read new status and then apply.
		print("15 secs have passed. ")
	else:
		print("no need to turn off inverter.")

	#3. get sensor average (10 reads)
	print("getting new average sensor value...")
	new_zero_point = int( SensorReading() )
	
	if ( new_zero_point != 0 ):	
		print( "Acquired. new val is " + str( new_zero_point ) )
		#4. apply new zero point
		print( "Writing new val to Arduino: " + str( new_zero_point ) )
		applied_zero_point = subprocess.check_output(['python','/home/pi/current_sensor_update_zero_point.py', str( new_zero_point )])		
		print ("New zero point written to Arduino..." + str( applied_zero_point ) )
		
	else:	#could not get a new reading...
		print( "could not acquire new reading from sensor." )
	

	#5. apply previous state of relay
	print ( "Applying previous status to Inverter, " + str(prev_inverter_relay_status) )
	UpdateDBFromSetting( str( prev_inverter_relay_status ) )
	print ( "Previous Inverter setting has been applied. DONE!" )
	
except Exception, e:
	print("there was an error. check log for details.")
	PrintException()
	
