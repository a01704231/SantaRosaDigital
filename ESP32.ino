const int mic1Pin = 4;
const int mic2Pin = 2;
const int mic3Pin = 15;
int mic1Value = 0;
int mic2Value = 0;
int mic3Value = 0;
int t=0;

void setup() {
  pinMode(mic1Pin,INPUT);
  pinMode(mic2Pin,INPUT);
  pinMode(mic3Pin,INPUT);
  Serial.begin(115200);
  Serial.println("Starting");
  delay(1000);
}

void loop() {
  mic1Value = analogRead(mic1Pin);
  mic2Value = analogRead(mic2Pin);
  mic3Value = analogRead(mic3Pin);
  Serial.print(mic1Value);
  Serial.print(" ");
  Serial.print(mic2Value);
  Serial.print(" ");
  Serial.print(mic3Value);
  Serial.println("");
  delayMicroseconds(400);
}
