/*This code will Verify MPU6050 data reading.*/

#include <Wire.h>

#define MPU_ADDR 0x68

void setup() {

  Serial.begin(115200);

  Wire.begin(4,5);

  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x6B);
  Wire.write(0);
  Wire.endTransmission(true);
}

void loop() {

  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x3B);
  Wire.endTransmission(false);

  Wire.requestFrom(MPU_ADDR,6,true);

  int16_t ax = Wire.read()<<8 | Wire.read();
  int16_t ay = Wire.read()<<8 | Wire.read();
  int16_t az = Wire.read()<<8 | Wire.read();

  Serial.print(ax);
  Serial.print(",");

  Serial.print(ay);
  Serial.print(",");

  Serial.println(az);

  delay(100);
}

/*Expected Output
AX: 100
AY: -50
AZ: 16000*/