#include <WiFi.h>
#include <WiFiUdp.h>

const char* ssid="YOUR_WIFI";
const char* password="YOUR_PASSWORD";

const char* laptopIP="192.168.1.3";
const int udpPort=5005;

WiFiUDP udp;

void setup() {

  Serial.begin(115200);

  WiFi.begin(ssid,password);

  while(WiFi.status()!=WL_CONNECTED)
    delay(500);
}

void loop() {

  udp.beginPacket(laptopIP,udpPort);
  udp.print("AirPen Test");
  udp.endPacket();

  delay(1000);
}