/*
 * https://forum.arduino.cc/index.php?topic=382737.0
 * read data from serial expecting an integer. if value is integer then
 * it udpates the ZERO_POINT value with which it calculates the
 * appropriate current.
 */
#include <EEPROM.h>
#include <ArduinoJson.h>
#include <ctype.h>

const byte a_pin=A0;
int zero_point_EEPROM; //initial zero point (in mem)
int zero_point = 740; //initial zero point 
//const int point_72a = 336; 
const float amp_per_step = 0.15254 ; // 72/(818-336) Values to be adjusted/calibrated

//address in EEPROM where I store the zero pint calculated from the incoming voltage.
int address = 0;

String inputString = "";         // a string to hold incoming data
boolean stringComplete = false;  // whether the string is complete

void setup() 
{  
  zero_point_EEPROM = EEPROM.read(address);
  Serial.begin(115200);
  while (!Serial) 
  {
    ; // wait for serial port to connect. Needed for native USB port only
  }
  Serial.println("arduino_CSLA2CD03");
  // reserve 3 bytes for the inputString:
  //inputString.reserve(3);
}

void loop() 
{
  zero_point = zero_point_EEPROM * 4;
  int steps;
  float current;
  int raw;
  int loopamount = 100;
  float samples = 0.0;
  float avgSamples = 0.0;
    
  for (int x = 0; x < loopamount; x++){ //Get samples
    raw = analogRead(a_pin); 
    samples = samples + raw;
    delay (5); // let ADC settle before next sample
  }

  avgSamples = samples / (float)loopamount;  
  steps = zero_point - avgSamples;
  current =  amp_per_step * steps;
    
  // Memory pool for JSON object tree.
  //
  // Inside the brackets, 200 is the size of the pool in bytes.
  // If the JSON object is more complex, you need to increase that value.
  StaticJsonBuffer<200> jsonBuffer;
  // Create the root of the object tree.
  //
  // It's a reference to the JsonObject, the actual bytes are inside the
  // JsonBuffer with all the other nodes of the object tree.
  // Memory is freed when jsonBuffer goes out of scope.
  JsonObject& root = jsonBuffer.createObject();
  // Add values in the object
  //
  // Most of the time, you can rely on the implicit casts.
  // In other case, you can do root.set<long>("time", 1351824120);

  root["raw"] = raw;
  root["zero_point"] = zero_point;  
  root["avgSamples"] = avgSamples;
  root["current"] = current;  
  root.printTo(Serial);
  Serial.println("");



}

void serialEvent() {
  inputString = "";
  //Serial.println("some data in...");
  while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read();
    if ( isdigit(inChar) )
    {
      // add it to the inputString:
      inputString += inChar;
    }    
    // if the incoming character is a newline, set a flag
    // so the main loop can do something about it:
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
  Serial.println(inputString);
  //Serial.println(zero_point);
  zero_point_EEPROM = inputString.toInt() / 4;
  EEPROM.update(address, zero_point_EEPROM);
  //Serial.println(zero_point_EEPROM);
  
  while(Serial.read() != -1);
}

