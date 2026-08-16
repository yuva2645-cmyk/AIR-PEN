/*This Code will Verify ESP32-C3 SuperMini is working and Serial Monitor communication is functioning.*/
void setup() {
  Serial.begin(115200);
  delay(2000);

  Serial.println("ESP32-C3 STARTED");
}

void loop() {
  Serial.println("Running...");
  delay(1000);
}
/*Expected Output
ESP32-C3 STARTED
Running...
Running...
Running...*/