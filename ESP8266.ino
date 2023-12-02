#include <ESP8266WiFi.h>
#include <PubSubClient.h>

WiFiClient espClient;
PubSubClient client(espClient);
char* ssid = "xd1";
char* password = "98765432";
const char* mqtt_server = "192.168.137.182";
const int State1=16;
const int State2=5;
bool state=0;
bool stateLast;

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP8266Client")) {
      Serial.println("connected");
      client.subscribe("esp32/lights1");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}
void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}
void callback(char* topic, byte* message, unsigned int length) {
  String messageTemp;
  for (int i = 0; i < length; i++) {
    messageTemp += (char)message[i];
  }
  if (String(topic) == "esp32/lights1") {
    if(messageTemp == "true"){
      state=0;
    }
    else if(messageTemp == "false"){
      state=1;
    }
  }
}
void State1On(){
  digitalWrite(State1,HIGH);
  digitalWrite(State2,LOW);
  stateLast=0;
}
void State2On(){
  digitalWrite(State1,LOW);
  digitalWrite(State2,HIGH);
  stateLast=1;
}
void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  pinMode(State1,OUTPUT);
  pinMode(State2,OUTPUT);
  State1On();
}
void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  if (state!=stateLast){
    if (state==0){
      State1On();
    }
    else if (state==1){
      State2On();
    }
  }
}
