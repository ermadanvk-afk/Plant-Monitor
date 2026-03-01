import os
os.environ["TF_USE_LEGACY_KERAS"] = "1"

from flask import Flask, request, render_template_string
import tensorflow as tf
import numpy as np
from PIL import Image
import io

app = Flask(__name__)

# Global variables to store the latest data
ml_result = "Waiting for image..."
sensor_data = {"temp": "--", "humidity": "--", "moisture": "--"}

# Load the Model
model = tf.keras.models.load_model('keras_model.h5', compile=False)
with open('labels.txt', 'r') as f:
    class_names = [line.strip() for line in f.readlines()]

def analyze_image(image_bytes):
    img = Image.open(io.BytesIO(image_bytes)).convert('RGB').resize((224, 224))
    img_array = np.expand_dims((np.asarray(img) / 127.5) - 1.0, axis=0)
    prediction = model.predict(img_array)
    class_name = class_names[np.argmax(prediction)]
    return class_name.split(' ', 1)[1] if ' ' in class_name else class_name

# 1. The Main Dashboard Page
@app.route('/', methods=['GET', 'POST'])
def dashboard():
    global ml_result
    if request.method == 'POST' and 'file' in request.files:
        file = request.files['file']
        if file:
            ml_result = analyze_image(file.read())
            
    # The HTML code for your new web dashboard
    html = '''
    <!doctype html>
    <html>
    <head>
      <title>Plant Health Dashboard</title>
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f9; padding: 20px; color: #333; }
        .card { background: white; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        h2 { color: #2c3e50; }
        .data-text { font-size: 1.2em; margin: 10px 0; }
        input[type="submit"] { background-color: #27ae60; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-size: 1em; }
      </style>
    </head>
    <body>
      <h2>🌱 Plant Health Dashboard</h2>
      
      <div class="card">
        <h3>Live Sensor Data</h3>
        <div class="data-text">🌡️ Temperature: <strong>{{ s['temp'] }} &deg;C</strong></div>
        <div class="data-text">💧 Humidity: <strong>{{ s['humidity'] }} %</strong></div>
        <div class="data-text">🪴 Soil Moisture: <strong>{{ s['moisture'] }} %</strong></div>
      </div>

      <div class="card">
        <h3>Disease Analysis</h3>
        <div class="data-text">🩺 Status: <strong>{{ result }}</strong></div>
        <br>
        <form method="post" enctype="multipart/form-data">
          <input type="file" name="file" accept="image/*" capture="camera"><br><br>
          <input type="submit" value="Upload & Analyze">
        </form>
      </div>
    </body>
    </html>
    '''
    return render_template_string(html, s=sensor_data, result=ml_result)

# 2. The Endpoint for the ESP32 to push data to
@app.route('/update_sensors', methods=['GET'])
def update_sensors():
    # The ESP32 will send data in the URL, like: /update_sensors?t=32&h=80&m=70
    sensor_data['temp'] = request.args.get('t', "--")
    sensor_data['humidity'] = request.args.get('h', "--")
    sensor_data['moisture'] = request.args.get('m', "--")
    return "Data Received"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)