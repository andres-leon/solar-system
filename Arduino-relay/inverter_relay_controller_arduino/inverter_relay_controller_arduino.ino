/*  https://forum.arduino.cc/index.php?topic=288234.0 */
#include <EEPROM.h>

#define relay 13

char receivedChar;
boolean newData = false;

// start reading from the first byte (address 0) of the EEPROM
int address = 0;
byte value;
char relay_stat;

void setup() 
{
  value = EEPROM.read(address);
  Serial.begin(115200);
  pinMode(relay, OUTPUT); 
  if (value == 99) //99==ascii for o; 111==ascii for c
  {
    digitalWrite(relay, LOW); 
    Serial.print('o');
    relay_stat = 'o';
  }
  else if (value == 111) 
  {
    digitalWrite(relay, HIGH); 
    Serial.print('c');
    relay_stat = 'c';
  }
}

void loop() 
{
  recvOneChar();
  processNewCmd();
}

void recvOneChar() 
{
 if (Serial.available() > 0) 
 {
  receivedChar = Serial.read();
  newData = true;
 }
}

void processNewCmd()
{
  if (newData == true) 
  {
    if (receivedChar == 'o' || receivedChar =='O')
    {
      relay_stat = 'o';
      value = 99;
      digitalWrite(relay,LOW);
      EEPROM.write(address, value);
    }    
    else if (receivedChar == 'c' || receivedChar =='C')
    {
      relay_stat = 'c';
      value = 111;
      digitalWrite(relay, HIGH);
      EEPROM.write(address, value);
    }
    //else if (receivedChar == 'q' || receivedChar =='Q')
    else
    { //Query the staus of the relay
      value = EEPROM.read(address);
      if (value == 99) //99==ascii for o; 111==ascii for c
      {
        relay_stat = 'o';
      }
      else if (value == 111) 
      {
        relay_stat = 'c';
      }     
      //for (int x = 0; x<=5; x++)
      //{
      //  Serial.println(relay_stat);
      //}
    }
    
    for (int x = 0; x<=5; x++)
    {
      Serial.println(relay_stat);
    }
    newData = false;
  }
}

