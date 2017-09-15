#include <LiquidCrystal.h>

// ######################### LCD #########################
// Connection between LCD and Arduino Pro Micro
//         LCD       ||| VSS | VDD | V0  | RS | RW  | E  | DB0 | DB1 | DB2 | DB3 | DB4 | DB5 | DB6 | DB7 | LEDA | LEDK
//===================|||=====|=====|=====|====|=====|====|=====|=====|=====|=====|=====|=====|=====|=====|======|=======
// Arduino Pro Micro ||| GND | VCC | GND | A1 | GND | A0 | --- | --- | --- | --- | 15  | 14  | 16  | 10  | VCC  | GND 
LiquidCrystal lcd(A1, A0, 15, 14, 16, 10);
int LCDTemperature, LCDLight, MessageLength, pos = 0;
char *LCDMessage;

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
  lcd.setCursor(0, 2);
  for (int i = pos; i < 16 + pos && i < MessageLength; i+=1) {
    lcd.print(LCDMessage[i]);
  }
  pos += 1;
  if (pos == MessageLength)
    pos = 0;

  // debuging
}

void LCDSetMessage(char *message, int mesLength) {
  LCDMessage = message;
  pos = 0;
  MessageLength = mesLength;
}

void LCDSetLight(int light) {
  LCDLight = light;
}

void LCDSetTemperature(int temperature) {
  LCDTemperature = temperature;
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

// ######################### Main Code #########################
char message[30] = "this is another long message.";
void setup() {
  LCDSetup();
  LCDSetMessage(message, 29);
}

unsigned long oneSecond = millis();
void loop() {
  if (millis() - oneSecond > 1000) {
    oneSecond = millis();

    // LCD operations
    LCDSetTemperature(getTemperature());
    LCDSetLight(getLDR());
    LCDShow();
  }
}

