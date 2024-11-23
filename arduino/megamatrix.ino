void setup() {
  Serial.begin(9600);  // Ensure baud rate matches Python code
  //analogReference(INTERNAL2V56);  // Set analog reference to internal 1.1V

  // Optional: Ground unused analog pins to reduce noise
  pinMode(54, OUTPUT);  // Ground A0 (digital 54)
  digitalWrite(54, LOW);

  pinMode(56, OUTPUT);  // Ground A2 (digital 56)
  digitalWrite(56, LOW);

  pinMode(57, OUTPUT);  // Ground A3 (digital 57)
  digitalWrite(57, LOW);

  pinMode(58, OUTPUT);  // Ground A4 (digital 58)
  digitalWrite(58, LOW);

  pinMode(59, OUTPUT);  // Ground A5 (digital 59)
  digitalWrite(59, LOW);

  pinMode(60, OUTPUT);  // Ground A6 (digital 60)
  digitalWrite(60, LOW);

  pinMode(62, OUTPUT);  // Ground A8 (digital 62)
  digitalWrite(62, LOW);

  pinMode(63, OUTPUT);  // Ground A9 (digital 63)
  digitalWrite(63, LOW);

  pinMode(64, OUTPUT);  // Ground A10 (digital 64)
  digitalWrite(64, LOW);

  pinMode(65, OUTPUT);  // Ground A11 (digital 65)
  digitalWrite(65, LOW);

  pinMode(66, OUTPUT);  // Ground A12 (digital 66)
  digitalWrite(66, LOW);

  pinMode(67, OUTPUT);  // Ground A13 (digital 67)
  digitalWrite(67, LOW);

  pinMode(68, OUTPUT);  // Ground A14 (digital 68)
  digitalWrite(68, LOW);
}

void loop() {
  // Read A1, A7, and A15 twice, discarding the first reading for each to stabilize
  delay(10);
  int sensorValue1 = analogRead(A1);  // Discard first read
  delay(10);  // Small delay for ADC stabilization
  sensorValue1 = analogRead(A1);  // Use second read
  

  int sensorValue2 = analogRead(A7);  // Discard first read
  delay(10);  // Small delay for ADC stabilization
  sensorValue2 = analogRead(A7);  // Use second read
 
  
  int sensorValue3 = analogRead(A15);  // Discard first read
  delay(10);  // Small delay for ADC stabilization
  sensorValue3 = analogRead(A15);  // Use second read
  
  // Send the stabilized values to the serial port
  Serial.print("(");
  Serial.print(sensorValue1);
  Serial.print(",");
  Serial.print(sensorValue2);
  Serial.print(",");
  Serial.println(sensorValue3);
  Serial.print(")");
  Serial.println(",");
 
  delay(16);  // Adjust delay as needed
}
