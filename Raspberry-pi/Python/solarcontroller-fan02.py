#!/usr/bin/env python2.7
#andres leon: this script starts on @reboot and continually runs to check the db for status updates from the web interface
# then runs the fans based on cpu temperature comparison and if enabled at all.
import sys
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time
import logging, json
import os
import MySQLdb

logger = logging.getLogger('fancontroller')
hdlr = logging.FileHandler('/home/pi/solarcontroller-fan02.log')
formatter = logging.Formatter("%(asctime)s     %(levelname)s     %(message)s")
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.WARNING)

relayPIN = 17
relay2PIN = 27
templimit = 122
allowFanToRun = 1
sleepTimeSecs = 10
prevfan = 0
currfan = 0	


def PrintException():
	exc_type, exc_obj, tb = sys.exc_info()
	f = tb.tb_frame
	lineno = tb.tb_lineno
	filename = f.f_code.co_filename
	linecache.checkcache(filename)
	line = linecache.getline(filename, lineno, f.f_globals)
	logger.error('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))


def getFanSettingsFromDB():
	global templimit
	global allowFanToRun
	try:
		db = MySQLdb.connect(host= "localhost", user="xx", passwd="yy", db="solardata")	
		cur = db.cursor()
		cur.execute("SELECT setting, value FROM settings WHERE setting LIKE 'fan%'")
		for row in cur.fetchall():
			print "'" + row[0] + "' : '" + row[1] + "'"
			if ( row[0] == "fan" ):
				allowFanToRun = int(row[1])
			elif ( row[0] == "fan_temp" ):
				templimit = int(row[1])

		db.close()
	except Exception, e:
		PrintException()
        
def getCPUtemperature():
        try:
                res = os.popen('vcgencmd measure_temp').readline()
                tmp1 = res.replace("temp=","")
                tmp1 = tmp1.replace("'","")
                tmp1 = tmp1.replace("C","")
                #print tmp1
                return tmp1
        except Exception, e:
                PrintException()
                return 0
		
def CtoF(c):
	#print("getting temp")
	tempf = 9.0/5.0 * float(c) + 32
	#print ("temp is " + str(tempf) )
	return tempf 

def ToggleFans(newCmd):
	if (newCmd == 1):
		GPIO.output(relayPIN, GPIO.LOW) 
		GPIO.output(relay2PIN, GPIO.LOW)
	else:
		GPIO.output(relayPIN, GPIO.HIGH)
		GPIO.output(relay2PIN, GPIO.HIGH)
		
	
#sleep for 25 seconds before loop begins to allow startup tasks to end.
time.sleep(25)
while True:
	try:
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(relayPIN, GPIO.OUT)
		GPIO.setup(relay2PIN, GPIO.OUT)
		
		while True:		
			getFanSettingsFromDB()
			currtime = time.strftime("%Y-%m-%d %H:%M:%S")
			temp = CtoF(getCPUtemperature())
		
			if ( allowFanToRun == 1 ):	
				if (temp > templimit):
					currfan = 1
					ToggleFans(1) 
					logger.info(" temp: " + str(temp) + " - Fan is running.")
					print (currtime + " - temp: " + str(temp) + " - Fan is running.")
				else:
					currfan = 0
					ToggleFans(0)
					logger.info(" temp: " + str(temp) + " - Fan is NOT running.")
					print (currtime + " - temp: " + str(temp) + " - Fan NOT running.")
					
			else:	#fan setting is to no run
				currfan = 0
				ToggleFans(0)
				logger.info(" temp: " + str(temp) + " - Fan is NOT running due to setting in database.")
				print (currtime + " - temp: " + str(temp) + " - Fan NOT running due to setting in database.")
			
			topic = "solarcontroller/fan"
			
			payload = { 'datetimedatacollected': currtime, 'currfan': currfan, 'prevfan': prevfan, 'cpu_temp': temp, 'allowFanToRun': allowFanToRun, 'templimit': templimit }

			mqtthost = "your mqtt address"
			mqttuser = "user"
			mqttpwd = "password"

			mqttclient = mqtt.Client()
			mqttclient.username_pw_set(mqttuser, mqttpwd)
			mqttclient.connect(mqtthost, 1883, 60)
			
			payload_json = json.dumps(payload)

			print (payload_json)
			
			persistant_data = True
			
			#logger.error("sending mqtt")

			mqttclient.publish(topic, payload_json, 0, persistant_data)
			mqttclient.disconnect()
			#logger.error("mqtt sent")
			
			prevfan = currfan			
			
			time.sleep(sleepTimeSecs)
		
	except Exception, e:
		PrintException()
		print str(currtime) + " - " + str(e)
			
	finally:
		GPIO.output(relayPIN, GPIO.LOW)
		GPIO.output(relay2PIN, GPIO.LOW)
		#GPIO.cleanup()


