#!/usr/bin/env python2.7
# andres leon: updates the Arduino board with a new zero point to calibrate current readings for the current sensor.
#RUN this when the current readings from the sensor are wildly incorrect.
import serial
import sys
import time
import logging, json

logger = logging.getLogger('current_sensor_update_zero_point')
hdlr = logging.FileHandler('/home/pi/current_sensor_update_zero_point.log')
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

new_zero_point = 0.0

if len(sys.argv) == 2:
	#print (" -- " + str(sys.argv[1]) + " -- " )
	try:
		new_zero_point = int(sys.argv[1]) + 1 #this checks if it's a number. if it fails then pass, if works then write to serial.
	except: #not a number
		pass	

try:
	if (new_zero_point != 0.0):#a new value needs to be written to the Arduino.
		ser = serial.Serial('/dev/ttyUSB2', 115200)
		time.sleep(3)	#give Arduino time to reset...
		#print("writing " + str( sys.argv[1] ) + " to arduino memory.")
		#print ( str( ser.write( str( sys.argv[1] ) + '\n' ) ) + " written to Arduino!" )
		ser.write( str( sys.argv[1] ) + '\n' )
		#ser.close()
		print(new_zero_point)
		
except Exception, e:
	PrintException()		