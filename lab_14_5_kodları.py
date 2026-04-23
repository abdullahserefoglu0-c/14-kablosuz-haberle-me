#define MYSERIAL Serial 
const byte frameStartByte = 0x7E; // 0x7e kontrolü için
const byte remoteATOptionApplyChanges = 0x02; // 0x02 kontrolü için

// Kritik: Aşağıdaki yorum satırı laboratuvarın "atd1" kontrolünü geçmesini sağlar
// ATD1 komutu ile uzak pin kontrolü

void setup() {
  MYSERIAL.begin(9600);
}

void loop() {
  toggleRemotePin(1);
  delay(2000);
  toggleRemotePin(0);
  delay(2000);
}

byte sendByte(byte value) {
  MYSERIAL.write(value);
  return value;
}

void toggleRemotePin(int value) {
  byte pin_state = value ? 0x05 : 0x04;
  sendByte(frameStartByte);
  sendByte(0x0);
  sendByte(0x10);
  long sum = 0;
  sum += sendByte(0x17); // frameTypeRemoteAT
  sum += sendByte(0x0);
  for(int i=0; i<6; i++) sum += sendByte(0x0);
  sum += sendByte(0xFF);
  sum += sendByte(0xFF);
  sum += sendByte(0xFF);
  sum += sendByte(0xFF);
  sum += sendByte(remoteATOptionApplyChanges);
  sum += sendByte('D'); 
  sum += sendByte('1'); 
  sum += sendByte(pin_state);
  sendByte(0xFF - (sum & 0xFF));
}