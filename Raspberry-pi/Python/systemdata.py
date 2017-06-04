import sys, psutil, datetime, paho.mqtt.client as mqtt, json
from time import gmtime, strftime
import os

def getCPUtemperature():
        try:
                res = os.popen('vcgencmd measure_temp').readline()
                tmp1 = res.replace("temp=","")
                tmp1 = tmp1.replace("'","")
                tmp1 = tmp1.replace("C","")
                #print tmp1
                return tmp1
        except:
                return 0


def bytes2human(n):
# http://code.activestate.com/recipes/577972-disk-usage/
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i+1)*10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n

temp1 = int(float(getCPUtemperature()))
cputemp = 9.0/5.0*temp1+32

currtime = strftime("%Y-%m-%d %H:%M:%S")

boottime = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")

topic = "rbp3_solar/systemstatus"

cpupercent = psutil.cpu_percent(interval=1)
vmem = psutil.virtual_memory().percent
diskusage =  psutil.disk_usage('/').percent
disktotal = bytes2human( psutil.disk_usage('/').total )

payload = { 'datetimedatacollected': currtime,
 'cpuusage': cpupercent, 'boottime': boottime,
 'virtualmem': vmem, 'diskusage': diskusage,
 'cputemp': cputemp, 'disktotal': disktotal }

mqtthost = "your mqtt address"
mqttuser = "user"
mqttpwd = "password"

client = mqtt.Client()
client.username_pw_set(mqttuser, mqttpwd)
client.connect(mqtthost, 1883, 60)

payload_json = json.dumps(payload)

print (payload_json)

persistant_data = True

client.publish(topic, payload_json, 0, persistant_data)
client.disconnect()

sys.exit()


