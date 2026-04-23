#define MYSERIAL Serial 

void setup() {
  MYSERIAL.begin(9600);
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  while (MYSERIAL.available()) {
    MYSERIAL.write(MYSERIAL.read()); 
    digitalWrite(LED_BUILTIN, HIGH);
    delay(10);
    digitalWrite(LED_BUILTIN, LOW);
    delay(10);
  }
}