/*
 * Description: This code controls Arduino used in Greenhouse, managing a stepper motor for a lid, 
 *              an LED for light, and a soil moisture sensor. The system responds to serial 
 *              commands to open/close the lid, turn the light on/off, and report soil moisture levels.
 * Author: Ondrej Galeta
 * Date: 17.7.2024
 */

#include <Stepper.h>

// Define the number of steps per revolution for your stepper motor
#define STEPS_PER_REV 2048
#define ledPin 6
#define soilMoisturePin A0
#define lidPower 4
#define lightPin 5
#define lidgate 3

// Create a stepper motor object
Stepper stepper(STEPS_PER_REV, 8, 10, 9, 11); // Pins for ULN2003 driver

// Variables to keep track of state
bool waterPumpState = false;
bool lightState = false;
bool lidState = false;


void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  
  // Initialize pins
  pinMode(lidPower, OUTPUT);
  pinMode(soilMoisturePin, INPUT);
  pinMode(lightPin, OUTPUT);
  
  // Set initial states
  digitalWrite(lidPower, HIGH);
  digitalWrite(lightPin, LOW);
  
  // Set the speed for the stepper motor
  stepper.setSpeed(10); // Speed in RPM
}

void loop() {
  // Check for serial commands
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    handleCommand(command);
  }
}


void handleCommand(String command) {
  // Parse the command and execute actions
  if (command == "LID_OPEN") {
    if(digitalRead(lidgate)) {
      digitalWrite(lidPower, LOW);
      stepper.step(STEPS_PER_REV / 5); // rotate counterclockwise
      Serial.println("Lid is: OPEN");
      lidState = true;
      digitalWrite(lidPower, HIGH);
    }
  } else if (command == "LID_CLOSE") {
    if(!digitalRead(lidgate)) {
      digitalWrite(lidPower, LOW);
      stepper.step(-STEPS_PER_REV / 5); // rotate clockwise
      Serial.println("Lid is: CLOSED");
      lidState = false;
      digitalWrite(lidPower, HIGH);
    }
  } else if (command == "LIGHT_ON") {
    lightState = true;
    digitalWrite(lightPin, HIGH);
    Serial.println("Light: ON");
  } else if (command == "LIGHT_OFF") {
    lightState = false;
    digitalWrite(lightPin, LOW);
    Serial.println("Light: OFF");
  } else if (command == "GET_HUMIDITY") {
    Serial.print("Soil_moisture_level:");
    Serial.println(readHum());
  } else {
    Serial.print("Unknown command {");
    Serial.print(command);
    Serial.println("}");
  }
}

int readHum() {
  // read humidity, return value from range 0 to 100
  int sensorValue = analogRead(soilMoisturePin); 
  int outputValue = map(sensorValue, 0, 1023, 168, 0);
  if (outputValue > 100) {outputValue=100;}
  return outputValue;             
}
