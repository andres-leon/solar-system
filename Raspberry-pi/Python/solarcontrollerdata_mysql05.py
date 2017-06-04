#!/usr/bin/env python2.7
#code to access data from the MPPT Controller derived from http://www.solarpoweredhome.co.uk/#prettyPhoto
#andres leon: this script starts on @reboot and continually runs to read data from the MPPT charge controller as well as 
#the current sensor. Data is then stored in the mysql database as well as published to my Home Assistant MQTT messaging server
import sys, psutil, datetime, paho.mqtt.client as mqtt, json
import MySQLdb
import datetime
import time
import logging
from time import gmtime, strftime
import os
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
import serial
import linecache
import sys
import subprocess

sleeptime = 1
loopCounterForSQLInsert = 0
#resetloopCounterForSQLInsert of 10 is about an isert every 2 minutes. incresing to 5 so entry is done once a minute
resetloopCounterForSQLInsert = 4	#every x times a reading is taken data will be stored in SQL

batteryMinVoltageReal = 11.80
batteryMaxVoltageReal = 12.80
voltageRangeReal = (batteryMaxVoltageReal - batteryMinVoltageReal)

def getCPUtemperature():
        try:
                res = os.popen('vcgencmd measure_temp').readline()
                tmp1 = res.replace("temp=","")
                tmp1 = tmp1.replace("'","")
                tmp1 = tmp1.replace("C","")
                return tmp1
        except:
                return 0

def CtoF(c):
	return 9.0/5.0 * float(c) + 32

logger = logging.getLogger('myapp')
hdlr = logging.FileHandler('/home/pi/solarcontrollerdata_mysql05.log')
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

#logger.error("started program!")	
#sleep for 15 seconds before loop begins to allow other tasks to end.
print("start! waiting 15 secs...")
time.sleep(15)
print("15 secs have passed...")

