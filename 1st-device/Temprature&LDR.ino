// ######################### Temprature Sensor #########################
float temprature, steps = 1024.0;
int volt = 4000/10, tempPin = 3;

float getTemprature() {
  temprature = (analogRead(tempPin) / steps) * volt;
  return temprature;
}

// ######################### LDR Sensor #########################

int ldrPin = 2, ldr;

int getLDR() {
  ldr = analogRead(ldrPin);
  return ldr;
}

// ######################### Main Code #########################

void setup() {
  Serial.begin(9600);  //start the serial monitor
}

void loop() {
  Serial.print("The temperature is :");  //Display the results on serial monitor
  Serial.print(getTemprature());
  Serial.print("'C and light: ");
  Serial.println(getLDR());
  Serial.println();
  delay(1000);                           //1 second delay to avoid overloop
}
