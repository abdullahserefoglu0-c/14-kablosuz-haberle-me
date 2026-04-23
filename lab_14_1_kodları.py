#include <SPI.h>
#include <RH_RF69.h>
#include <RHReliableDatagram.h>

#define MY_ADDR 2 
#define DEST_ADDR 1 
#define RF69_FREQ 915.0 

#define RFM69_INT 3
#define RFM69_CS 4
#define RFM69_RST 2

RH_RF69 rf69(RFM69_CS, RFM69_INT);
RHReliableDatagram rf69_manager(rf69, MY_ADDR);

void setup() {
  Serial.begin(9600);
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(RFM69_RST, OUTPUT);
  digitalWrite(RFM69_RST, LOW);
  
  digitalWrite(RFM69_RST, HIGH); delay(10);
  digitalWrite(RFM69_RST, LOW); delay(10);

  if (!rf69_manager.init()) {
    while (1); 
  }

  if (!rf69.setFrequency(RF69_FREQ)) {
    while (1); 
  }

  rf69.setTxPower(20, true); 
  uint8_t key[] = { 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
                    0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08};
  rf69.setEncryptionKey(key);
}

void loop() {
  delay(1000);
  byte message[] = "Hello!";
  byte response[RH_RF69_MAX_MESSAGE_LEN];

  if (rf69_manager.sendtoWait((byte*)message, strlen((char*)message), DEST_ADDR)) {
    byte len = sizeof(response);
    byte sender;
    if (rf69_manager.recvfromAckTimeout(response, &len, 2000, &sender)) {
      response[len] = 0;
      Serial.print("Got ["); Serial.print((char*)response);
      Serial.print("] from "); Serial.println(sender);
      digitalWrite(LED_BUILTIN, HIGH); delay(250);
      digitalWrite(LED_BUILTIN, LOW); delay(250);
    }
  }
}