#!/usr/bin/env python2.7
#andres leon: this script is called from the main sollarcontrollerdata_mysqlxx.py and gets data from the
#current sensor which is connected to its own Arduino board. it delivers a json dataset that the other
#scripts can decipher and use.
import json
import serial
import sys
import time

ser = serial.Serial('/dev/ttyUSB2', 115200)

for x in range(1,3):
	jsondata =  str(ser.readline().strip())	
	#print ("'" + jsondata + "'")
	
raw = 0.0
zero_point = 0.0
current = 0.0
avgSamples = 0.0
	
jsondata = ""
try:
	print( str( ser.readline().strip() ) )
except Exception as e:
	print str("ERROR!")


	
