#include <SoftwareSerial.h>
const int rxpin = 2; 
const int txpin = 3; 
SoftwareSerial mySerial(rxpin, txpin);
#define BTSERIAL mySerial

void setup() {
  Serial.begin(9600);
  BTSERIAL.begin(9600);
  Serial.println("Serial ready");
  BTSERIAL.println("Bluetooth ready");
}

void loop() {
  if (BTSERIAL.available()) {
    char c = (char)BTSERIAL.read();
    Serial.write(c);
  }
  if (Serial.available()) {
    char c = (char)Serial.read();
    BTSERIAL.write(c);
  }
}