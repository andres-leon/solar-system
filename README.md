# solar-system
A series of scripts and code I have written to control my home solar energy storage system. You can find more information about this project at 

# http://www.andresleonphoto.com/blog/2017/6/02/my-home-solar-system-project

The folder Arduino-current_sensor/arduino_CSLA2CD03 holds the code for the Arduino board that reads and sends the current sensor data in serial to the Raspberry Pi.

The folder Arduino-relay/inverter_relay_controller_arduino contains the code for another Arduino board. This one controls a relay which provides power to my system inverter. This allows me to control when the inverter is on remotely.

The Raspberry-pi folder contains all the code that run in the pi. These are python scripts and html files served from the pi itself. 
