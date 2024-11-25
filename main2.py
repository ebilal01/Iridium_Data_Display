from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import random
import threading
import time
from collections import deque
import datetime
import json
import os

app = Flask(__name__, static_folder='static')
CORS(app)

# Store telemetry data
data_history = deque(maxlen=1000)

# Current satellite state
current_position = {
    "latitude": 36.4477,
    "longitude": -119.4179,
    "altitude": 1000,
    "temperature": -10
}

def load_initial_data():
    try:
        filepath = os.path.join('static', 'telemetry_data.json')
        with open(filepath, 'r') as file:
            data = json.load(file)
            data_history.extend(data)
            print(f"Loaded {len(data)} data points from telemetry_data.json")
    except FileNotFoundError:
        print("telemetry_data.json not found. Starting with an empty history.")
    except json.JSONDecodeError as e:
        print(f"Error decoding telemetry_data.json: {e}")

def generate_realistic_data():
    global current_position
    current_position["latitude"] += random.uniform(-0.02, 0.02)
    current_position["longitude"] += random.uniform(-0.03, 0.03)
    current_position["altitude"] += random.uniform(-20, 50)
    current_position["altitude"] = max(0, min(current_position["altitude"], 35000))
    current_position["temperature"] += random.uniform(-0.5, 0.5)

    data_point = {
        "time": datetime.datetime.utcnow().isoformat(),
        "latitude": current_position["latitude"],
        "longitude": current_position["longitude"],
        "altitude": current_position["altitude"],
        "temperature": current_position["temperature"]
    }
    data_history.append(data_point)

@app.route('/')
def index():
    return app.send_static_file('index2.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/live-data')
def live_data():
    if not data_history:
        return jsonify({"message": "No data available"}), 200
    return jsonify(data_history[-1])

@app.route('/history')
def history():
    return jsonify(list(data_history))

def continuous_data_simulation():
    while True:
        generate_realistic_data()
        time.sleep(5)

if __name__ == "__main__":
    load_initial_data()
    threading.Thread(target=continuous_data_simulation, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)


