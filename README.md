# 🌱 IoT Plant Health Monitor & AI Disease Classifier

An end-to-end hardware and software project that monitors real-time plant environment data and uses Machine Learning to classify leaf diseases via a cloud-hosted web dashboard.

## 🛠️ Project Overview
This system uses an ESP32 microcontroller to read physical sensor data (temperature, humidity, and soil moisture). Instead of relying on local networks, the ESP32 pushes this data to a custom Python Flask web server hosted on the internet (Hugging Face Spaces). 

Users can access the web dashboard from their phone, see the live sensor readings, and upload a photo of a plant leaf. The cloud server runs the image through a TensorFlow/Keras neural network, predicts the disease status, and instantly sends that status back down to the physical LCD screen attached to the ESP32.

## 🧰 Hardware & Components
* **Microcontroller:** ESP32 Dev Module
* **Sensors:** DHT11 (Temperature & Humidity), Capacitive Soil Moisture Sensor v1.2
* **Display:** 16x2 LCD Display 
* **Wiring Setup:** The LCD is wired in "4-bit mode." Instead of using the standard 10 pins to communicate with the screen, we only used 6 pins (4 data pins + 2 control pins). The ESP32 sends the characters in two halves over those 4 data lines, which saved enough GPIO pins to plug in our sensors.

## 💻 Software Stack
* **Hardware Code:** C++ (Arduino IDE) using `HTTPClient.h` and `WiFiClientSecure.h`
* **Backend Web Server:** Python 3.11, Flask, Gunicorn
* **Machine Learning Framework:** TensorFlow 2.15 & Keras
* **Cloud Hosting:** Docker container on Hugging Face Spaces (16GB RAM)

## 🏗️ How It Was Built (Step-by-Step)

1. **The Hardware Setup:** We wired the DHT11, Soil Moisture sensor, and 16x2 LCD to the ESP32. We wrote C++ code to read the analog/digital voltages, convert them to human-readable numbers, and print them on the screen.
2. **The Local Web Page:** We wrote a Python Flask script (`app.py`) to create a basic webpage for image uploading, initially testing it locally using a mobile hotspot and USB tethering to bypass campus Wi-Fi isolation.
3. **The Machine Learning Model:** Using Google Teachable Machine, we utilized Transfer Learning on a MobileNet architecture. We trained the model to recognize 4 categories: Healthy, Infected, Moderate, and Background (to prevent false positives on empty walls).
4. **Cloud Migration:** To make the system independent of a local laptop, we containerized the Python app using Docker and deployed it to Hugging Face Spaces.
5. **Two-Way Synchronization:** The ESP32 code was updated to make HTTP `GET` requests to the cloud. It pushes the sensor data up to the dashboard and simultaneously pulls the latest AI prediction down to display on the physical LCD.

## 🐛 Problems Faced & Engineering Solutions

* **The Network Isolation Problem:** Campus Wi-Fi blocked devices from talking to each other. 
  * *Solution:* We moved the entire backend to a public cloud server, allowing the ESP32 to communicate via standard HTTPS over any network.
* **The Keras Framework Version Clash:** The Teachable Machine exported an older Keras 2 model, but the modern cloud server downloaded Keras 3, causing a `DepthwiseConv2D` crash. 
  * *Solution:* We injected the environment variable `TF_USE_LEGACY_KERAS="1"` and installed the `tf_keras` package to force backward compatibility on the server.
* **Cloud Server Memory Timeouts:** Free tiers on standard cloud hosts (512MB RAM) crashed while trying to install the massive TensorFlow framework. 
  * *Solution:* We migrated to Hugging Face Spaces, utilizing their free 16GB RAM Docker instances to successfully compile the ML environment.
* **Empty Wall False Positives:** The AI would randomly guess an empty wall was an "Infected Plant." 
  * *Solution:* We applied an "Open Set" fix by training a 4th `Background` class with pictures of desks and hands, teaching the AI to output a neutral status when no plant is present.
* **LCD Screen Overflow:** Triple-digit sensor readings caused the text to wrap around and corrupt the second row of the LCD. 
  * *Solution:* We abbreviated the C++ print statements and added trailing blank spaces (`"    "`) to manually clear leftover characters from previous hardware loops.

## 🚀 How to Run the Project
1. Flash the `ESP32_Code.ino` to your ESP32, ensuring you update the Wi-Fi credentials and the Hugging Face Cloud URL.
2. Upload the `app.py`, `keras_model.h5`, `labels.txt`, `requirements.txt`, and `Dockerfile` to a Hugging Face Space.
3. Power the ESP32 via a wall plug or power bank.
4. Open the generated Hugging Face https://prince12313-plant-dashboard.hf.space/ on any smartphone to access the live dashboard.
