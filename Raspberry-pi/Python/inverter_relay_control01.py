#!/usr/bin/env python2.7
#andres leon: this script is called from inverter_db_control.py. 
# it sends a command to the Arduino running the solid state relay updating the running
# status of the relay. The Arduino keeps this in memory in case the Raspberry Pi is off
# the relay will contin ue providing power to the Inverter if that was the last status it
# had from the Pi.
# In essence, this shuts down the inverter when the parameter it receives is 'o' (open)
# or turns it on when it receives an 'c' (close).
import sys
#import paho.mqtt.client as mqtt
#import RPi.GPIO as GPIO
import time
import logging, json
import os
import serial

logger = logging.getLogger('inverter_serial_control')
hdlr = logging.FileHandler('/home/pi/inverter_relay_control01.log')
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


#serialPIN = 21
#sleepTimeSecs = 15

#GPIO.setmode(GPIO.BCM)
#GPIO.setup(serialPIN, GPIO.OUT)	
sleepTimeSecs = 10

#print("program started.")
#while (True):
try:
	serial = serial.Serial('/dev/ttyUSB1', 115200)
	#print("waiting for arduino to reset...")
	time.sleep(2) 
	#print("DONE!")
	#print("number of args: " + str(len(sys.argv)))
	if len(sys.argv) == 2:
                cmdNewserialStat = sys.argv[1]
                if cmdNewserialStat == "O" or cmdNewserialStat == "o":
                        serial.write('o')
                elif cmdNewserialStat == "C" or cmdNewserialStat == "c":
                        serial.write('c')
                elif cmdNewserialStat == "q" or cmdNewserialStat == "Q":
                        serial.write('q')
	
	for x in range(0,5):
		val = serial.readline().strip()
	
	print (val)
			
except Exception, e:
	PrintException()

