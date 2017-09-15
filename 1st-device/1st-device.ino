#include <LiquidCrystal.h>
#include <WiFiEsp.h>
#include <WiFiEspClient.h>
#include <WiFiEspUdp.h>
#include "SoftwareSerial.h"
#include <PubSubClient.h>

// ######################### LCD #########################
// Connection between LCD and Arduino Pro Micro
//         LCD       ||| VSS | VDD | V0  | RS | RW  | E  | DB0 | DB1 | DB2 | DB3 | DB4 | DB5 | DB6 | DB7 | LEDA | LEDK
//===================|||=====|=====|=====|====|=====|====|=====|=====|=====|=====|=====|=====|=====|=====|======|=======
// Arduino Pro Micro ||| GND | VCC | GND | A1 | GND | A0 | --- | --- | --- | --- | 15  | 14  | 16  | 10  | VCC  | GND 
LiquidCrystal lcd(A1, A0, 15, 14, 16, 10);
int LCDTemperature, LCDLight, MessageLength, pos = 0, DebugMessageLength, dpos = 0;
char *LCDMessage, *LCDDebugMessage;
bool debugging = true;

void LCDSetup() {
  lcd.begin(16, 4);
}

void LCDShow() {
  lcd.clear();
  
  // temperature
  lcd.setCursor(0, 0);
  lcd.print("T: ");
  lcd.print(LCDTemperature);

  // light
  lcd.setCursor(8, 0);
  lcd.print("L: ");
  lcd.print(LCDLight);

  // rfid id

  // message
  pos = LCDShowMessage(LCDMessage, MessageLength, 2, pos);

  // debuging
  if (debugging) {
    dpos = LCDShowMessage(LCDDebugMessage, DebugMessageLength, 3, dpos);
  }
}

void LCDSetTemperature(int temperature) {
  LCDTemperature = temperature;
}

void LCDSetLight(int light) {
  LCDLight = light;
}

void LCDSetMessage(char *message, int mesLength) {
  LCDMessage = message;
  pos = 0;
  MessageLength = mesLength;
}

void LCDSetDebugMessage(char *message, int mesLength) {
  LCDDebugMessage = message;
  dpos = 0;
  DebugMessageLength = mesLength;
}

int LCDShowMessage(char *message, int mesLength, int row, int p) {
  lcd.setCursor(0, row);
  for (int i = p; i < 16 + p && i < mesLength; i+=1)
    lcd.write(message[i]);
  if (mesLength > 16)
    p += 1;
  if (p == mesLength)
    p = 0;
  return p;
}

// ######################### Temperature Sensor #########################
float steps = 1024.0;
int volt = 4000/10, tempPin = 3;

float getTemperature() {
  return (analogRead(tempPin) / steps) * volt;
}

// ######################### LDR Sensor #########################
int ldrPin = 2, ldr;

int getLDR() {
  return analogRead(ldrPin) / 10;
}

// ######################### WiFi & MQTT #########################
IPAddress server(192, 168, 1, 35); // MQTT Broker address
char ssid[] = "-=-=-=-=-=-=-=-";               // Network SSID (name)
char pass[] = "282483191413";               // Network password (secret)
int status = WL_IDLE_STATUS;       // Wifi radio's status

SoftwareSerial soft(9, 8);         // RX, TX to communicate with ESP8266
WiFiEspClient espClient;
PubSubClient client(espClient);

void WiFiSetup() {
  soft.begin(9600);
  WiFi.init(&soft);

  if (WiFi.status() == WL_NO_SHIELD) {
//    Serial.println("WiFi shiel/d not present");
    LCDSetDebugMessage("No WiFi.", 8);
    while (true);
  }

//  Serial.print("Attempting to connect t/o WPA SSID: ");
//  Serial.print(ssid);/
//  Serial.print(" ");/
  while (status != WL_CONNECTED) {
    // Connect to WPA/WPA2 network
//    Serial.print(".");/
    status = WiFi.begin(ssid, pass);
  }
//  Serial.println(" Connec/ted.");
  LCDSetDebugMessage("WiFi Connected.", 15);
}

void MQTTSetup() {
  client.setServer(server, 1883);
  client.setCallback(callback);
  reconnect();
  client.loop();
}

//print any message received for subscribed topic
void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i=0;i<length;i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    LCDSetDebugMessage("MQTT .....", 10);
    if (client.connect("arduino")) {
      Serial.println("connected");
      LCDSetDebugMessage("MQTT Connected.", 15);
      
      client.publish("command","hello world!");
      client.subscribe("presence");
      
    } else {
      Serial.print("failed, rc=");
      LCDSetDebugMessage("MQTT Failed.", 12);
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

// ######################### Main Code #########################
char message[30] = "this is another long message.";
void setup() {
  Serial.begin(9600); // For debugging
  
  LCDSetup();
  LCDSetMessage(message, 29);

  WiFiSetup();
  MQTTSetup();
}

unsigned long oneSecond = millis(), mSecond = millis();
void loop() {
  if (millis() - oneSecond > 1000) {
    oneSecond = millis();

    // Check MQTT connection.
    if (!client.connected())
      reconnect();

    // LCD operations.
    LCDSetTemperature(getTemperature());
    LCDSetLight(getLDR());
    LCDShow();

    // Publish Sensors information under "data" topic.
    char message[20];
    sprintf(message, "T: %d, L: %d", LCDTemperature, LCDLight);
    client.publish("data", message);
    client.loop();
  }

  if (millis() - mSecond > 33)
    client.loop();
}
