bool pressed[9] = {false, false, false, false, false, false, false, false, false};
unsigned long lastPressed[9] = {0, 0, 0, 0, 0, 0, 0, 0, 0};
String notes[9] = {"C1", "D1", "E1", "F1", "G1", "A1", "B1", "C2", "RECORD"};

void setup() {
  // put your setup code here, to run once:
  // keys
  pinMode(2, INPUT_PULLUP);
  pinMode(3, INPUT_PULLUP);
  pinMode(4, INPUT_PULLUP);
  pinMode(5, INPUT_PULLUP);
  pinMode(6, INPUT_PULLUP);
  pinMode(7, INPUT_PULLUP);
  pinMode(8, INPUT_PULLUP);
  pinMode(9, INPUT_PULLUP);

  // record
  pinMode(10, INPUT_PULLUP);
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  for (int i = 0; i < 9; i++) {
    if (digitalRead(i + 2) == LOW
        && !pressed[i]
        && (millis() > lastPressed[i] + 200 || lastPressed[i] == 0)) {
      pressed[i] = true;
      lastPressed[i] = millis();
      Serial.println(notes[i]);
    } else if (digitalRead(i + 2) == HIGH) {
      pressed[i] = false;
    }
  }
}
