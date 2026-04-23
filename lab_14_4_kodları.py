#define MYSERIAL Serial 
#define MIN_CHUNK 21
#define OFFSET 18
const int ledPin = 5;

void setup() {
  MYSERIAL.begin(9600);
  delay(1000);
  configureRadio();
}

bool configureRadio() {
  MYSERIAL.flush();
  MYSERIAL.print("+++");
  delay(100);
  MYSERIAL.print("ATAP1\r"); 
  delay(100);
  MYSERIAL.print("ATCN\r"); 
  return true;
}

void loop() {
  if (MYSERIAL.available() >= MIN_CHUNK) {
    if (MYSERIAL.read() == 0x7E) {
      for (int i = 0; i < OFFSET; i++) {
        MYSERIAL.read();
      }
      int analogHigh = MYSERIAL.read();
      int analogLow = MYSERIAL.read();
      int analogValue = analogLow + (analogHigh * 256);
      int brightness = map(analogValue, 0, 1023, 0, 255);
      analogWrite(ledPin, brightness);
    }
  }
}