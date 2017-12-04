int ports[15] = {A0, A1, A2, A3, A4, A5, 2, 3, 4, 5, 6, 7, 8, 9, 10};
bool pressed[15] = {false, false, false, false, false, false, false, false, false, false, false, false, false, false, false};
unsigned long lastPressed[15] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
String notes[15] = {"C1", "D1", "E1", "F1", "G1", "A1", "B1", "C2", "D2", "E2", "F2", "G2", "A2", "B2", "C3"};

int isRecord = LOW;
unsigned long lastRecord = 0;

void setup() {
  pinMode(A0, INPUT_PULLUP); // C1
  pinMode(A1, INPUT_PULLUP); // D1
  pinMode(A2, INPUT_PULLUP); // E1
  pinMode(A3, INPUT_PULLUP); // F1
  pinMode(A4, INPUT_PULLUP); // G1
  pinMode(A5, INPUT_PULLUP); // A1
  pinMode(2, INPUT_PULLUP); // B1
  pinMode(3, INPUT_PULLUP); // C2
  pinMode(4, INPUT_PULLUP); // D2
  pinMode(5, INPUT_PULLUP); // E2
  pinMode(6, INPUT_PULLUP); // F2
  pinMode(7, INPUT_PULLUP); // G2
  pinMode(8, INPUT_PULLUP); // A2
  pinMode(9, INPUT_PULLUP); // B2
  pinMode(10, INPUT_PULLUP); // C3

  pinMode(11, INPUT_PULLUP); // RECORD
  pinMode(12, OUTPUT);       // RECORD LED
  
  Serial.begin(9600);
}

void loop() {
  for (int i = 0; i < 15; i++) {
    if (digitalRead(ports[i]) == LOW
        && !pressed[i]
        && (millis() > lastPressed[i] + 200 || lastPressed[i] == 0)) {
      pressed[i] = true;
      lastPressed[i] = millis();
      Serial.println(notes[i]);
    } else if (digitalRead(ports[i]) == HIGH) {
      pressed[i] = false;
    }
  }

  int record = digitalRead(11);
  if (record != isRecord && (millis() > lastRecord + 200 || lastRecord == 0)) {
    digitalWrite(12, record);
    Serial.println(record == HIGH ? "RECORDON" : "RECORDOFF");
    isRecord = record;
    lastRecord = millis();
  }
}
