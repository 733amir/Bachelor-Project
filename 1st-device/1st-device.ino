#include <LiquidCrystal.h>

// Connection between LCD and Arduino Pro Micro
//         LCD       ||| VSS | VDD | V0  | RS | RW  | E  | DB0 | DB1 | DB2 | DB3 | DB4 | DB5 | DB6 | DB7 | LEDA | LEDK
//===================|||=====|=====|=====|====|=====|====|=====|=====|=====|=====|=====|=====|=====|=====|======|=======
// Arduino Pro Micro ||| GND | +5  | GND | A1 | GND | A0 | --- | --- | --- | --- | 16  | 10  | 15  | 14  | ---- | ---- 
LiquidCrystal lcd(A1, A0, 16, 10, 15, 14);

void setup() {
  lcd.begin(16, 4);
  lcd.print("Hello World!");
}

void loop() {
}

