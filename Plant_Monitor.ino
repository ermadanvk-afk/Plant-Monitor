#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>
#include <LiquidCrystal.h>
#include "DHTesp.h"

// --- YOUR PHONE HOTSPOT OR HOME WIFI ---
const char* ssid = "MADAN_PC";
const char* password = "madan123";

// --- YOUR HUGGING FACE URL ---
// Paste your URL and MAKE SURE to keep /update_sensors at the end!
// Example: "https://prince12313-plant-dashboard.hf.space/update_sensors"
String serverBase = "https://prince12313-plant-dashboard.hf.space/update_sensors"; 
// ---------------------------------------

DHTesp dht;
#define DHTPIN 4
#define SOIL_PIN 34

LiquidCrystal lcd(19, 23, 18, 17, 16, 15);

unsigned long lastTime = 0;
unsigned long timerDelay = 5000; // Send to cloud every 5 seconds

void setup() {
  Serial.begin(115200);
  dht.setup(DHTPIN, DHTesp::DHT11);
  lcd.begin(16, 2);
  
  lcd.setCursor(0, 0);
  lcd.print("WiFi Connecting.");
  WiFi.begin(ssid, password);
  
  while(WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
  lcd.clear();
}

void loop() {
  float h = dht.getHumidity();
  float t = dht.getTemperature();
  int soilRaw = analogRead(SOIL_PIN);
  int soilMoisture = map(soilRaw, 4095, 1500, 0, 100);
  if (soilMoisture > 100) soilMoisture = 100;
  if (soilMoisture < 0) soilMoisture = 0;

  if ((millis() - lastTime) > timerDelay) {
    if(WiFi.status() == WL_CONNECTED){
      
      // Bypass SSL verification for the Hugging Face server
      WiFiClientSecure *client = new WiFiClientSecure;
      client->setInsecure(); 
      
      HTTPClient http;
      String url = serverBase + "?t=" + String((int)t) + "&h=" + String((int)h) + "&m=" + String(soilMoisture);
      
      http.begin(*client, url);
      int httpResponseCode = http.GET();
      http.end();
      delete client;
    }
    lastTime = millis();
  }

  // Display on hardware LCD
  lcd.setCursor(0, 0);
  lcd.print("H:"); lcd.print((int)h); lcd.print(" ");
  lcd.print("M:"); lcd.print(soilMoisture); lcd.print(" ");
  lcd.print("T:"); lcd.print((int)t); lcd.print("  ");

  lcd.setCursor(0, 1);
  lcd.print("Cloud Synced... ");

  delay(2000); 
}