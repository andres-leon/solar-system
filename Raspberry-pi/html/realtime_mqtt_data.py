import sys, psutil, datetime, paho.mqtt.client as mqtt, json
from time import gmtime, strftime
import os
import logging
import linecache
import sys


logger = logging.getLogger('myapp')
hdlr = logging.FileHandler('/var/www/solar/realtime_mqtt_data.log')
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

try:
	if len(sys.argv) == 2:
		fieldToRetrieve = sys.argv[1]

		topic = "solarcontroller/status"

		mqtthost = "your mqqt address"
		mqttuser = "your user"
		mqttpwd = "your password"

		def getData(msg, dataitem):
			json_data = json.loads(msg)
			return json_data[dataitem]
				

		def on_connect(client, userdata, flags, rc):
			#print("Connected with result code "+str(rc))
			client.subscribe(topic)

		def on_message(client, userdata, msg):
			msg =  msg.payload.decode()
			#print msg
			client.disconnect()

			dta = str( getData( msg, fieldToRetrieve ) ) 
			if (fieldToRetrieve == "solarVoltage"):	#mppt incorrectly passes info when near zero voltage from panels.
				if ( float( dta ) <= 0.20 ):
					dta = "0.0"
					
			print ( str( dta ) )

		mqttclient = mqtt.Client()
		mqttclient.username_pw_set(mqttuser, mqttpwd)
		mqttclient.connect(mqtthost, 1883, 60)

		mqttclient.on_connect = on_connect
		mqttclient.on_message = on_message

		mqttclient.loop_forever()
except Exception as e:
	PrintException()