while (1==1):
	result_error_count = 0
	result_error_count_if = 0
	result_error_count_batt = 0
	db = MySQLdb.connect(host= "localhost", user="xx", passwd="yy", db="solardata")
	
	client = ModbusClient(method = 'rtu', port = '/dev/ttyUSB0', baudrate = 115200)
	client.connect()
	print ("modbus connected!")	
	
	try:		
		#the ModbusClient takes about 3 seconds to query the controller. 
		#add extra 7 seconds to make it poll every 10 seconds.
		#time.sleep(7)
		#result = client.read_input_registers(0x3100,6,unit=1)
		try:
			print("reading data from modbus...")
			result = client.read_input_registers(0x3100,20,unit=1)
			print("data received! = " + str(result) )
			
		except Exception as e:
			print("error reading modbus")
			result_error_count = result_error_count + 1
			if (result_error_count >= 10):
				logger.error("failed to connect 10 times or more. ")
				PrintException()
				time.sleep(30)	#take a 30 second break to allow connection to USB to stabilize.
				#os.system("sudo shutdown -r 1")
				logger.error("Command to reboot has been sent.")
				result_error_count = 0
				
			pass
			
		if not (result is None):
			solarVoltage = float(result.registers[0] / 100.0)
			solarCurrent = float(result.registers[1] / 100.0)
			solarWatts = float(result.registers[2] / 100.0)
			value3 = float(result.registers[3] / 100.0)
			batteryVoltage = float(result.registers[4] / 100.0)
			batteryCurrent = float(result.registers[5] / 100.0)
			batteryWatts = float(result.registers[6] / 100.0)
			value7 = float(result.registers[7] / 100.0)
			loadVoltage = float(result.registers[8] / 100.0)
			#Load_current = float(result.registers[9] / 100.0)
			#loadWatts = float(result.registers[10] / 100.0)
			value11 = float(result.registers[11] / 100.0)
			value12 = float(result.registers[12] / 100.0)
			value13 = float(result.registers[13] / 100.0)
			value14 = float(result.registers[14] / 100.0)
			value15 = float(result.registers[15] / 100.0)
			batteryTemp = CtoF(float(result.registers[16] / 100.0))
			insideTemp = CtoF(float(result.registers[17] / 100.0))
			heatsinkTemp = CtoF(float(result.registers[18] / 100.0))				
			
			loadWatts = 0.0
			Load_current = 0.0
			
			print("getting data from current sensor...")
			current_jsondata = subprocess.check_output(['python','/home/pi/currentsensor01.py'])		
			print("got data from current sensor!" + str(current_jsondata) )
			
			if (len(current_jsondata) > 0):
				current_data = json.loads(current_jsondata)
				#current_raw = current_data["raw"]
				#current_zero_point = current_data["zero_point"]
				#current_avgSamples = current_data["avgSamples"]
				Load_current = current_data["current"]
				#print ("raw = " + str(raw))
				#print ("zero_point = " + str(zero_point))
				#print ("avgSamples = " + str(avgSamples))
				#print ("current = " + str(Load_current))
				
			loadWatts = Load_current * batteryVoltage
		
			#old method mapping to max and min volts
			OldRange = (batteryMaxVoltageReal - batteryMinVoltageReal)
			if (OldRange == 0):
				batteryChargePercentNew = 0
			else:
				NewRange = (100 - 0)  
				batteryChargePercentNew = (((batteryVoltage - batteryMinVoltageReal) * NewRange) / OldRange) + 0
			
			
			result_batt_percent = 0.0
			try:
				result_batt_percent = client.read_input_registers(0x311A,1,unit=1)
			except Exception as e:
				print ("error2")
				result_error_count_batt = result_error_count_batt + 1
				if (result_error_count_batt >= 10):
					PrintException()
					time.sleep(30)	#take a 30 second break to allow connection to USB to stabilize.
					result_error_count_batt = 0
				
				pass
			
			if not (result_batt_percent is None):
				batteryChargePercent = float(result_batt_percent.registers[0])
			else:
				batteryChargePercent = 0.0
				
			temp1 = int(float(getCPUtemperature()))
			cputemp = CtoF(temp1)
			
			#get the status of the inverter relay
			inverter_relay_status = subprocess.check_output(['python','/home/pi/inverter_relay_control01.py', 'q'])
			inverter_relay_status = inverter_relay_status.strip()
			
			#inverter_serial = serial.Serial('/dev/ttyUSB1', 115200)
			#time.sleep(2) 
			#inverter_serial.write('q')
			#for x in range(0,5):
			#	inverter_relay_status = inverter_serial.readline().strip()
				
			
			sqlcmd = "INSERT INTO stats(PV_array_voltage, PV_array_current, PV_array_power, \
Battery_voltage, Battery_charging_current, Battery_charging_power, Battery_charge_percentage, \
Load_voltage, Load_current, Load_power, Charger_temperature, Heat_sink_temperature, \
Battery_Sensor_temperature, RBP_CPU_temperature) \
VALUES (" + str(solarVoltage) + ", " + str(solarCurrent) + ", " + str(solarWatts) + ", " +  \
str(batteryVoltage) + ", " + str(batteryCurrent) + ", " + str(batteryWatts) + ", " + \
str(batteryChargePercent) + ", " + str(loadVoltage) + ", " + str(Load_current) + ", " + \
str(loadWatts) + ", " + str(insideTemp) + ", " + str(heatsinkTemp) + ", " + \
str(batteryTemp) + ", " + str(cputemp) +  ")"
			
			if loopCounterForSQLInsert >= resetloopCounterForSQLInsert:
				print (sqlcmd)			
				cursor = db.cursor()
				cursor.execute(sqlcmd)
				# Commit your changes in the database
				db.commit()
				db.close()
				#logger.error("insert into db OK!")	
				loopCounterForSQLInsert = 0
			else:
				loopCounterForSQLInsert = loopCounterForSQLInsert + 1
			
			print("")
			now = datetime.datetime.now()
			print str(now)
			print("-------------------------------------------")
			print ("solarVoltage: " + str(solarVoltage))
			print ("solarCurrent: " + str(solarCurrent))
			print ("solarWatts: " + str(solarWatts))
			print("-------------------------------------------")
			print ("batteryVoltage: " + str(batteryVoltage))
			print ("batteryCurrent: " + str(batteryCurrent))
			print ("batteryWatts: " + str(batteryWatts))
			print ("batteryChargePercentage: " + str(batteryChargePercent) + "%")
			#print ("battery state of charge: " + str(bS))
			print("-------------------------------------------")
			print ("loadVoltage: " + str(loadVoltage))
			print ("Load_current: " + str(Load_current))
			print ("loadWatts: " + str(loadWatts))
			print("-------------------------------------------")
			print ("batteryTemp: " + str(batteryTemp))
			print ("insideTemp: " + str(insideTemp))
			print ("heatsinkTemp: " + str(heatsinkTemp))			
			
			print ("RBP_CPU_Temp: " + str(cputemp))			
			
			topic = "solarcontroller/status"
			currtime = strftime("%Y-%m-%d %H:%M:%S")		
			
			payload = { 'datetimedatacollected': currtime,
				'solarVoltage': solarVoltage, 'solarCurrent': solarCurrent,
				'solarWatts': solarWatts, 'batteryVoltage': batteryVoltage,
				'batteryWatts': batteryWatts, 'batteryCurrent': batteryCurrent,
				'batteryChargePercent': batteryChargePercent, 'loadVoltage': loadVoltage,
				'batteryChargePercentNew': batteryChargePercentNew,
				'Load_current': Load_current, 'loadWatts': loadWatts,
				'batteryTemp': batteryTemp, 'insideTemp': insideTemp,
				'cputemp': cputemp,'heatsinkTemp': heatsinkTemp,
				'inverter_relay_status': inverter_relay_status}

			mqtthost = "your mqtt address"
			mqttuser = "user"
			mqttpwd = "password"

			mqttclient = mqtt.Client()
			mqttclient.username_pw_set(mqttuser, mqttpwd)
			
			try:
				mqttclient.connect(mqtthost, 1883, 60)
			except Exception as e:
				PrintException()
				time.sleep(30)	#take a 30 second break to allow network to come back up.

				
			payload_json = json.dumps(payload)

			print (payload_json)
			
			persistant_data = True
			
			#logger.error("sending mqtt")

			mqttclient.publish(topic, payload_json, 0, persistant_data)
			mqttclient.disconnect()
			#logger.error("mqtt sent")
			
		else:
			print("ERROR: Could not connect or read data from controller.")
			result_error_count_if = result_error_count_if + 1
			if (result_error_count >= 10):
				PrintException()
				logger.error("ERROR: Could not connect or read data from controller.")
				time.sleep(30)	#take a 30 second break to allow connection to USB to stabilize.
				#os.system("sudo shutdown -r 1")
				logger.error("Command to reboot has been sent.")
				result_error_count_if = 0				
			#pass			
			
		#wait to run process again
		time.sleep(sleeptime)

	except Exception as e: 
		PrintException()
		print str(e)
		#logger.error(str(e))


