void setup() {
pinMode(0, OUTPUT);
pinMode(1, OUTPUT);
pinMode(2, OUTPUT);
pinMode(3, OUTPUT);
}

void loop() {
  while(true){
    digitalWrite(0, analogRead(PIN_A1) > 60);
    digitalWrite(1, analogRead(PIN_A2) > 60);
    digitalWrite(2, analogRead(PIN_A3) > 60);
    digitalWrite(3, analogRead(PIN_A4) > 60);
  }
}
