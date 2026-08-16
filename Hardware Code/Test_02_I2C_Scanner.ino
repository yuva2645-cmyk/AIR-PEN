/*This code automatically detects and displays the address of any connected I2C peripheral hardware.*/
#include <Wire.h>

void setup() {
  Serial.begin(115200);
  Wire.begin(4,5);

  Serial.println("Scanning...");
}

void loop() {

  byte error;

  for(byte address=1; address<127; address++) {

    Wire.beginTransmission(address);
    error = Wire.endTransmission();

    if(error==0) {
      Serial.print("Found Device: 0x");
      Serial.println(address,HEX);
    }
  }

  delay(3000);
}

/*
Expected Output
Found Device: 0x68
*/

